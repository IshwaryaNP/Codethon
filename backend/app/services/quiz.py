from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Tuple, Optional

def create_spaced_revision_dates(
    completion_date: date,
    exam_date: Optional[date] = None
) -> List[date]:
    """
    Calculates spaced revision dates (+1, +3, +7, +14 days) after topic completion.
    Skips any date that falls on or after exam_date.
    """
    offsets = [1, 3, 7, 14]
    revision_dates = []
    for offset in offsets:
        rev_dt = completion_date + timedelta(days=offset)
        if exam_date is None or rev_dt < exam_date:
            revision_dates.append(rev_dt)
    return revision_dates


def grade_quiz_attempt(
    questions: List[Dict[str, Any]],
    user_answers: Dict[str, int],
    confidence: int
) -> Tuple[float, int, int, bool, List[str]]:
    """
    Grades quiz attempt deterministically in Python.
    
    Excludes reported questions from total valid count.
    
    Formula:
      quiz_score = correct_answers / valid_questions
      new_mastery = 0.7 * quiz_score + 0.3 * (confidence / 5.0)
    
    Returns:
      (score, correct_count, total_valid_questions, confidence_warning, weak_subtopics)
    """
    valid_questions = []
    for q in questions:
        q_id = str(q.get("id", q.get("_id", "")))
        if not q.get("is_reported", False):
            valid_questions.append(q)

    if not valid_questions:
        # Fallback if all reported or no questions
        score = 0.0
        new_mastery = 0.3 * (confidence / 5.0)
        return (score, 0, 0, False, [])

    correct_count = 0
    weak_subtopics = set()

    for q in valid_questions:
        q_id = str(q.get("id", q.get("_id", "")))
        correct_idx = q.get("correct_index")
        chosen_idx = user_answers.get(q_id)
        subtopic = q.get("subtopic", "General")

        if chosen_idx is not None and chosen_idx == correct_idx:
            correct_count += 1
        else:
            if subtopic:
                weak_subtopics.add(subtopic)

    score = correct_count / len(valid_questions)

    confidence_norm = max(1, min(5, confidence)) / 5.0
    new_mastery = 0.7 * score + 0.3 * confidence_norm
    new_mastery = round(max(0.0, min(1.0, new_mastery)), 4)

    confidence_warning = (confidence >= 4) and (score < 0.5)

    return (score, correct_count, len(valid_questions), confidence_warning, list(weak_subtopics))
