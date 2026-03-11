from fastapi import APIRouter, Depends, status
from bson import ObjectId

from app.database import get_db
from app.middleware.auth_middleware import get_current_user
from app.models.setback import SetbackCreate, SetbackResponse
from app.services.community_service import create_activity
from app.utils.datetime_helpers import utc_now, today_str

router = APIRouter()


@router.post(
    "/setbacks",
    response_model=SetbackResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_setback(
    setback: SetbackCreate,
    current_user: dict = Depends(get_current_user),
):
    """Record a setback. Resets the user's streak."""
    db = get_db()
    user_id = current_user["id"]
    now = utc_now()
    today = today_str()

    doc = {
        "user_id": user_id,
        "notes": setback.notes,
        "date_str": today,
        "created_at": now,
    }
    result = await db.setbacks.insert_one(doc)

    # Reset streak by clearing streak_start_date
    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {
            "streak_days": 0,
            "streak_start_date": None,
            "updated_at": now,
        }},
    )

    # Create a private community activity (only visible to the user)
    await create_activity(
        db,
        user_id,
        "setback",
        f"{current_user['name']} is starting fresh. Day 1!",
        "flame",
    )

    return SetbackResponse(
        id=str(result.inserted_id),
        user_id=user_id,
        notes=setback.notes,
        created_at=now,
    )


@router.get("/setbacks", response_model=list[SetbackResponse])
async def get_setbacks(current_user: dict = Depends(get_current_user)):
    """Get all setbacks for the current user."""
    db = get_db()

    cursor = db.setbacks.find(
        {"user_id": current_user["id"]}
    ).sort("created_at", -1)

    setbacks = []
    async for doc in cursor:
        setbacks.append(SetbackResponse(
            id=str(doc["_id"]),
            user_id=doc["user_id"],
            notes=doc.get("notes"),
            created_at=doc["created_at"],
        ))

    return setbacks
