from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class LeaderboardEntry(BaseModel):
    rank: int
    name: str
    streak_days: int
    level: int


class FriendResponse(BaseModel):
    name: str
    streak_days: int
    level: int
    friend_code: str


class ActivityItem(BaseModel):
    type: str
    message: str
    icon: str
    created_at: datetime


class AddFriendRequest(BaseModel):
    friend_code: str
