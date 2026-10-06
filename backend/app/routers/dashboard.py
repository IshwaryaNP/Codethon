from fastapi import APIRouter, Depends
from datetime import date, datetime, timedelta, timezone
from typing import Dict, Any, List
from app.db import get_db
from app.auth.dependencies import get_current_user
from app.services.velocity import get_all_subject_velocities, calculate_subject_velocity
from app.services.readiness import calculate_exam_readiness
from app.services.scheduler import run_scheduler, calculate_topic_priority
from app.services.triage import run_triage_analysis

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/summary")
async def get_dashboard_summary(current_user: dict = Depends(get_current_user)):
    db = get_db()
    user_id = current_user["id"]
    today_str = date.today().isoformat()

    # 1. Fetch all collections for user
    subjects = await db.subjects.find({"user_id": user_id}).to_list(None)
    topics = await db.topics.find({"user_id": user_id}).to_list(None)
    events = await db.events.find({"user_id": user_id}).to_list(None)
    availability = await db.availability.find_one({"user_id": user_id}) or {}
    sessions = await db.sessions.find({"user_id": user_id}).to_list(None)

    for s in subjects:
        s["id"] = str(s["_id"])
    for t in topics:
        t["id"] = str(t["_id"])
    for e in events:
        e["id"] = str(e["_id"])
    for s in sessions:
        s["id"] = str(s["_id"])

    # Map subject names/colors
    sub_map = {s["id"]: s for s in subjects}
    topic_map = {t["id"]: t for t in topics}

    # 2. Overall Topic & Hour Progress
    total_topics = len(topics)
    completed_topics = sum(1 for t in topics if t.get("status") == "completed")
    overall_progress_pct = round((completed_topics / total_topics * 100.0), 1) if total_topics > 0 else 0.0

    # Weekly study hours (last 7 days)
    seven_days_ago = (date.today() - timedelta(days=7)).isoformat()
    weekly_completed_mins = sum(
        s.get("actual_minutes", 0) for s in sessions
        if s.get("status") == "done" and s.get("planned_date") >= seven_days_ago
    )
    weekly_study_hours = round(weekly_completed_mins / 60.0, 1)

    # 3. Subject Cards
    subject_cards = []
    subject_velocities = get_all_subject_velocities(sessions)

    for sub in subjects:
        sub_id = sub["id"]
        sub_topics = [t for t in topics if t.get("subject_id") == sub_id]
        tot_sub = len(sub_topics)
        comp_sub = sum(1 for t in sub_topics if t.get("status") == "completed")
        pct_sub = round((comp_sub / tot_sub * 100.0), 1) if tot_sub > 0 else 0.0

        vel = subject_velocities.get(sub_id, 1.0)
        rem_hours = sum(
            float(t.get("est_hours", 1.0)) * (1.0 - float(t.get("mastery", 0.0))) * vel
            for t in sub_topics if t.get("status") != "completed"
        )

        subject_cards.append({
            "id": sub_id,
            "name": sub["name"],
            "color": sub.get("color", "#3b82f6"),
            "progress_pct": pct_sub,
            "total_topics": tot_sub,
            "completed_topics": comp_sub,
            "remaining_topics": tot_sub - comp_sub,
            "estimated_remaining_hours": round(rem_hours, 1),
            "velocity": vel
        })

    # 4. Exam Readiness Cards (Monte Carlo)
    exam_readiness_cards = []
    upcoming_exams = [e for e in events if e.get("type") == "exam"]

    for exam in upcoming_exams:
        sub_id = exam.get("subject_id", "")
        due_dt = exam.get("due_date")
        if isinstance(due_dt, datetime):
            e_date = due_dt.date()
        elif isinstance(due_dt, str):
            e_date = datetime.fromisoformat(due_dt.replace("Z", "+00:00")).date()
        elif isinstance(due_dt, date):
            e_date = due_dt
        else:
            continue

        if e_date >= date.today():
            sub_topics = [t for t in topics if t.get("subject_id") == sub_id]
            sub_sessions = [s for s in sessions if s.get("subject_id") == sub_id]
            
            readiness_res = calculate_exam_readiness(
                exam_id=exam["id"],
                exam_title=exam["title"],
                exam_date=e_date,
                topics=sub_topics,
                availability=availability,
                completed_sessions=sub_sessions,
                today=date.today(),
                simulations_count=1000
            )
            exam_readiness_cards.append(readiness_res)

    # 5. Today's Plan Sessions
    todays_sessions = []
    for sess in sessions:
        if sess.get("planned_date") == today_str:
            t_id = sess.get("topic_id", "")
            s_id = sess.get("subject_id", "")
            top = topic_map.get(t_id, {})
            sub = sub_map.get(s_id, {})

            todays_sessions.append({
                "id": sess["id"],
                "topic_id": t_id,
                "topic_name": top.get("name", "Study Session"),
                "subject_id": s_id,
                "subject_name": sub.get("name", "General"),
                "subject_color": sub.get("color", "#3b82f6"),
                "planned_minutes": sess.get("planned_minutes", 60),
                "actual_minutes": sess.get("actual_minutes", 0),
                "status": sess.get("status", "planned"),
                "type": sess.get("type", "study")
            })

    # 6. Upcoming Deadlines (Next 14 Days)
    fourteen_days_ahead = (date.today() + timedelta(days=14)).isoformat()
    upcoming_deadlines = []
    for evt in events:
        due_dt = evt.get("due_date")
        if isinstance(due_dt, datetime):
            d_str = due_dt.date().isoformat()
        elif isinstance(due_dt, str):
            d_str = due_dt[:10]
        else:
            continue

        if today_str <= d_str <= fourteen_days_ahead:
            s_id = evt.get("subject_id", "")
            sub = sub_map.get(s_id, {})
            upcoming_deadlines.append({
                "id": evt["id"],
                "title": evt["title"],
                "type": evt["type"],
                "subject_name": sub.get("name", "General"),
                "subject_color": sub.get("color", "#3b82f6"),
                "due_date": d_str
            })

    # 7. Priority Topics
    scored_pending_topics = []
    for top in topics:
        if top.get("status") != "completed":
            s_id = top.get("subject_id", "")
            # find earliest exam for subject
            exam_info = next((e for e in upcoming_exams if e.get("subject_id") == s_id), None)
            exam_date = None
            if exam_info:
                due_d = exam_info.get("due_date")
                if isinstance(due_d, datetime):
                    exam_date = due_d.date()
                elif isinstance(due_d, str):
                    exam_date = datetime.fromisoformat(due_d[:10]).date()

            prio = calculate_topic_priority(top, exam_date, 1.0, date.today())
            sub = sub_map.get(s_id, {})
            scored_pending_topics.append({
                "id": top["id"],
                "name": top["name"],
                "subject_name": sub.get("name", "General"),
                "subject_color": sub.get("color", "#3b82f6"),
                "priority": prio,
                "mastery": top.get("mastery", 0.0),
                "difficulty": top.get("difficulty", 1),
                "est_hours": top.get("est_hours", 1.0)
            })
    scored_pending_topics.sort(key=lambda x: -x["priority"])

    # 8. Warnings Calculation
    missed_count = sum(1 for s in sessions if s.get("status") == "missed")
    infeasible_exams = [card for card in exam_readiness_cards if not card.get("feasible", True)]

    warnings = []
    if missed_count > 0:
        warnings.append({
            "type": "missed_sessions",
            "title": f"{missed_count} Missed Session(s)",
            "message": "You have missed study sessions. The scheduler has automatically adjusted your future plan.",
            "severity": "warning"
        })

    for inf in infeasible_exams:
        warnings.append({
            "type": "infeasible_exam",
            "title": f"Exam At Risk: {inf['exam_title']}",
            "message": f"Readiness is {inf['readiness_probability']}%. You need {inf['remaining_hours']}h but only have {inf['available_hours']}h usable time.",
            "severity": "critical"
        })

    return {
        "stats": {
            "overall_progress_pct": overall_progress_pct,
            "completed_topics": completed_topics,
            "total_topics": total_topics,
            "weekly_study_hours": weekly_study_hours,
            "upcoming_exams_count": len(upcoming_exams)
        },
        "subject_cards": subject_cards,
        "exam_readiness": exam_readiness_cards,
        "todays_plan": todays_sessions,
        "upcoming_deadlines": upcoming_deadlines,
        "priority_topics": scored_pending_topics[:5],
        "warnings": warnings
    }
