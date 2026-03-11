from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TaskCreate(BaseModel):
    name: str
    icon: str
    category: str


class TaskResponse(BaseModel):
    id: str
    name: str
    icon: str
    category: str
    is_completed_today: bool = False
    user_id: str
    created_at: datetime


class TaskCompletionResponse(BaseModel):
    id: str
    task_id: str
    user_id: str
    date_str: str
    streak_days: int
    total_tasks_completed: int
    level: int
    created_at: datetime
