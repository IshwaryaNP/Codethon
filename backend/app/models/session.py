from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

class SessionCreate(BaseModel):
    topic_id: str
    subject_id: str
    planned_date: str  # YYYY-MM-DD
    planned_minutes: int = Field(..., gt=0)
    type: Literal["study", "revision"] = "study"

class SessionUpdateStatus(BaseModel):
    status: Literal["done", "missed", "planned"]
    actual_minutes: Optional[int] = Field(default=None, ge=0)

class SessionResponse(BaseModel):
    id: str
    user_id: str
    subject_id: str
    topic_id: str
    topic_name: Optional[str] = ""
    subject_name: Optional[str] = ""
    subject_color: Optional[str] = "#3b82f6"
    planned_date: str
    planned_minutes: int
    actual_minutes: Optional[int] = 0
    status: Literal["planned", "done", "missed"]
    type: Literal["study", "revision"]
    created_at: datetime
    updated_at: datetime
