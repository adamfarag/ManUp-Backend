import logging

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.config import settings
from app.utils.datetime_helpers import utc_now

logger = logging.getLogger(__name__)


async def track_event(
    db: AsyncIOMotorDatabase,
    user_id: str,
    event_name: str,
    properties: dict | None = None,
) -> None:
    """
    Track an analytics event. Saves to DB always.
    If Mixpanel token is configured, logs intent (actual Mixpanel integration
    would use mixpanel-python sync client in a background task).
    """
    now = utc_now()
    event_doc = {
        "user_id": user_id,
        "event_name": event_name,
        "properties": properties or {},
        "created_at": now,
    }
    await db.analytics_events.insert_one(event_doc)

    if settings.mixpanel_token and settings.mixpanel_token != "placeholder":
        logger.info(
            f"Mixpanel track: user={user_id} event={event_name} "
            f"properties={properties}"
        )
    else:
        logger.debug(
            f"Analytics event (no Mixpanel): user={user_id} event={event_name}"
        )
