import pytest
from datetime import date, timedelta
from app.services.scheduler import calculate_topic_priority, run_scheduler

def test_priority_ordering():
    today = date(2026, 10, 1)
    
    topic_high_urgency = {
        "id": "t1", "name": "Urgent Topic", "subject_id": "s1",
        "difficulty": 4, "weight": 5, "mastery": 0.2
    }
    topic_low_urgency = {
        "id": "t2", "name": "Far Topic", "subject_id": "s1",
        "difficulty": 4, "weight": 5, "mastery": 0.2
    }

    # Exam in 5 days vs exam in 30 days
    prio1 = calculate_topic_priority(topic_high_urgency, today + timedelta(days=5), 1.0, today)
    prio2 = calculate_topic_priority(topic_low_urgency, today + timedelta(days=30), 1.0, today)

    assert prio1 > prio2, "Urgent topic closer to exam must have higher priority"

def test_scheduler_deterministic_allocation():
    today = date(2026, 10, 1)
    topics = [
        {"id": "t1", "subject_id": "s1", "name": "Binary Trees", "est_hours": 3.0, "difficulty": 4, "weight": 5, "mastery": 0.0, "status": "pending"},
        {"id": "t2", "subject_id": "s1", "name": "Graph Traversal", "est_hours": 2.0, "difficulty": 3, "weight": 4, "mastery": 0.0, "status": "pending"}
    ]
    events = [
        {"id": "e1", "subject_id": "s1", "title": "DS Midterm", "due_date": (today + timedelta(days=5)).isoformat(), "type": "exam"}
    ]
    avail = {"monday": 4.0, "tuesday": 4.0, "wednesday": 4.0, "thursday": 4.0, "friday": 4.0, "saturday": 4.0, "sunday": 4.0}
    vel_map = {"s1": 1.0}

    sessions1, rep1 = run_scheduler(topics, events, avail, vel_map, today, buffer_ratio=0.2)
    sessions2, rep2 = run_scheduler(topics, events, avail, vel_map, today, buffer_ratio=0.2)

    assert sessions1 == sessions2, "Scheduler output must be strictly deterministic"
    assert rep1["overall_feasible"] is True
    assert len(sessions1) > 0

def test_scheduler_completed_topic_skipping():
    today = date(2026, 10, 1)
    topics = [
        {"id": "t1", "subject_id": "s1", "name": "Finished Topic", "est_hours": 3.0, "difficulty": 4, "weight": 5, "mastery": 1.0, "status": "completed"}
    ]
    events = []
    avail = {"monday": 2.0, "tuesday": 2.0, "wednesday": 2.0, "thursday": 2.0, "friday": 2.0, "saturday": 2.0, "sunday": 2.0}

    sessions, _ = run_scheduler(topics, events, avail, {}, today)
    assert len(sessions) == 0, "Completed topics must not produce new study sessions"
