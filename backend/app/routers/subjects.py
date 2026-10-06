from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime, timezone
from bson import ObjectId
from app.db import get_db
from app.auth.dependencies import get_current_user
from app.models.subject import SubjectCreate, SubjectUpdate, SubjectResponse

from app.routers.sessions import _trigger_automatic_replan

router = APIRouter(prefix="/subjects", tags=["Subjects"])

@router.post("", response_model=SubjectResponse)
async def create_subject(
    subject_in: SubjectCreate,
    current_user: dict = Depends(get_current_user)
):
    db = get_db()
    user_id = current_user["id"]
    now = datetime.now(timezone.utc)
    
    doc = {
        "user_id": user_id,
        "name": subject_in.name,
        "description": subject_in.description or "",
        "color": subject_in.color or "#3b82f6",
        "created_at": now,
        "updated_at": now
    }
    
    result = await db.subjects.insert_one(doc)
    subject_id = str(result.inserted_id)
    doc["id"] = subject_id

    # If exam_date is provided, create exam event
    if subject_in.exam_date:
        try:
            exam_doc = {
                "user_id": user_id,
                "title": f"{subject_in.name} Exam",
                "type": "exam",
                "subject_id": subject_id,
                "due_date": subject_in.exam_date,
                "description": f"Target exam for {subject_in.name}",
                "created_at": now,
                "updated_at": now
            }
            await db.events.insert_one(exam_doc)
        except Exception:
            pass

    # Create initial topic (user-specified or standard Chapter 1 so it immediately schedules onto timetable)
    topic_title = subject_in.initial_topic.strip() if (subject_in.initial_topic and subject_in.initial_topic.strip()) else f"{subject_in.name} Fundamentals"
    topic_doc = {
        "user_id": user_id,
        "subject_id": subject_id,
        "name": topic_title,
        "est_hours": float(subject_in.initial_est_hours or 2.0),
        "difficulty": 3,
        "weight": 4,
        "mastery": 0.0,
        "status": "pending",
        "created_at": now,
        "updated_at": now
    }
    await db.topics.insert_one(topic_doc)

    # Automatically run scheduler & replan so sessions instantly appear on the timetable
    try:
        await _trigger_automatic_replan(user_id)
    except Exception as e:
        print("Replan error after subject creation:", e)

    return SubjectResponse(**doc)

@router.get("", response_model=List[SubjectResponse])
async def list_subjects(current_user: dict = Depends(get_current_user)):
    db = get_db()
    user_id = current_user["id"]
    cursor = db.subjects.find({"user_id": user_id}).sort("created_at", -1)
    subjects = []
    async for s in cursor:
        s["id"] = str(s["_id"])
        subjects.append(SubjectResponse(**s))
    return subjects

@router.get("/{subject_id}", response_model=SubjectResponse)
async def get_subject(
    subject_id: str,
    current_user: dict = Depends(get_current_user)
):
    db = get_db()
    user_id = current_user["id"]
    try:
        s = await db.subjects.find_one({"_id": ObjectId(subject_id), "user_id": user_id})
    except Exception:
        s = None
    
    if not s:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    s["id"] = str(s["_id"])
    return SubjectResponse(**s)

@router.put("/{subject_id}", response_model=SubjectResponse)
async def update_subject(
    subject_id: str,
    subject_in: SubjectUpdate,
    current_user: dict = Depends(get_current_user)
):
    db = get_db()
    user_id = current_user["id"]
    update_data = {k: v for k, v in subject_in.model_dump().items() if v is not None}
    if not update_data:
        return await get_subject(subject_id, current_user)
    
    update_data["updated_at"] = datetime.now(timezone.utc)
    try:
        res = await db.subjects.find_one_and_update(
            {"_id": ObjectId(subject_id), "user_id": user_id},
            {"$set": update_data},
            return_document=True
        )
    except Exception:
        res = None

    if not res:
        raise HTTPException(status_code=404, detail="Subject not found")

    res["id"] = str(res["_id"])
    return SubjectResponse(**res)

@router.delete("/{subject_id}")
async def delete_subject(
    subject_id: str,
    current_user: dict = Depends(get_current_user)
):
    db = get_db()
    user_id = current_user["id"]
    try:
        res = await db.subjects.delete_one({"_id": ObjectId(subject_id), "user_id": user_id})
    except Exception:
        res = None

    if not res or res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    # Also clean up associated topics, events, sessions
    await db.topics.delete_many({"subject_id": subject_id, "user_id": user_id})
    await db.events.delete_many({"subject_id": subject_id, "user_id": user_id})
    await db.sessions.delete_many({"subject_id": subject_id, "user_id": user_id})

    return {"message": "Subject and related resources deleted successfully"}
