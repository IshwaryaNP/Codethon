from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

class EventCreate(BaseModel):
    title: str = Field(..., min_length=1)
    type: Literal["exam", "assignment"]
    subject_id: str
    due_date: datetime
    description: Optional[str] = ""

class EventUpdate(BaseModel):
    title: Optional[str] = None
    type: Optional[Literal["exam", "assignment"]] = None
    subject_id: Optional[str] = None
    due_date: Optional[datetime] = None
    description: Optional[str] = None

class EventResponse(BaseModel):
    id: str
    user_id: str
    title: str
    type: str
    subject_id: str
    due_date: datetime
    description: Optional[str] = ""
    created_at: datetime
    updated_at: datetime
