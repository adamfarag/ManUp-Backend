from datetime import timedelta

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.utils.datetime_helpers import utc_now, date_str


async def calculate_streak(db: AsyncIOMotorDatabase, user_id: str) -> int:
    """
    Count consecutive days with at least 1 task completion and no setbacks.
    Walks backward from today, checking each day.
    """
    today = utc_now()
    streak = 0

    for days_back in range(0, 3650):  # max ~10 years
        check_date = today - timedelta(days=days_back)
        check_date_str = date_str(check_date)

        # Check if there was a setback on this day
        setback = await db.setbacks.find_one({
            "user_id": user_id,
            "date_str": check_date_str,
        })
        if setback:
            break

        # Check if there was at least one task completion on this day
        completion = await db.task_completions.find_one({
            "user_id": user_id,
            "date_str": check_date_str,
        })
        if completion:
            streak += 1
        else:
            # If today has no completions, that's okay - keep checking
            # But if a past day has no completions, the streak ends
            if days_back > 0:
                break

    return streak
