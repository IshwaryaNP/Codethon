from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class SubjectCreate(BaseModel):
    name: str = Field(..., min_length=1)
    description: Optional[str] = ""
    color: Optional[str] = "#3b82f6"  # default accent color
    initial_topic: Optional[str] = None
    initial_est_hours: Optional[float] = 2.0
    exam_date: Optional[str] = None

class SubjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None

class SubjectResponse(BaseModel):
    id: str
    user_id: str
    name: str
    description: Optional[str] = ""
    color: str = "#3b82f6"
    created_at: datetime
    updated_at: datetime
