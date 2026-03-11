from typing import Optional

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel

from app.database import get_db
from app.middleware.auth_middleware import get_current_user
from app.services.analytics_service import track_event

router = APIRouter()


class AnalyticsEvent(BaseModel):
    event_name: str
    properties: Optional[dict] = None


@router.post("/analytics/event", status_code=status.HTTP_201_CREATED)
async def track_analytics_event(
    event: AnalyticsEvent,
    current_user: dict = Depends(get_current_user),
):
    """Track an analytics event."""
    db = get_db()
    await track_event(
        db,
        user_id=current_user["id"],
        event_name=event.event_name,
        properties=event.properties,
    )
    return {"message": "Event tracked"}
