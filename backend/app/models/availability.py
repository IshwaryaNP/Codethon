from pydantic import BaseModel, Field

class AvailabilityConfig(BaseModel):
    monday: float = Field(default=2.0, ge=0.0, le=24.0)
    tuesday: float = Field(default=2.0, ge=0.0, le=24.0)
    wednesday: float = Field(default=2.0, ge=0.0, le=24.0)
    thursday: float = Field(default=2.0, ge=0.0, le=24.0)
    friday: float = Field(default=2.0, ge=0.0, le=24.0)
    saturday: float = Field(default=4.0, ge=0.0, le=24.0)
    sunday: float = Field(default=4.0, ge=0.0, le=24.0)

class AvailabilityResponse(AvailabilityConfig):
    id: str
    user_id: str
