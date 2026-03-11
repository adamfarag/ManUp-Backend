from fastapi import APIRouter, Depends, HTTPException, status

from app.database import get_db
from app.middleware.auth_middleware import get_current_user
from app.models.user import UserProfile, UserUpdate
from app.services.user_service import delete_user, update_user

router = APIRouter()


def _build_profile(user: dict) -> UserProfile:
    return UserProfile(
        id=user["id"],
        email=user["email"],
        name=user["name"],
        friend_code=user["friend_code"],
        is_onboarded=user.get("is_onboarded", False),
        streak_days=user.get("streak_days", 0),
        streak_start_date=user.get("streak_start_date"),
        total_tasks_completed=user.get("total_tasks_completed", 0),
        level=user.get("level", 1),
        friends=user.get("friends", []),
        onboarding_data=user.get("onboarding_data"),
        personal_motto=user.get("personal_motto"),
        primary_goal=user.get("primary_goal"),
        motivation_driver=user.get("motivation_driver"),
        danger_zone_time=user.get("danger_zone_time"),
        created_at=user["created_at"],
        updated_at=user["updated_at"],
    )


@router.get("/users/me", response_model=UserProfile)
async def get_me(current_user: dict = Depends(get_current_user)):
    """Get the current authenticated user's profile."""
    return _build_profile(current_user)


@router.put("/users/me", response_model=UserProfile)
async def update_me(
    update_data: UserUpdate,
    current_user: dict = Depends(get_current_user),
):
    """Update the current authenticated user's profile."""
    db = get_db()

    # Only include fields that were actually provided
    fields_to_update = update_data.model_dump(exclude_none=True)
    if not fields_to_update:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update",
        )

    # If email is being changed, check uniqueness
    if "email" in fields_to_update:
        existing = await db.users.find_one({"email": fields_to_update["email"]})
        if existing and str(existing["_id"]) != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already in use",
            )

    updated_user = await update_user(db, current_user["id"], fields_to_update)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return _build_profile(updated_user)


@router.delete("/users/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_me(current_user: dict = Depends(get_current_user)):
    """Delete the current authenticated user and all their data."""
    db = get_db()
    await delete_user(db, current_user["id"])
