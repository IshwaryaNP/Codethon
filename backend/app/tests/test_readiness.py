import pytest
from datetime import date, timedelta
from app.services.readiness import calculate_exam_readiness

def test_readiness_easily_feasible():
    today = date(2026, 10, 1)
    exam_date = today + timedelta(days=20)
    topics = [{"name": "Topic A", "est_hours": 2.0, "mastery": 0.0, "status": "pending"}]
    avail = {"monday": 5.0, "tuesday": 5.0, "wednesday": 5.0, "thursday": 5.0, "friday": 5.0, "saturday": 5.0, "sunday": 5.0}

    res = calculate_exam_readiness(
        exam_id="e1", exam_title="Easy Exam", exam_date=exam_date,
        topics=topics, availability=avail, completed_sessions=[],
        today=today, random_seed=42
    )

    assert res["readiness_probability"] >= 90.0
    assert res["status"] == "Ready"
    assert res["feasible"] is True

def test_readiness_impossible_exam():
    today = date(2026, 10, 1)
    exam_date = today + timedelta(days=2)
    # Needs 50 hours in 2 days
    topics = [{"name": "Massive Topic", "est_hours": 50.0, "mastery": 0.0, "status": "pending"}]
    avail = {"monday": 2.0, "tuesday": 2.0, "wednesday": 2.0, "thursday": 2.0, "friday": 2.0, "saturday": 2.0, "sunday": 2.0}

    res = calculate_exam_readiness(
        exam_id="e2", exam_title="Hard Exam", exam_date=exam_date,
        topics=topics, availability=avail, completed_sessions=[],
        today=today, random_seed=42
    )

    assert res["readiness_probability"] == 0.0
    assert res["status"] == "Infeasible"
    assert res["feasible"] is False

def test_readiness_reproducibility():
    today = date(2026, 10, 1)
    exam_date = today + timedelta(days=10)
    topics = [{"name": "Topic A", "est_hours": 15.0, "mastery": 0.0, "status": "pending"}]
    avail = {"monday": 3.0, "tuesday": 3.0, "wednesday": 3.0, "thursday": 3.0, "friday": 3.0, "saturday": 3.0, "sunday": 3.0}

    res1 = calculate_exam_readiness("e1", "Exam", exam_date, topics, avail, [], today, random_seed=123)
    res2 = calculate_exam_readiness("e1", "Exam", exam_date, topics, avail, [], today, random_seed=123)

    assert res1["readiness_probability"] == res2["readiness_probability"], "Seeded Monte Carlo runs must produce identical results"
