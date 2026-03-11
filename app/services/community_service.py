from typing import Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.utils.datetime_helpers import utc_now


async def get_leaderboard(db: AsyncIOMotorDatabase) -> list[dict]:
    """Get top 100 users sorted by streak days descending."""
    cursor = db.users.find(
        {},
        {"name": 1, "streak_days": 1, "level": 1},
    ).sort("streak_days", -1).limit(100)

    entries = []
    rank = 1
    async for user in cursor:
        entries.append({
            "rank": rank,
            "name": user.get("name", "Anonymous"),
            "streak_days": user.get("streak_days", 0),
            "level": user.get("level", 1),
        })
        rank += 1
    return entries


async def get_activity_feed(db: AsyncIOMotorDatabase) -> list[dict]:
    """Get the last 50 community activity events."""
    cursor = db.community_activity.find().sort("created_at", -1).limit(50)
    activities = []
    async for activity in cursor:
        activities.append({
            "type": activity.get("type", ""),
            "message": activity.get("message", ""),
            "icon": activity.get("icon", ""),
            "created_at": activity.get("created_at"),
        })
    return activities


async def create_activity(
    db: AsyncIOMotorDatabase,
    user_id: str,
    activity_type: str,
    message: str,
    icon: str,
) -> None:
    """Create a community activity event."""
    await db.community_activity.insert_one({
        "user_id": user_id,
        "type": activity_type,
        "message": message,
        "icon": icon,
        "created_at": utc_now(),
    })


async def add_friend(
    db: AsyncIOMotorDatabase, user_id: str, friend_code: str
) -> Optional[dict]:
    """
    Look up a user by friend code and add them to the current user's friend list
    and vice versa. Returns the friend's info or None if not found.
    """
    friend = await db.users.find_one({"friend_code": friend_code})
    if not friend:
        return None

    friend_id = str(friend["_id"])

    # Don't add yourself
    if friend_id == user_id:
        return None

    # Add friend to current user's friend list (if not already there)
    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$addToSet": {"friends": friend_id}},
    )

    # Add current user to friend's friend list
    await db.users.update_one(
        {"_id": ObjectId(friend_id)},
        {"$addToSet": {"friends": user_id}},
    )

    return {
        "name": friend.get("name", "Anonymous"),
        "streak_days": friend.get("streak_days", 0),
        "level": friend.get("level", 1),
        "friend_code": friend.get("friend_code", ""),
    }


async def get_friends(db: AsyncIOMotorDatabase, user_id: str) -> list[dict]:
    """Get all friends for a user."""
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user or not user.get("friends"):
        return []

    friend_ids = [ObjectId(fid) for fid in user["friends"]]
    cursor = db.users.find(
        {"_id": {"$in": friend_ids}},
        {"name": 1, "streak_days": 1, "level": 1, "friend_code": 1},
    )

    friends = []
    async for friend in cursor:
        friends.append({
            "name": friend.get("name", "Anonymous"),
            "streak_days": friend.get("streak_days", 0),
            "level": friend.get("level", 1),
            "friend_code": friend.get("friend_code", ""),
        })
    return friends
