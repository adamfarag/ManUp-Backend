from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator


class CheckInCreate(BaseModel):
    mood: int
    urge_level: int
    notes: Optional[str] = None

    @field_validator("mood", "urge_level")
    @classmethod
    def validate_range(cls, v: int) -> int:
        if v < 1 or v > 5:
            raise ValueError("Value must be between 1 and 5")
        return v


class CheckInResponse(BaseModel):
    id: str
    user_id: str
    mood: int
    urge_level: int
    notes: Optional[str] = None
    created_at: datetime
