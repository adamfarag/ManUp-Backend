from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings

client: AsyncIOMotorClient | None = None
db: AsyncIOMotorDatabase | None = None


async def connect_to_mongo() -> None:
    global client, db
    client = AsyncIOMotorClient(settings.mongo_url)
    db = client[settings.mongo_db]

    # Create indexes
    await db.users.create_index("email", unique=True)
    await db.users.create_index("friend_code", unique=True)
    await db.tasks.create_index("user_id")
    await db.task_completions.create_index([("user_id", 1), ("date_str", 1)])
    await db.checkins.create_index([("user_id", 1), ("created_at", -1)])
    await db.setbacks.create_index([("user_id", 1), ("created_at", -1)])
    await db.community_activity.create_index([("created_at", -1)])
    await db.chat_messages.create_index([("user_id", 1), ("created_at", -1)])
    await db.analytics_events.create_index([("user_id", 1), ("created_at", -1)])


async def close_mongo_connection() -> None:
    global client
    if client:
        client.close()


def get_db() -> AsyncIOMotorDatabase:
    if db is None:
        raise RuntimeError("Database not initialized")
    return db
