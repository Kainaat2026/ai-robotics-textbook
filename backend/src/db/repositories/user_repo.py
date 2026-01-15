"""User repository for async database operations."""

import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.user import User
from src.models.user_profile import UserProfile, SkillLevel


class UserRepository:
    """Repository for user database operations."""

    def __init__(self, db: AsyncSession):
        """
        Initialize repository with database session.

        Args:
            db: Async database session
        """
        self.db = db

    async def create_user(
        self,
        email: str,
        password_hash: str
    ) -> User:
        """
        Create a new user.

        Args:
            email: User email address
            password_hash: Hashed password

        Returns:
            Created user
        """
        user = User(
            email=email,
            password_hash=password_hash
        )

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def get_user_by_id(
        self,
        user_id: uuid.UUID,
        load_profile: bool = False
    ) -> Optional[User]:
        """
        Get user by ID.

        Args:
            user_id: User UUID
            load_profile: Whether to eager load profile

        Returns:
            User or None if not found
        """
        query = select(User).where(User.id == user_id)

        if load_profile:
            query = query.options(selectinload(User.profile))

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_user_by_email(
        self,
        email: str,
        load_profile: bool = False
    ) -> Optional[User]:
        """
        Get user by email address.

        Args:
            email: User email
            load_profile: Whether to eager load profile

        Returns:
            User or None if not found
        """
        query = select(User).where(User.email == email)

        if load_profile:
            query = query.options(selectinload(User.profile))

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def update_user(
        self,
        user_id: uuid.UUID,
        **updates
    ) -> Optional[User]:
        """
        Update user fields.

        Args:
            user_id: User UUID
            **updates: Fields to update

        Returns:
            Updated user or None if not found
        """
        user = await self.get_user_by_id(user_id)

        if not user:
            return None

        for field, value in updates.items():
            if hasattr(user, field):
                setattr(user, field, value)

        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def delete_user(self, user_id: uuid.UUID) -> bool:
        """
        Delete a user (and all related data via CASCADE).

        Args:
            user_id: User UUID

        Returns:
            True if deleted, False if not found
        """
        user = await self.get_user_by_id(user_id)

        if not user:
            return False

        await self.db.delete(user)
        await self.db.commit()

        return True

    async def create_user_profile(
        self,
        user_id: uuid.UUID,
        python_level: SkillLevel = SkillLevel.INTERMEDIATE,
        ai_experience: SkillLevel = SkillLevel.BEGINNER,
        robotics_experience: SkillLevel = SkillLevel.BEGINNER,
        has_rtx_gpu: bool = False,
        preferred_language: str = "en"
    ) -> UserProfile:
        """
        Create user profile (questionnaire data).

        Args:
            user_id: User UUID
            python_level: Python skill level
            ai_experience: AI/ML experience level
            robotics_experience: Robotics experience level
            has_rtx_gpu: GPU availability
            preferred_language: UI language preference

        Returns:
            Created profile
        """
        profile = UserProfile(
            user_id=user_id,
            python_level=python_level,
            ai_experience=ai_experience,
            robotics_experience=robotics_experience,
            has_rtx_gpu=has_rtx_gpu,
            preferred_language=preferred_language
        )

        self.db.add(profile)
        await self.db.commit()
        await self.db.refresh(profile)

        return profile

    async def get_user_profile(
        self,
        user_id: uuid.UUID
    ) -> Optional[UserProfile]:
        """
        Get user profile by user ID.

        Args:
            user_id: User UUID

        Returns:
            User profile or None
        """
        query = select(UserProfile).where(UserProfile.user_id == user_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def update_user_profile(
        self,
        user_id: uuid.UUID,
        **updates
    ) -> Optional[UserProfile]:
        """
        Update user profile fields.

        Args:
            user_id: User UUID
            **updates: Fields to update

        Returns:
            Updated profile or None
        """
        profile = await self.get_user_profile(user_id)

        if not profile:
            return None

        for field, value in updates.items():
            if hasattr(profile, field):
                setattr(profile, field, value)

        await self.db.commit()
        await self.db.refresh(profile)

        return profile
