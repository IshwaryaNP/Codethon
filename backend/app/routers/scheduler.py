from fastapi import APIRouter, Depends, HTTPException
from datetime import date, datetime, timezone
from app.db import get_db
from app.auth.dependencies import get_current_user
from app.services.velocity import get_all_subject_velocities
from app.services.scheduler import run_scheduler
from app.services.triage import run_triage_analysis
from app.routers.sessions import _trigger_automatic_replan

router = APIRouter(prefix="/scheduler", tags=["Scheduler"])

@router.post("/replan")
async def trigger_replan(current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    feasibility_report = await _trigger_automatic_replan(user_id)
    return {
        "message": "Schedule successfully generated and reconciled",
        "feasibility": feasibility_report
    }

@router.get("/feasibility")
async def get_feasibility_report(current_user: dict = Depends(get_current_user)):
    db = get_db()
    user_id = current_user["id"]

    topics_cursor = db.topics.find({"user_id": user_id})
    topics = [t async for t in topics_cursor]

    events_cursor = db.events.find({"user_id": user_id})
    events = [e async for e in events_cursor]

    avail_doc = await db.availability.find_one({"user_id": user_id})
    availability = avail_doc if avail_doc else {}

    sessions_cursor = db.sessions.find({"user_id": user_id})
    all_sessions = [s async for s in sessions_cursor]

    vel_map = get_all_subject_velocities(all_sessions)

    _, report = run_scheduler(
        topics=topics,
        events=events,
        availability=availability,
        velocity_map=vel_map,
        today=date.today()
    )

    # Attach triage recommendations for infeasible exams
    triage_results = []
    for exam in report.get("exams", []):
        if not exam["feasible"] and exam["deficit_hours"] > 0:
            sub_id = exam["subject_id"]
            sub_topics = [t for t in topics if t.get("subject_id") == sub_id]
            triage_res = run_triage_analysis(
                topics=sub_topics,
                deficit_hours=exam["deficit_hours"],
                subject_name=exam["exam_title"]
            )
            triage_results.append(triage_res)

    report["triage_recommendations"] = triage_results
    return report
