from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime, timezone
from bson import ObjectId
from app.db import get_db
from app.auth.dependencies import get_current_user
from app.models.event import EventCreate, EventUpdate, EventResponse

router = APIRouter(prefix="/events", tags=["Events"])

@router.post("", response_model=EventResponse)
async def create_event(
    event_in: EventCreate,
    current_user: dict = Depends(get_current_user)
):
    db = get_db()
    user_id = current_user["id"]
    
    # Verify subject ownership
    try:
        sub = await db.subjects.find_one({"_id": ObjectId(event_in.subject_id), "user_id": user_id})
    except Exception:
        sub = None

    if not sub:
        raise HTTPException(status_code=400, detail="Invalid subject_id or access denied")

    now = datetime.now(timezone.utc)
    doc = {
        "user_id": user_id,
        "title": event_in.title,
        "type": event_in.type,
        "subject_id": event_in.subject_id,
        "due_date": event_in.due_date,
        "description": event_in.description or "",
        "created_at": now,
        "updated_at": now
    }
    
    result = await db.events.insert_one(doc)
    doc["id"] = str(result.inserted_id)

    # Replan so exam deadlines immediately re-prioritize and allocate sessions
    try:
        from app.routers.sessions import _trigger_automatic_replan
        await _trigger_automatic_replan(user_id)
    except Exception as e:
        print("Replan error after event creation:", e)

    return EventResponse(**doc)

@router.get("", response_model=List[EventResponse])
async def list_events(
    subject_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    db = get_db()
    user_id = current_user["id"]
    query = {"user_id": user_id}
    if subject_id:
        query["subject_id"] = subject_id

    cursor = db.events.find(query).sort("due_date", 1)
    events = []
    async for e in cursor:
        e["id"] = str(e["_id"])
        events.append(EventResponse(**e))
    return events

@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: str,
    current_user: dict = Depends(get_current_user)
):
    db = get_db()
    user_id = current_user["id"]
    try:
        e = await db.events.find_one({"_id": ObjectId(event_id), "user_id": user_id})
    except Exception:
        e = None
    
    if not e:
        raise HTTPException(status_code=404, detail="Event not found")
    
    e["id"] = str(e["_id"])
    return EventResponse(**e)

@router.put("/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: str,
    event_in: EventUpdate,
    current_user: dict = Depends(get_current_user)
):
    db = get_db()
    user_id = current_user["id"]
    update_data = {k: v for k, v in event_in.model_dump().items() if v is not None}
    if not update_data:
        return await get_event(event_id, current_user)
    
    update_data["updated_at"] = datetime.now(timezone.utc)
    try:
        res = await db.events.find_one_and_update(
            {"_id": ObjectId(event_id), "user_id": user_id},
            {"$set": update_data},
            return_document=True
        )
    except Exception:
        res = None

    if not res:
        raise HTTPException(status_code=404, detail="Event not found")

    res["id"] = str(res["_id"])
    return EventResponse(**res)

@router.delete("/{event_id}")
async def delete_event(
    event_id: str,
    current_user: dict = Depends(get_current_user)
):
    db = get_db()
    user_id = current_user["id"]
    try:
        res = await db.events.delete_one({"_id": ObjectId(event_id), "user_id": user_id})
    except Exception:
        res = None

    if not res or res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Event not found")

    return {"message": "Event deleted successfully"}
