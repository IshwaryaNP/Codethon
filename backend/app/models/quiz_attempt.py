from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime

class QuizSubmission(BaseModel):
    topic_id: str
    confidence: int = Field(..., ge=1, le=5)
    answers: Dict[str, int]  # question_id -> chosen index

class QuizReportQuestion(BaseModel):
    question_id: str
    reason: str  # incorrect question, unclear question, duplicate, wrong answer, other

class QuizResultResponse(BaseModel):
    id: str
    user_id: str
    topic_id: str
    confidence: int
    score: float  # correct_answers / valid_questions (0.0 - 1.0)
    correct_count: int
    total_valid_questions: int
    new_mastery: float
    confidence_warning: bool
    weak_subtopics: List[str]
    created_at: datetime
