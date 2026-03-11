from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class SetbackCreate(BaseModel):
    notes: Optional[str] = None


class SetbackResponse(BaseModel):
    id: str
    user_id: str
    notes: Optional[str] = None
    created_at: datetime
