from fastapi import APIRouter, Depends, HTTPException, status

from app.database import get_db
from app.middleware.auth_middleware import get_current_user
from app.models.community import (
    ActivityItem,
    AddFriendRequest,
    FriendResponse,
    LeaderboardEntry,
)
from app.services.community_service import (
    add_friend,
    get_activity_feed,
    get_friends,
    get_leaderboard,
)

router = APIRouter()


@router.get("/community/leaderboard", response_model=list[LeaderboardEntry])
async def leaderboard(current_user: dict = Depends(get_current_user)):
    """Get the global leaderboard (top 100 by streak)."""
    db = get_db()
    return await get_leaderboard(db)


@router.get("/community/activity", response_model=list[ActivityItem])
async def activity_feed(current_user: dict = Depends(get_current_user)):
    """Get the community activity feed (last 50 events)."""
    db = get_db()
    return await get_activity_feed(db)


@router.get("/community/friends", response_model=list[FriendResponse])
async def my_friends(current_user: dict = Depends(get_current_user)):
    """Get the current user's friends list."""
    db = get_db()
    return await get_friends(db, current_user["id"])


@router.post("/community/friends", response_model=FriendResponse)
async def add_friend_route(
    request: AddFriendRequest,
    current_user: dict = Depends(get_current_user),
):
    """Add a friend by their friend code."""
    db = get_db()
    result = await add_friend(db, current_user["id"], request.friend_code)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Friend not found or you cannot add yourself",
        )

    return FriendResponse(**result)


@router.get("/community/me/friend-code")
async def get_my_friend_code(current_user: dict = Depends(get_current_user)):
    """Get the current user's friend code for sharing."""
    return {"friend_code": current_user["friend_code"]}
