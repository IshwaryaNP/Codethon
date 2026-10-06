from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
from datetime import datetime, date, timedelta, timezone
from bson import ObjectId
from app.db import get_db
from app.auth.dependencies import get_current_user
from app.models.question import QuestionFrontendResponse, QuestionDB
from app.models.quiz_attempt import QuizSubmission, QuizResultResponse, QuizReportQuestion
from app.services.llm import generate_mcqs_with_llm
from app.services.quiz import grade_quiz_attempt, create_spaced_revision_dates
from app.routers.sessions import _trigger_automatic_replan

router = APIRouter(prefix="/quizzes", tags=["Quizzes"])

@router.post("/generate/{topic_id}", response_model=List[QuestionFrontendResponse])
async def generate_quiz_for_topic(
    topic_id: str,
    current_user: dict = Depends(get_current_user)
):
    db = get_db()
    user_id = current_user["id"]

    try:
        topic = await db.topics.find_one({"_id": ObjectId(topic_id), "user_id": user_id})
    except Exception:
        topic = None

    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    # Check if cached questions exist for this topic
    existing_cursor = db.questions.find({"topic_id": topic_id, "is_reported": False})
    cached_qs = [q async for q in existing_cursor]

    if len(cached_qs) >= 5:
        res = []
        for q in cached_qs[:5]:
            q["id"] = str(q["_id"])
            res.append(QuestionFrontendResponse(**q))
        return res

    # Otherwise, fetch subject name and call Anthropic LLM generator
    subject_id = topic.get("subject_id", "")
    subj_doc = await db.subjects.find_one({"_id": ObjectId(subject_id)}) if ObjectId.is_valid(subject_id) else None
    subj_name = subj_doc.get("name", "General") if subj_doc else "General"

    success, questions_data, err_msg = await generate_mcqs_with_llm(topic["name"], subj_name)

    if not success or not questions_data:
        # Fallback question set if Anthropic API key is not present or failed
        questions_data = [
            {
                "question": f"What is a fundamental concept in {topic['name']}?",
                "options": ["Core Specification", "Secondary Component", "Legacy Feature", "Deprecated Primitive"],
                "correct_index": 0,
                "explanation": "Core specification defines the baseline architecture of this topic.",
                "subtopic": "Core Fundamentals"
            },
            {
                "question": f"Which operation is most common when applying {topic['name']}?",
                "options": ["Optimization Routine", "Initialization Phase", "Garbage Collection", "Infinite Loop"],
                "correct_index": 1,
                "explanation": "Initialization Phase prepares the required state machine before execution.",
                "subtopic": "Operations"
            },
            {
                "question": f"What is the time/space complexity characteristic of {topic['name']}?",
                "options": ["O(1) Constant", "O(log N) Logarithmic", "O(N) Linear", "O(N^2) Quadratic"],
                "correct_index": 2,
                "explanation": "Linear scale factor guarantees predictable execution bounds.",
                "subtopic": "Complexity"
            },
            {
                "question": f"What is the primary constraint to keep in mind for {topic['name']}?",
                "options": ["Memory Overhead", "Network Latency", "Type Safety", "All of the above"],
                "correct_index": 3,
                "explanation": "All listed factors directly influence optimal system implementation.",
                "subtopic": "Best Practices"
            },
            {
                "question": f"How is errors or edge cases handled in {topic['name']}?",
                "options": ["Exception Propagation", "Silent Fallback", "Null Pointer Dereference", "Fatal Termination"],
                "correct_index": 0,
                "explanation": "Explicit exception handling ensures stability and fault tolerance.",
                "subtopic": "Error Handling"
            }
        ]

    # Save questions in database
    saved_questions = []
    for q in questions_data:
        doc = {
            "topic_id": topic_id,
            "question": q["question"],
            "options": q["options"],
            "correct_index": q["correct_index"],
            "explanation": q["explanation"],
            "subtopic": q["subtopic"],
            "is_reported": False,
            "created_at": datetime.now(timezone.utc)
        }
        res = await db.questions.insert_one(doc)
        doc["id"] = str(res.inserted_id)
        saved_questions.append(doc)

    frontend_qs = [QuestionFrontendResponse(**q) for q in saved_questions]
    return frontend_qs


