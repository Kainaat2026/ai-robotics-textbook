"""User profile model for personalization and questionnaire data."""

from sqlalchemy import Column, String, Boolean, Enum as SQLEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from src.db.connection import Base


class SkillLevel(str, enum.Enum):
    """Skill level enumeration for questionnaire."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class UserProfile(Base):
    """
    User profile model for storing questionnaire responses and preferences.

    Attributes:
        user_id: Foreign key to users table
        python_level: Python programming skill level
        ai_experience: AI/ML experience level
        robotics_experience: Robotics experience level
        has_rtx_gpu: Whether user has access to RTX GPU
        preferred_language: Preferred UI language (en or ur)
    """

    __tablename__ = "user_profiles"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    python_level = Column(SQLEnum(SkillLevel), default=SkillLevel.INTERMEDIATE, nullable=False)
    ai_experience = Column(SQLEnum(SkillLevel), default=SkillLevel.BEGINNER, nullable=False)
    robotics_experience = Column(SQLEnum(SkillLevel), default=SkillLevel.BEGINNER, nullable=False)
    has_rtx_gpu = Column(Boolean, default=False, nullable=False)
    preferred_language = Column(String(5), default="en", nullable=False)

    # Relationships
    user = relationship("User", back_populates="profile")

    def __repr__(self):
        return f"<UserProfile(user_id={self.user_id}, python={self.python_level}, ai={self.ai_experience})>"
