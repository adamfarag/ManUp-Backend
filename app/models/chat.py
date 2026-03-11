from datetime import datetime

from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


class ChatMessageResponse(BaseModel):
    content: str
    is_from_user: bool
    created_at: datetime