@router.post("/submit", response_model=QuizResultResponse)
async def submit_quiz_attempt(
    submission: QuizSubmission,
    current_user: dict = Depends(get_current_user)
):
    db = get_db()
    user_id = current_user["id"]
    topic_id = submission.topic_id

    try:
        topic = await db.topics.find_one({"_id": ObjectId(topic_id), "user_id": user_id})
    except Exception:
        topic = None

    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    # Fetch questions for topic
    cursor = db.questions.find({"topic_id": topic_id})
    questions = [q async for q in cursor]
    for q in questions:
        q["id"] = str(q["_id"])

    # Grade in Python
    score, correct_count, total_valid, conf_warning, weak_subtopics = grade_quiz_attempt(
        questions=questions,
        user_answers=submission.answers,
        confidence=submission.confidence
    )

    now = datetime.now(timezone.utc)

    # Save quiz attempt record
    attempt_doc = {
        "user_id": user_id,
        "topic_id": topic_id,
        "confidence": submission.confidence,
        "score": score,
        "correct_count": correct_count,
        "total_valid_questions": total_valid,
        "new_mastery": score,  # computed below
        "confidence_warning": conf_warning,
        "weak_subtopics": weak_subtopics,
        "answers": submission.answers,
        "created_at": now
    }

    # Update topic mastery in DB
    new_mastery = 0.7 * score + 0.3 * (submission.confidence / 5.0)
    new_mastery = round(max(0.0, min(1.0, new_mastery)), 4)
    attempt_doc["new_mastery"] = new_mastery

    new_status = "completed" if new_mastery >= 0.85 else "in_progress"

    await db.topics.update_one(
        {"_id": ObjectId(topic_id)},
        {"$set": {
            "mastery": new_mastery,
            "status": new_status,
            "updated_at": now
        }}
    )

    result_entry = await db.quiz_attempts.insert_one(attempt_doc)
    attempt_doc["id"] = str(result_entry.inserted_id)

    # 1. Create weak subtopic revision session if student struggled on any subtopic
    if weak_subtopics:
        rev_date = (date.today() + timedelta(days=1)).isoformat()
        # Check if weak subtopic session already exists
        dup_chk = await db.sessions.find_one({
            "user_id": user_id,
            "topic_id": topic_id,
            "planned_date": rev_date,
            "type": "revision"
        })
        if not dup_chk:
            await db.sessions.insert_one({
                "user_id": user_id,
                "subject_id": topic.get("subject_id"),
                "topic_id": topic_id,
                "planned_date": rev_date,
                "planned_minutes": 20,
                "actual_minutes": 0,
                "status": "planned",
                "type": "revision",
                "created_at": now,
                "updated_at": now
            })

    # 2. Create spaced revisions if topic is now completed
    if new_status == "completed":
        # Find earliest upcoming exam date for subject to avoid scheduling after exam
        subject_id = topic.get("subject_id")
        exam_evt = await db.events.find_one({
            "user_id": user_id,
            "subject_id": subject_id,
            "type": "exam",
            "due_date": {"$gte": now}
        })
        exam_date = None
        if exam_evt:
            d = exam_evt.get("due_date")
            exam_date = d.date() if isinstance(d, datetime) else None

        spaced_dates = create_spaced_revision_dates(date.today(), exam_date)
        for s_date in spaced_dates:
            s_date_str = s_date.isoformat()
            chk = await db.sessions.find_one({
                "user_id": user_id,
                "topic_id": topic_id,
                "planned_date": s_date_str,
                "type": "revision"
            })
            if not chk:
                await db.sessions.insert_one({
                    "user_id": user_id,
                    "subject_id": subject_id,
                    "topic_id": topic_id,
                    "planned_date": s_date_str,
                    "planned_minutes": 20,
                    "actual_minutes": 0,
                    "status": "planned",
                    "type": "revision",
                    "created_at": now,
                    "updated_at": now
                })

    # Auto Re-plan to adjust future calendar
    await _trigger_automatic_replan(user_id)

    return QuizResultResponse(**attempt_doc)


@router.post("/report")
async def report_question(
    report_in: QuizReportQuestion,
    current_user: dict = Depends(get_current_user)
):
    db = get_db()
    try:
        q_id = ObjectId(report_in.question_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid question_id")

    res = await db.questions.find_one_and_update(
        {"_id": q_id},
        {"$set": {
            "is_reported": True,
            "report_reason": report_in.reason
        }},
        return_document=True
    )

    if not res:
        raise HTTPException(status_code=404, detail="Question not found")

    return {"message": "Question reported successfully. It will be excluded from quiz scoring."}
