import logging
import random
from typing import Optional

import httpx
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.config import settings
from app.utils.datetime_helpers import utc_now

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a supportive recovery coach in the ManUp app. "
    "You help men overcome pornography addiction. "
    "Be empathetic, direct, and encouraging. "
    "Keep responses concise (2-3 sentences). "
    "Never judge. Focus on practical advice and emotional support."
)

CANNED_RESPONSES = [
    "You're doing great by reaching out. Remember, every day you choose to be better is a victory. Stay focused on your goals.",
    "It's completely normal to have tough days. What matters is that you keep going. Try doing one of your daily tasks right now.",
    "I hear you. Recovery isn't a straight line — it's a journey with ups and downs. You've got the strength to push through this.",
    "That takes real courage to share. Remember why you started this journey and the person you're working to become.",
    "You're not alone in this. Many men are on the same path. Focus on what you can control today, right now.",
    "Progress, not perfection. Every step forward counts, even the small ones. What's one positive thing you can do in the next 5 minutes?",
    "I believe in you. The fact that you're here and talking about it shows incredible strength. Keep building those healthy habits.",
    "Take a deep breath. Urges are temporary — they pass. Try going for a walk, doing some push-ups, or calling a friend.",
    "Remember: you are more than your struggles. Each day is a fresh start. Focus on winning today.",
    "It's okay to feel vulnerable. That's actually a sign of growth. Keep pushing forward — your future self will thank you.",
]


async def get_ai_response(
    db: AsyncIOMotorDatabase, user_id: str, message: str
) -> str:
    """
    Get an AI response. Uses OpenAI if the API key is configured,
    otherwise falls back to canned responses.
    """
    if (
        settings.openai_api_key
        and settings.openai_api_key != "sk-placeholder"
        and not settings.openai_api_key.startswith("sk-placeholder")
    ):
        return await _get_openai_response(db, user_id, message)
    else:
        return _get_canned_response()


async def _get_openai_response(
    db: AsyncIOMotorDatabase, user_id: str, message: str
) -> str:
    """Call OpenAI chat completions API."""
    # Fetch recent chat history for context
    cursor = db.chat_messages.find(
        {"user_id": user_id}
    ).sort("created_at", -1).limit(10)

    history_messages = []
    async for msg in cursor:
        role = "user" if msg.get("is_from_user") else "assistant"
        history_messages.append({
            "role": role,
            "content": msg.get("content", ""),
        })

    # Reverse to chronological order
    history_messages.reverse()

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *history_messages,
        {"role": "user", "content": message},
    ]

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.openai_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "gpt-4.1-nano",
                    "messages": messages,
                    "max_tokens": 200,
                    "temperature": 0.7,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        return _get_canned_response()


def _get_canned_response() -> str:
    """Return a random canned response."""
    return random.choice(CANNED_RESPONSES)


async def save_message(
    db: AsyncIOMotorDatabase,
    user_id: str,
    content: str,
    is_from_user: bool,
) -> dict:
    """Save a chat message to the database."""
    now = utc_now()
    message_doc = {
        "user_id": user_id,
        "content": content,
        "is_from_user": is_from_user,
        "created_at": now,
    }
    result = await db.chat_messages.insert_one(message_doc)
    message_doc["id"] = str(result.inserted_id)
    message_doc.pop("_id", None)
    return message_doc


async def get_chat_history(
    db: AsyncIOMotorDatabase,
    user_id: str,
    skip: int = 0,
    limit: int = 50,
) -> list[dict]:
    """Get paginated chat history for a user."""
    cursor = (
        db.chat_messages.find({"user_id": user_id})
        .sort("created_at", -1)
        .skip(skip)
        .limit(limit)
    )

    messages = []
    async for msg in cursor:
        messages.append({
            "content": msg.get("content", ""),
            "is_from_user": msg.get("is_from_user", True),
            "created_at": msg.get("created_at"),
        })

    # Return in chronological order
    messages.reverse()
    return messages
