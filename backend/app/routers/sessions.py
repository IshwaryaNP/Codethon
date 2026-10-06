from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime, date, timezone
from bson import ObjectId
from app.db import get_db
from app.auth.dependencies import get_current_user
from app.models.session import SessionResponse, SessionUpdateStatus
from app.services.velocity import get_all_subject_velocities
from app.services.scheduler import run_scheduler

router = APIRouter(prefix="/sessions", tags=["Sessions"])

@router.get("", response_model=List[SessionResponse])
async def list_sessions(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    db = get_db()
    user_id = current_user["id"]
    query = {"user_id": user_id}
    if start_date or end_date:
        date_q = {}
        if start_date:
            date_q["$gte"] = start_date
        if end_date:
            date_q["$lte"] = end_date
        query["planned_date"] = date_q

    cursor = db.sessions.find(query).sort("planned_date", 1)
    sessions = []

    # Map topics and subjects for names/colors
    topics_cursor = db.topics.find({"user_id": user_id})
    topic_map = {str(t["_id"]): t.get("name", "") async for t in topics_cursor}

    subjects_cursor = db.subjects.find({"user_id": user_id})
    subj_map = {str(s["_id"]): s async for s in subjects_cursor}

    async for sess in cursor:
        sess["id"] = str(sess["_id"])
        t_id = sess.get("topic_id", "")
        s_id = sess.get("subject_id", "")

        sess["topic_name"] = topic_map.get(t_id, "Study Session")
        subj = subj_map.get(s_id, {})
        sess["subject_name"] = subj.get("name", "General")
        sess["subject_color"] = subj.get("color", "#3b82f6")

        sessions.append(SessionResponse(**sess))

    return sessions


async def _trigger_automatic_replan(user_id: str):
    """
    Helper function to automatically trigger replanning from today forward.
    Preserves historical done/missed sessions, updates future planned sessions.
    """
    db = get_db()
    today_str = date.today().isoformat()

    # 1. Fetch topics, events, availability, completed sessions
    topics_cursor = db.topics.find({"user_id": user_id})
    topics = [t async for t in topics_cursor]

    events_cursor = db.events.find({"user_id": user_id})
    events = [e async for e in events_cursor]

    avail_doc = await db.availability.find_one({"user_id": user_id})
    availability = avail_doc if avail_doc else {}

    sessions_cursor = db.sessions.find({"user_id": user_id})
    all_sessions = [s async for s in sessions_cursor]

    # Calculate subject velocities
    vel_map = get_all_subject_velocities(all_sessions)

    # 2. Run deterministic scheduler
    new_sessions, feasibility_report = run_scheduler(
        topics=topics,
        events=events,
        availability=availability,
        velocity_map=vel_map,
        today=date.today()
    )

    # 3. Delete future PLANNED sessions starting today, leave done/missed intact
    await db.sessions.delete_many({
        "user_id": user_id,
        "status": "planned",
        "planned_date": {"$gte": today_str}
    })

    # 4. Insert newly calculated planned sessions
    now = datetime.now(timezone.utc)
    to_insert = []
    for s in new_sessions:
        s["user_id"] = user_id
        s["created_at"] = now
        s["updated_at"] = now
        to_insert.append(s)

    if to_insert:
        await db.sessions.insert_many(to_insert)

    return feasibility_report


@router.put("/{session_id}/status", response_model=SessionResponse)
async def update_session_status(
    session_id: str,
    status_in: SessionUpdateStatus,
    current_user: dict = Depends(get_current_user)
):
    db = get_db()
    user_id = current_user["id"]
    
    try:
        sess = await db.sessions.find_one({"_id": ObjectId(session_id), "user_id": user_id})
    except Exception:
        sess = None

    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")

    now = datetime.now(timezone.utc)
    actual_mins = status_in.actual_minutes if status_in.actual_minutes is not None else sess.get("planned_minutes", 60)

    updated_sess = await db.sessions.find_one_and_update(
        {"_id": ObjectId(session_id), "user_id": user_id},
        {"$set": {
            "status": status_in.status,
            "actual_minutes": actual_mins if status_in.status == "done" else 0,
            "updated_at": now
        }},
        return_document=True
    )

    # Auto Replanning trigger!
    await _trigger_automatic_replan(user_id)

    # Populate labels for response
    t_id = updated_sess.get("topic_id", "")
    s_id = updated_sess.get("subject_id", "")
    topic_doc = await db.topics.find_one({"_id": ObjectId(t_id)}) if ObjectId.is_valid(t_id) else None
    subj_doc = await db.subjects.find_one({"_id": ObjectId(s_id)}) if ObjectId.is_valid(s_id) else None

    updated_sess["id"] = str(updated_sess["_id"])
    updated_sess["topic_name"] = topic_doc.get("name", "Study Session") if topic_doc else "Study Session"
    updated_sess["subject_name"] = subj_doc.get("name", "General") if subj_doc else "General"
    updated_sess["subject_color"] = subj_doc.get("color", "#3b82f6") if subj_doc else "#3b82f6"

    return SessionResponse(**updated_sess)
