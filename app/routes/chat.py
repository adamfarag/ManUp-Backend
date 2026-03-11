from fastapi import APIRouter, Depends, Query, status

from app.database import get_db
from app.middleware.auth_middleware import get_current_user
from app.models.chat import ChatMessageResponse, ChatRequest, ChatResponse
from app.services.chat_service import get_ai_response, get_chat_history, save_message

router = APIRouter()


@router.post("/chat/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user),
):
    """Send a message and get an AI response."""
    db = get_db()
    user_id = current_user["id"]

    # Save user message
    await save_message(db, user_id, request.message, is_from_user=True)

    # Get AI response
    reply = await get_ai_response(db, user_id, request.message)

    # Save AI response
    await save_message(db, user_id, reply, is_from_user=False)

    return ChatResponse(reply=reply)


@router.get("/chat/history", response_model=list[ChatMessageResponse])
async def chat_history(
    skip: int = Query(0, ge=0, description="Number of messages to skip"),
    limit: int = Query(50, ge=1, le=100, description="Max messages to return"),
    current_user: dict = Depends(get_current_user),
):
    """Get paginated chat history."""
    db = get_db()
    messages = await get_chat_history(db, current_user["id"], skip=skip, limit=limit)
    return [ChatMessageResponse(**msg) for msg in messages]
