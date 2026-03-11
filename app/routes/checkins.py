from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query, status

from app.database import get_db
from app.middleware.auth_middleware import get_current_user
from app.models.checkin import CheckInCreate, CheckInResponse
from app.utils.datetime_helpers import utc_now

router = APIRouter()


@router.post(
    "/checkins",
    response_model=CheckInResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_checkin(
    checkin: CheckInCreate,
    current_user: dict = Depends(get_current_user),
):
    """Create a new check-in entry."""
    db = get_db()
    now = utc_now()

    doc = {
        "user_id": current_user["id"],
        "mood": checkin.mood,
        "urge_level": checkin.urge_level,
        "notes": checkin.notes,
        "created_at": now,
    }
    result = await db.checkins.insert_one(doc)

    return CheckInResponse(
        id=str(result.inserted_id),
        user_id=current_user["id"],
        mood=checkin.mood,
        urge_level=checkin.urge_level,
        notes=checkin.notes,
        created_at=now,
    )


@router.get("/checkins", response_model=list[CheckInResponse])
async def get_checkins(
    start_date: Optional[str] = Query(
        None, description="Start date filter (YYYY-MM-DD)"
    ),
    end_date: Optional[str] = Query(
        None, description="End date filter (YYYY-MM-DD)"
    ),
    current_user: dict = Depends(get_current_user),
):
    """Get check-ins for the current user with optional date range."""
    db = get_db()

    query: dict = {"user_id": current_user["id"]}

    if start_date or end_date:
        date_filter: dict = {}
        if start_date:
            try:
                start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                date_filter["$gte"] = start_dt
            except ValueError:
                pass
        if end_date:
            try:
                end_dt = datetime.strptime(end_date, "%Y-%m-%d")
                # Include the entire end date
                end_dt = end_dt.replace(hour=23, minute=59, second=59)
                date_filter["$lte"] = end_dt
            except ValueError:
                pass
        if date_filter:
            query["created_at"] = date_filter

    cursor = db.checkins.find(query).sort("created_at", -1)

    checkins = []
    async for doc in cursor:
        checkins.append(CheckInResponse(
            id=str(doc["_id"]),
            user_id=doc["user_id"],
            mood=doc["mood"],
            urge_level=doc["urge_level"],
            notes=doc.get("notes"),
            created_at=doc["created_at"],
        ))

    return checkins
