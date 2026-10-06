from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime, timezone
from bson import ObjectId
from app.db import get_db
from app.auth.dependencies import get_current_user
from app.models.topic import TopicCreate, TopicUpdate, TopicResponse

router = APIRouter(prefix="/topics", tags=["Topics"])

@router.post("", response_model=TopicResponse)
async def create_topic(
    topic_in: TopicCreate,
    current_user: dict = Depends(get_current_user)
):
    db = get_db()
    user_id = current_user["id"]
    
    # Verify subject ownership
    try:
        sub = await db.subjects.find_one({"_id": ObjectId(topic_in.subject_id), "user_id": user_id})
    except Exception:
        sub = None

    if not sub:
        raise HTTPException(status_code=400, detail="Invalid subject_id or access denied")

    now = datetime.now(timezone.utc)
    doc = {
        "user_id": user_id,
        "subject_id": topic_in.subject_id,
        "name": topic_in.name,
        "est_hours": topic_in.est_hours,
        "difficulty": topic_in.difficulty,
        "weight": topic_in.weight,
        "mastery": topic_in.mastery,
        "status": topic_in.status,
        "created_at": now,
        "updated_at": now
    }
    
    result = await db.topics.insert_one(doc)
    doc["id"] = str(result.inserted_id)

    # Replan so the new topic is immediately allocated onto the timetable
    try:
        from app.routers.sessions import _trigger_automatic_replan
        await _trigger_automatic_replan(user_id)
    except Exception as e:
        print("Replan error after topic creation:", e)

    return TopicResponse(**doc)

@router.get("", response_model=List[TopicResponse])
async def list_topics(
    subject_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    db = get_db()
    user_id = current_user["id"]
    query = {"user_id": user_id}
    if subject_id:
        query["subject_id"] = subject_id

    cursor = db.topics.find(query).sort("created_at", -1)
    topics = []
    async for t in cursor:
        t["id"] = str(t["_id"])
        topics.append(TopicResponse(**t))
    return topics

@router.get("/{topic_id}", response_model=TopicResponse)
async def get_topic(
    topic_id: str,
    current_user: dict = Depends(get_current_user)
):
    db = get_db()
    user_id = current_user["id"]
    try:
        t = await db.topics.find_one({"_id": ObjectId(topic_id), "user_id": user_id})
    except Exception:
        t = None
    
    if not t:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    t["id"] = str(t["_id"])
    return TopicResponse(**t)

@router.put("/{topic_id}", response_model=TopicResponse)
async def update_topic(
    topic_id: str,
    topic_in: TopicUpdate,
    current_user: dict = Depends(get_current_user)
):
    db = get_db()
    user_id = current_user["id"]
    update_data = {k: v for k, v in topic_in.model_dump().items() if v is not None}
    if not update_data:
        return await get_topic(topic_id, current_user)
    
    update_data["updated_at"] = datetime.now(timezone.utc)
    try:
        res = await db.topics.find_one_and_update(
            {"_id": ObjectId(topic_id), "user_id": user_id},
            {"$set": update_data},
            return_document=True
        )
    except Exception:
        res = None

    if not res:
        raise HTTPException(status_code=404, detail="Topic not found")

    res["id"] = str(res["_id"])
    return TopicResponse(**res)

@router.delete("/{topic_id}")
async def delete_topic(
    topic_id: str,
    current_user: dict = Depends(get_current_user)
):
    db = get_db()
    user_id = current_user["id"]
    try:
        res = await db.topics.delete_one({"_id": ObjectId(topic_id), "user_id": user_id})
    except Exception:
        res = None

    if not res or res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    await db.sessions.delete_many({"topic_id": topic_id, "user_id": user_id})
    await db.questions.delete_many({"topic_id": topic_id})
    return {"message": "Topic deleted successfully"}
