from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

class TopicCreate(BaseModel):
    subject_id: str
    name: str = Field(..., min_length=1)
    est_hours: float = Field(..., gt=0)
    difficulty: int = Field(..., ge=1, le=5)
    weight: int = Field(..., ge=1, le=5)
    mastery: float = Field(default=0.0, ge=0.0, le=1.0)
    status: Literal["pending", "in_progress", "completed"] = "pending"

class TopicUpdate(BaseModel):
    name: Optional[str] = None
    est_hours: Optional[float] = Field(default=None, gt=0)
    difficulty: Optional[int] = Field(default=None, ge=1, le=5)
    weight: Optional[int] = Field(default=None, ge=1, le=5)
    mastery: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    status: Optional[Literal["pending", "in_progress", "completed"]] = None

class TopicResponse(BaseModel):
    id: str
    user_id: str
    subject_id: str
    name: str
    est_hours: float
    difficulty: int
    weight: int
    mastery: float
    status: str
    created_at: datetime
    updated_at: datetime
