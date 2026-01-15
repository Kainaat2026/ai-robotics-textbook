"""Personalization API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from src.db.connection import get_db
from src.db.repositories.user_repo import UserRepository
from src.services.personalization_service import personalization_service
from src.utils.auth_dependencies import get_current_user
from src.models.auth import UserMeResponse

router = APIRouter()


class PersonalizeContentRequest(BaseModel):
    """Request to personalize chapter content."""
    chapter_id: str = Field(..., max_length=100)
    content: str = Field(..., min_length=10, max_length=50000)


class PersonalizeContentResponse(BaseModel):
    """Personalized content response."""
    chapter_id: str
    personalized_content: str
    skill_level: str
    response_time_ms: int

    class Config:
        json_schema_extra = {
            "example": {
                "chapter_id": "chapter-03-ros2-topics",
                "personalized_content": "# ROS 2 Topics - Simplified for Beginners...",
                "skill_level": "beginner",
                "response_time_ms": 3500
            }
        }


@router.post("/personalize", response_model=PersonalizeContentResponse)
async def personalize_content(
    request: PersonalizeContentRequest,
    current_user: UserMeResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> PersonalizeContentResponse:
    """
    Personalize chapter content based on user profile.

    Args:
        request: Content personalization request
        current_user: Authenticated user from JWT
        db: Database session

    Returns:
        Personalized content adapted to user's skill level

    Example:
        POST /api/personalize
        Authorization: Bearer <token>
        {
            "chapter_id": "chapter-03-ros2-topics",
            "content": "## ROS 2 Topics\n\nTopics enable..."
        }
    """
    user_repo = UserRepository(db)

    # Get full user profile with skill levels
    user_profile = await user_repo.get_user_profile(current_user.id)

    if not user_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found. Please complete questionnaire."
        )

    # Determine overall skill level (use highest level among Python/AI/Robotics)
    skill_levels = [
        user_profile.python_experience,
        user_profile.ai_ml_experience,
        user_profile.robotics_experience
    ]
    # Use the most advanced skill level
    from src.models.user import SkillLevel
    if SkillLevel.ADVANCED in skill_levels:
        overall_skill = SkillLevel.ADVANCED
    elif SkillLevel.INTERMEDIATE in skill_levels:
        overall_skill = SkillLevel.INTERMEDIATE
    else:
        overall_skill = SkillLevel.BEGINNER

    # Personalize content
    personalized_content, response_time_ms = await personalization_service.personalize_content(
        content=request.content,
        skill_level=overall_skill,
        has_rtx_gpu=user_profile.has_rtx_gpu,
        has_jetson=user_profile.has_jetson,
        has_robots=user_profile.has_robots
    )

    return PersonalizeContentResponse(
        chapter_id=request.chapter_id,
        personalized_content=personalized_content,
        skill_level=overall_skill.value,
        response_time_ms=response_time_ms
    )
