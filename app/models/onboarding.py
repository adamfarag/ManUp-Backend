from pydantic import BaseModel


class OnboardingSubmission(BaseModel):
    symptoms: list[str]
    duration: str
    frequency: str
    previous_attempts: str
    triggers: list[str]
    impact_areas: list[str]
    desired_outcomes: list[str]
    locations: list[str]
