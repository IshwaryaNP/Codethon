from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone
from bson import ObjectId
from app.db import get_db
from app.auth.dependencies import get_current_user
from app.services.llm import parse_syllabus_with_llm
from app.models.topic import TopicResponse

router = APIRouter(prefix="/syllabus", tags=["Syllabus"])

class SyllabusParseRequest(BaseModel):
    subject_id: str
    syllabus_text: str = Field(..., min_length=10)

class SyllabusConfirmRequest(BaseModel):
    subject_id: str
    topics: List[dict]

@router.post("/parse")
async def parse_syllabus(
    req: SyllabusParseRequest,
    current_user: dict = Depends(get_current_user)
):
    db = get_db()
    user_id = current_user["id"]

    try:
        sub = await db.subjects.find_one({"_id": ObjectId(req.subject_id), "user_id": user_id})
    except Exception:
        sub = None

    if not sub:
        raise HTTPException(status_code=400, detail="Subject not found or access denied")

    success, parsed_topics, err_msg = await parse_syllabus_with_llm(req.syllabus_text)

    if not success:
        raise HTTPException(status_code=400, detail=err_msg or "Failed to parse syllabus with AI")

    return {
        "subject_id": req.subject_id,
        "subject_name": sub.get("name", ""),
        "extracted_topics": parsed_topics
    }

@router.post("/confirm", response_model=List[TopicResponse])
async def confirm_syllabus_topics(
    req: SyllabusConfirmRequest,
    current_user: dict = Depends(get_current_user)
):
    db = get_db()
    user_id = current_user["id"]

    try:
        sub = await db.subjects.find_one({"_id": ObjectId(req.subject_id), "user_id": user_id})
    except Exception:
        sub = None

    if not sub:
        raise HTTPException(status_code=400, detail="Subject not found")

    now = datetime.now(timezone.utc)
    inserted_topics = []

    for t in req.topics:
        doc = {
            "user_id": user_id,
            "subject_id": req.subject_id,
            "name": t.get("name", "Untitled Topic"),
            "est_hours": float(t.get("est_hours", 2.0)),
            "difficulty": max(1, min(5, int(t.get("difficulty", 3)))),
            "weight": max(1, min(5, int(t.get("weight", 3)))),
            "mastery": 0.0,
            "status": "pending",
            "created_at": now,
            "updated_at": now
        }
        res = await db.topics.insert_one(doc)
        doc["id"] = str(res.inserted_id)
        inserted_topics.append(TopicResponse(**doc))

    return inserted_topics
