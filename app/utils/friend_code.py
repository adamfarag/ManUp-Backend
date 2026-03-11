import random
import string

from motor.motor_asyncio import AsyncIOMotorDatabase


async def generate_friend_code(db: AsyncIOMotorDatabase) -> str:
    """Generate a unique 6-character uppercase alphanumeric friend code."""
    while True:
        code = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
        existing = await db.users.find_one({"friend_code": code})
        if not existing:
            return code
