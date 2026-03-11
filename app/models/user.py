from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserProfile(BaseModel):
    id: str
    email: EmailStr
    name: str
    friend_code: str
    is_onboarded: bool = False
    streak_days: int = 0
    streak_start_date: Optional[str] = None
    total_tasks_completed: int = 0
    level: int = 1
    friends: list[str] = []
    onboarding_data: Optional[dict] = None
    personal_motto: Optional[str] = None
    primary_goal: Optional[str] = None
    motivation_driver: Optional[str] = None
    danger_zone_time: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    personal_motto: Optional[str] = None
    primary_goal: Optional[str] = None
    motivation_driver: Optional[str] = None
    danger_zone_time: Optional[str] = None
