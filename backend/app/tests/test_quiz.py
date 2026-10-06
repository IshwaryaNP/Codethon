import pytest
from datetime import date
from app.services.quiz import grade_quiz_attempt, create_spaced_revision_dates

def test_quiz_grading_perfect_score():
    questions = [
        {"id": "q1", "correct_index": 0, "subtopic": "SubA", "is_reported": False},
        {"id": "q2", "correct_index": 1, "subtopic": "SubB", "is_reported": False}
    ]
    user_answers = {"q1": 0, "q2": 1}
    confidence = 5  # high confidence

    score, correct, total, conf_warn, weak = grade_quiz_attempt(questions, user_answers, confidence)
    
    assert score == 1.0
    assert correct == 2
    assert total == 2
    assert conf_warn is False
    assert len(weak) == 0

def test_quiz_confidence_warning():
    questions = [
        {"id": "q1", "correct_index": 0, "subtopic": "SubA", "is_reported": False},
        {"id": "q2", "correct_index": 1, "subtopic": "SubB", "is_reported": False}
    ]
    # Wrong answers, but confidence 5/5
    user_answers = {"q1": 3, "q2": 3}
    confidence = 5

    score, correct, total, conf_warn, weak = grade_quiz_attempt(questions, user_answers, confidence)

    assert score == 0.0
    assert conf_warn is True, "High confidence with score < 50% must trigger warning"
    assert "SubA" in weak and "SubB" in weak

def test_reported_question_exclusion():
    questions = [
        {"id": "q1", "correct_index": 0, "subtopic": "SubA", "is_reported": False},
        {"id": "q2", "correct_index": 1, "subtopic": "SubB", "is_reported": True}  # Reported!
    ]
    user_answers = {"q1": 0, "q2": 0}
    confidence = 3

    score, correct, total, conf_warn, weak = grade_quiz_attempt(questions, user_answers, confidence)

    assert total == 1, "Reported questions must be excluded from valid question count"
    assert correct == 1
    assert score == 1.0

def test_spaced_revision_dates():
    completion_date = date(2026, 10, 1)
    exam_date = date(2026, 10, 10)  # Exam in 9 days

    dates = create_spaced_revision_dates(completion_date, exam_date)
    # Offsets are +1, +3, +7, +14 days.
    # +1 day = Oct 2 (before Oct 10)
    # +3 days = Oct 4 (before Oct 10)
    # +7 days = Oct 8 (before Oct 10)
    # +14 days = Oct 15 (on/after Oct 10 -> skipped!)
    assert len(dates) == 3
    assert dates == [date(2026, 10, 2), date(2026, 10, 4), date(2026, 10, 8)]
