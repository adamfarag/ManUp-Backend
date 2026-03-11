from typing import Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.utils.datetime_helpers import utc_now


async def get_user_by_id(db: AsyncIOMotorDatabase, user_id: str) -> Optional[dict]:
    """Fetch a user by their ObjectId string."""
    try:
        user = await db.users.find_one({"_id": ObjectId(user_id)})
    except Exception:
        return None
    if user:
        user["id"] = str(user.pop("_id"))
    return user


async def get_user_by_email(db: AsyncIOMotorDatabase, email: str) -> Optional[dict]:
    """Fetch a user by email."""
    user = await db.users.find_one({"email": email})
    if user:
        user["id"] = str(user.pop("_id"))
    return user


async def create_user(db: AsyncIOMotorDatabase, user_data: dict) -> dict:
    """Insert a new user document and return it with string id."""
    now = utc_now()
    user_data["created_at"] = now
    user_data["updated_at"] = now
    result = await db.users.insert_one(user_data)
    user_data["id"] = str(result.inserted_id)
    user_data.pop("_id", None)
    return user_data


async def update_user(
    db: AsyncIOMotorDatabase, user_id: str, update_data: dict
) -> Optional[dict]:
    """Update a user and return the updated document."""
    update_data["updated_at"] = utc_now()
    await db.users.update_one(
        {"_id": ObjectId(user_id)}, {"$set": update_data}
    )
    return await get_user_by_id(db, user_id)


async def delete_user(db: AsyncIOMotorDatabase, user_id: str) -> bool:
    """Delete a user and all associated data."""
    oid = ObjectId(user_id)
    await db.users.delete_one({"_id": oid})
    await db.tasks.delete_many({"user_id": user_id})
    await db.task_completions.delete_many({"user_id": user_id})
    await db.checkins.delete_many({"user_id": user_id})
    await db.setbacks.delete_many({"user_id": user_id})
    await db.chat_messages.delete_many({"user_id": user_id})
    await db.community_activity.delete_many({"user_id": user_id})
    await db.analytics_events.delete_many({"user_id": user_id})

    # Remove from other users' friend lists
    await db.users.update_many(
        {"friends": user_id}, {"$pull": {"friends": user_id}}
    )
    return True
