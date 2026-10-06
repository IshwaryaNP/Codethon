from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Tuple, Optional
import math

def calculate_topic_priority(
    topic: Dict[str, Any],
    exam_due_date: Optional[date],
    exam_weight: float = 1.0,
    today: Optional[date] = None
) -> float:
    """
    Calculates priority score for a topic.
    Formula: priority = urgency * exam_weight * (1 - mastery) * difficulty
    urgency = 1 / max(days_left_to_exam, 1)
    """
    if today is None:
        today = date.today()

    if exam_due_date:
        days_left = (exam_due_date - today).days
        days_left = max(days_left, 1)
    else:
        days_left = 30  # Default fallback horizon

    urgency = 1.0 / days_left
    mastery = max(0.0, min(1.0, float(topic.get("mastery", 0.0))))
    difficulty = float(topic.get("difficulty", 1))
    weight = float(topic.get("weight", 1)) * exam_weight

    priority = urgency * weight * (1.0 - mastery) * difficulty
    return round(priority, 6)

def get_day_name(dt: date) -> str:
    return dt.strftime("%A").lower()

def run_scheduler(
    topics: List[Dict[str, Any]],
    events: List[Dict[str, Any]],
    availability: Dict[str, float],
    velocity_map: Dict[str, float],
    today: date,
    buffer_ratio: float = 0.20,
    max_days_ahead: int = 60
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Pure deterministic scheduler.
    
    Returns:
      - sessions: list of dicts with planned sessions
      - feasibility_report: dict containing overall & per-exam capacity assessment
    """
    # 1. Filter out completed topics
    active_topics = [
        t for t in topics
        if t.get("status") != "completed" and float(t.get("mastery", 0.0)) < 1.0
    ]

    # Map events by subject_id (find earliest upcoming exam per subject)
    subject_exams: Dict[str, Dict[str, Any]] = {}
    for evt in events:
        if evt.get("type") == "exam":
            sub_id = str(evt.get("subject_id", ""))
            due_dt = evt.get("due_date")
            if isinstance(due_dt, datetime):
                evt_date = due_dt.date()
            elif isinstance(due_dt, str):
                evt_date = datetime.fromisoformat(due_dt.replace("Z", "+00:00")).date()
            elif isinstance(due_dt, date):
                evt_date = due_dt
            else:
                continue

            if evt_date >= today:
                if sub_id not in subject_exams or evt_date < subject_exams[sub_id]["date"]:
                    subject_exams[sub_id] = {
                        "event_id": str(evt.get("id", evt.get("_id", ""))),
                        "title": evt.get("title", "Exam"),
                        "date": evt_date,
                        "weight": float(evt.get("weight", 1.0))
                    }

    # 2. Calculate topic priority & remaining velocity-adjusted minutes
    scored_topics = []
    for t in active_topics:
        sub_id = str(t.get("subject_id", ""))
        exam_info = subject_exams.get(sub_id)
        exam_date = exam_info["date"] if exam_info else None
        exam_weight = exam_info["weight"] if exam_info else 1.0

        prio = calculate_topic_priority(t, exam_date, exam_weight, today)
        
        vel = velocity_map.get(sub_id, 1.0)
        est_hours = float(t.get("est_hours", 1.0))
        mastery = float(t.get("mastery", 0.0))
        remaining_hours = est_hours * (1.0 - mastery) * vel
        remaining_minutes = int(math.ceil(remaining_hours * 60))

        scored_topics.append({
            "topic": t,
            "topic_id": str(t.get("id", t.get("_id", ""))),
            "subject_id": sub_id,
            "topic_name": t.get("name", ""),
            "priority": prio,
            "remaining_minutes": remaining_minutes,
            "exam_date": exam_date,
            "exam_title": exam_info["title"] if exam_info else None
        })

    # Sort topics by priority DESC, tie-break by topic_id
    scored_topics.sort(key=lambda x: (-x["priority"], x["topic_id"]))

    # 3. Schedule sessions onto calendar days
    sessions = []
    current_date = today

    # Track daily capacity remaining for each date
    daily_remaining_minutes: Dict[date, float] = {}

    for item in scored_topics:
        mins_needed = item["remaining_minutes"]
        if mins_needed <= 0:
            continue

        deadline = item["exam_date"] or (today + timedelta(days=max_days_ahead))
        curr = today

        while mins_needed > 0 and curr <= deadline and (curr - today).days <= max_days_ahead:
            if curr not in daily_remaining_minutes:
                day_name = get_day_name(curr)
                avail_hours = float(availability.get(day_name, 2.0))
                usable_hours = avail_hours * (1.0 - buffer_ratio)
                daily_remaining_minutes[curr] = usable_hours * 60

            avail_mins = daily_remaining_minutes[curr]

            if avail_mins >= 15:  # Minimum 15-minute slot
                allocated = min(mins_needed, int(avail_mins))
                sessions.append({
                    "topic_id": item["topic_id"],
                    "subject_id": item["subject_id"],
                    "topic_name": item["topic_name"],
                    "planned_date": curr.isoformat(),
                    "planned_minutes": allocated,
                    "actual_minutes": 0,
                    "status": "planned",
                    "type": "study"
                })
                mins_needed -= allocated
                daily_remaining_minutes[curr] -= allocated

            curr += timedelta(days=1)

    # 4. Calculate overall & per-exam feasibility
    total_required_mins = sum(t["remaining_minutes"] for t in scored_topics)
    total_available_usable_mins = 0.0

    # Calculate usable capacity up to 30 days or latest exam date
    max_horizon = max([e["date"] for e in subject_exams.values()] + [today + timedelta(days=30)])
    check_date = today
    while check_date <= max_horizon:
        day_name = get_day_name(check_date)
        raw_avail = float(availability.get(day_name, 2.0))
        total_available_usable_mins += raw_avail * 60 * (1.0 - buffer_ratio)
        check_date += timedelta(days=1)

    overall_feasible = total_required_mins <= total_available_usable_mins

    exam_reports = []
    for sub_id, exam in subject_exams.items():
        exam_date = exam["date"]
        # Required hours for this subject
        sub_topics = [t for t in scored_topics if t["subject_id"] == sub_id]
        sub_req_mins = sum(t["remaining_minutes"] for t in sub_topics)
        
        # Available usable hours up to exam date
        sub_avail_mins = 0.0
        d = today
        while d <= exam_date:
            day_name = get_day_name(d)
            raw_avail = float(availability.get(day_name, 2.0))
            sub_avail_mins += raw_avail * 60 * (1.0 - buffer_ratio)
            d += timedelta(days=1)

        req_hours = round(sub_req_mins / 60.0, 1)
        avail_hours = round(sub_avail_mins / 60.0, 1)
        deficit = round(max(0.0, req_hours - avail_hours), 1)
        is_feasible = req_hours <= avail_hours

        exam_reports.append({
            "subject_id": sub_id,
            "exam_title": exam["title"],
            "exam_date": exam_date.isoformat(),
            "required_hours": req_hours,
            "available_hours": avail_hours,
            "deficit_hours": deficit,
            "feasible": is_feasible
        })

    feasibility_report = {
        "overall_feasible": overall_feasible,
        "total_required_hours": round(total_required_mins / 60.0, 1),
        "total_available_hours": round(total_available_usable_mins / 60.0, 1),
        "total_deficit_hours": round(max(0.0, (total_required_mins - total_available_usable_mins) / 60.0), 1),
        "exams": exam_reports
    }

    return sessions, feasibility_report
