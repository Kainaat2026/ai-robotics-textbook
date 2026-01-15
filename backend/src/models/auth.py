"""Authentication API models (Pydantic schemas)."""

import uuid
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

from src.models.user_profile import SkillLevel


# Request models
class UserSignupRequest(BaseModel):
    """User signup request."""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)


class UserLoginRequest(BaseModel):
    """User login request."""
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=100)


class QuestionnaireRequest(BaseModel):
    """Questionnaire submission request (optional during signup)."""
    python_level: SkillLevel = SkillLevel.INTERMEDIATE
    ai_experience: SkillLevel = SkillLevel.BEGINNER
    robotics_experience: SkillLevel = SkillLevel.BEGINNER
    has_rtx_gpu: bool = False
    preferred_language: str = Field(default="en", max_length=5)


class PasswordChangeRequest(BaseModel):
    """Password change request."""
    current_password: str = Field(..., min_length=1, max_length=100)
    new_password: str = Field(..., min_length=8, max_length=100)


# Response models
class AuthToken(BaseModel):
    """Authentication token response."""
    access_token: str
    token_type: str = "bearer"

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }


class UserProfileResponse(BaseModel):
    """User profile response."""
    python_level: SkillLevel
    ai_experience: SkillLevel
    robotics_experience: SkillLevel
    has_rtx_gpu: bool
    preferred_language: str

    class Config:
        from_attributes = True


class UserMeResponse(BaseModel):
    """Current user information response."""
    id: uuid.UUID
    email: str
    is_active: bool
    is_verified: bool
    created_at: str
    profile: Optional[UserProfileResponse] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "user@example.com",
                "is_active": True,
                "is_verified": False,
                "created_at": "2024-01-15T10:30:00Z",
                "profile": {
                    "python_level": "intermediate",
                    "ai_experience": "beginner",
                    "robotics_experience": "beginner",
                    "has_rtx_gpu": True,
                    "preferred_language": "en"
                }
            }
        }
