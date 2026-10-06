from fastapi import APIRouter, Depends
from datetime import date, datetime, timedelta
from app.db import get_db
from app.auth.dependencies import get_current_user
from app.services.summary import generate_daily_summary_text, generate_weekly_summary_text
from app.services.readiness import calculate_exam_readiness

router = APIRouter(prefix="/summaries", tags=["Summaries"])

@router.get("/daily")
async def get_daily_summary(current_user: dict = Depends(get_current_user)):
    db = get_db()
    user_id = current_user["id"]
    today_str = date.today().isoformat()

    # Calculate deterministic metrics for today
    today_sessions = await db.sessions.find({
        "user_id": user_id,
        "planned_date": today_str
    }).to_list(None)

    planned_mins = sum(s.get("planned_minutes", 0) for s in today_sessions)
    completed_mins = sum(s.get("actual_minutes", 0) for s in today_sessions if s.get("status") == "done")
    missed_count = sum(1 for s in today_sessions if s.get("status") == "missed")

    completed_topics_today = await db.topics.count_documents({
        "user_id": user_id,
        "status": "completed",
        "updated_at": {"$gte": datetime.now().replace(hour=0, minute=0, second=0)}
    })

    # Fetch next upcoming exam
    next_exam = await db.events.find_one({
        "user_id": user_id,
        "type": "exam",
        "due_date": {"$gte": datetime.now()}
    }, sort=[("due_date", 1)])

    readiness_pct = "N/A"
    exam_title = "None"
    if next_exam:
        exam_title = next_exam.get("title", "Upcoming Exam")
        sub_id = next_exam.get("subject_id")
        sub_topics = await db.topics.find({"user_id": user_id, "subject_id": sub_id}).to_list(None)
        sub_sessions = await db.sessions.find({"user_id": user_id, "subject_id": sub_id}).to_list(None)
        avail = await db.availability.find_one({"user_id": user_id}) or {}
        
        due_d = next_exam.get("due_date")
        e_date = due_d.date() if isinstance(due_d, datetime) else date.today()

        rd = calculate_exam_readiness(
            exam_id=str(next_exam["_id"]),
            exam_title=exam_title,
            exam_date=e_date,
            topics=sub_topics,
            availability=avail,
            completed_sessions=sub_sessions,
            today=date.today()
        )
        readiness_pct = rd["readiness_probability"]

    stats = {
        "planned_minutes": planned_mins,
        "completed_minutes": completed_mins,
        "missed_count": missed_count,
        "topics_completed_today": completed_topics_today,
        "upcoming_exam_title": exam_title,
        "upcoming_exam_readiness": readiness_pct
    }

    summary_text = generate_daily_summary_text(stats)
    return {
        "date": today_str,
        "stats": stats,
        "summary": summary_text
    }


@router.get("/weekly")
async def get_weekly_summary(current_user: dict = Depends(get_current_user)):
    db = get_db()
    user_id = current_user["id"]
    today = date.today()
    start_of_week = (today - timedelta(days=7)).isoformat()

    week_sessions = await db.sessions.find({
        "user_id": user_id,
        "planned_date": {"$gte": start_of_week, "$lte": today.isoformat()}
    }).to_list(None)

    planned_mins = sum(s.get("planned_minutes", 0) for s in week_sessions)
    completed_mins = sum(s.get("actual_minutes", 0) for s in week_sessions if s.get("status") == "done")
    comp_rate = round((completed_mins / max(planned_mins, 1)) * 100.0, 1)

    subjects = await db.subjects.find({"user_id": user_id}).to_list(None)
    subj_progress_parts = []
    for sub in subjects:
        sub_id = str(sub["_id"])
        sub_completed = sum(1 for s in week_sessions if s.get("subject_id") == sub_id and s.get("status") == "done")
        if sub_completed > 0:
            subj_progress_parts.append(f"{sub['name']}: {sub_completed} sessions completed")

    subj_summary = "; ".join(subj_progress_parts) if subj_progress_parts else "Consistent progress across all subjects."

    stats = {
        "weekly_planned_minutes": planned_mins,
        "weekly_completed_minutes": completed_mins,
        "weekly_completion_rate": comp_rate,
        "subject_progress_summary": subj_summary
    }

    summary_text = generate_weekly_summary_text(stats)
    return {
        "week_starting": start_of_week,
        "stats": stats,
        "summary": summary_text
    }
