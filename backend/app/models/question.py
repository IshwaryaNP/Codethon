from pydantic import BaseModel, Field
from typing import List, Optional

class QuestionSchema(BaseModel):
    question: str
    options: List[str] = Field(..., min_length=4, max_length=4)
    correct_index: int = Field(..., ge=0, le=3)
    explanation: str
    subtopic: str

class QuestionDB(QuestionSchema):
    id: str
    topic_id: str
    is_reported: bool = False
    report_reason: Optional[str] = None

# Schema exposed to frontend before submission (WITHOUT correct_index & explanation)
class QuestionFrontendResponse(BaseModel):
    id: str
    topic_id: str
    question: str
    options: List[str]
    subtopic: str
    is_reported: bool = False
