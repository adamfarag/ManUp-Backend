from fastapi import APIRouter, Depends, status

from app.database import get_db
from app.middleware.auth_middleware import get_current_user
from app.models.onboarding import OnboardingSubmission
from app.services.user_service import update_user

router = APIRouter()


@router.post("/onboarding", status_code=status.HTTP_200_OK)
async def submit_onboarding(
    submission: OnboardingSubmission,
    current_user: dict = Depends(get_current_user),
):
    """Save onboarding responses and mark the user as onboarded."""
    db = get_db()

    await update_user(db, current_user["id"], {
        "is_onboarded": True,
        "onboarding_data": submission.model_dump(),
    })

    return {"message": "Onboarding completed successfully"}
