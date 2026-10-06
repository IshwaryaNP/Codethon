import pytest
from app.services.triage import run_triage_analysis

def test_triage_feasible():
    res = run_triage_analysis([], deficit_hours=0.0)
    assert res["status"] == "FEASIBLE"
    assert len(res["recommendations"]) == 0

def test_triage_infeasible_lowest_ratio_first():
    topics = [
        {"id": "t1", "name": "High Weight Short Topic", "weight": 5, "est_hours": 1.0, "mastery": 0.0},
        {"id": "t2", "name": "Low Weight Long Topic", "weight": 1, "est_hours": 5.0, "mastery": 0.0}
    ]
    # Ratio t1 = 5 / 1 = 5.0
    # Ratio t2 = 1 / 5 = 0.2

    res = run_triage_analysis(topics, deficit_hours=3.0, subject_name="Computer Networks")
    assert res["status"] == "INFEASIBLE"
    assert len(res["recommendations"]) > 0
    # First recommendation should be t2 (lowest value ratio)
    top_rec = res["recommendations"][0]
    assert top_rec["topic_id"] == "t2"
    assert top_rec["recommended_action"] == "drop"
