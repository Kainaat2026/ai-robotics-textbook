"""User progress repository for chapter completion tracking."""

import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import select, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user_progress import UserProgress, QuizAttempt, UserBookmark


class ProgressRepository:
    """Repository for user progress tracking operations."""

    def __init__(self, db: AsyncSession):
        """
        Initialize repository with database session.

        Args:
            db: Async database session
        """
        self.db = db

    async def get_user_progress(
        self,
        user_id: uuid.UUID,
        chapter_id: str
    ) -> Optional[UserProgress]:
        """
        Get progress for a specific chapter.

        Args:
            user_id: User UUID
            chapter_id: Chapter identifier

        Returns:
            UserProgress or None
        """
        query = select(UserProgress).where(
            and_(
                UserProgress.user_id == user_id,
                UserProgress.chapter_id == chapter_id
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_all_user_progress(
        self,
        user_id: uuid.UUID
    ) -> List[UserProgress]:
        """
        Get all progress records for a user.

        Args:
            user_id: User UUID

        Returns:
            List of UserProgress records
        """
        query = select(UserProgress).where(
            UserProgress.user_id == user_id
        ).order_by(UserProgress.last_accessed_at.desc())

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create_or_update_progress(
        self,
        user_id: uuid.UUID,
        chapter_id: str,
        **updates
    ) -> UserProgress:
        """
        Create new progress record or update existing one.

        Args:
            user_id: User UUID
            chapter_id: Chapter identifier
            **updates: Fields to update

        Returns:
            UserProgress record
        """
        # Try to get existing progress
        progress = await self.get_user_progress(user_id, chapter_id)

        if progress:
            # Update existing
            for field, value in updates.items():
                if hasattr(progress, field):
                    setattr(progress, field, value)

            progress.last_accessed_at = datetime.utcnow()
        else:
            # Create new
            progress = UserProgress(
                user_id=user_id,
                chapter_id=chapter_id,
                **updates
            )
            self.db.add(progress)

        await self.db.commit()
        await self.db.refresh(progress)

        return progress

    async def mark_chapter_complete(
        self,
        user_id: uuid.UUID,
        chapter_id: str
    ) -> UserProgress:
        """
        Mark a chapter as completed.

        Args:
            user_id: User UUID
            chapter_id: Chapter identifier

        Returns:
            Updated progress
        """
        return await self.create_or_update_progress(
            user_id=user_id,
            chapter_id=chapter_id,
            is_completed=True,
            completed_at=datetime.utcnow()
        )

    async def update_time_spent(
        self,
        user_id: uuid.UUID,
        chapter_id: str,
        minutes: int
    ) -> UserProgress:
        """
        Add time spent on a chapter.

        Args:
            user_id: User UUID
            chapter_id: Chapter identifier
            minutes: Minutes to add

        Returns:
            Updated progress
        """
        progress = await self.get_user_progress(user_id, chapter_id)

        if progress:
            new_time = progress.time_spent_minutes + minutes
        else:
            new_time = minutes

        return await self.create_or_update_progress(
            user_id=user_id,
            chapter_id=chapter_id,
            time_spent_minutes=new_time
        )

    async def record_quiz_attempt(
        self,
        user_id: uuid.UUID,
        chapter_id: str,
        score: float,
        correct_answers: int,
        total_questions: int,
        time_taken_seconds: int
    ) -> QuizAttempt:
        """
        Record a quiz attempt.

        Args:
            user_id: User UUID
            chapter_id: Chapter identifier
            score: Percentage score (0-100)
            correct_answers: Number of correct answers
            total_questions: Total number of questions
            time_taken_seconds: Time taken in seconds

        Returns:
            Created QuizAttempt
        """
        # Create quiz attempt record
        attempt = QuizAttempt(
            user_id=user_id,
            chapter_id=chapter_id,
            score=score,
            correct_answers=correct_answers,
            total_questions=total_questions,
            time_taken_seconds=time_taken_seconds
        )

        self.db.add(attempt)

        # Update user progress with quiz data
        progress = await self.get_user_progress(user_id, chapter_id)

        if progress:
            # Increment attempts
            new_attempts = progress.quiz_attempts + 1
            # Update best score
            new_best = max(progress.best_quiz_score or 0, score)

            await self.create_or_update_progress(
                user_id=user_id,
                chapter_id=chapter_id,
                quiz_score=score,
                quiz_attempts=new_attempts,
                best_quiz_score=new_best
            )
        else:
            # Create initial progress with quiz data
            await self.create_or_update_progress(
                user_id=user_id,
                chapter_id=chapter_id,
                quiz_score=score,
                quiz_attempts=1,
                best_quiz_score=score
            )

        await self.db.commit()
        await self.db.refresh(attempt)

        return attempt

    async def get_quiz_attempts(
        self,
        user_id: uuid.UUID,
        chapter_id: Optional[str] = None,
        limit: int = 10
    ) -> List[QuizAttempt]:
        """
        Get quiz attempts for a user.

        Args:
            user_id: User UUID
            chapter_id: Optional chapter filter
            limit: Maximum number of attempts to return

        Returns:
            List of QuizAttempt records
        """
        query = select(QuizAttempt).where(
            QuizAttempt.user_id == user_id
        )

        if chapter_id:
            query = query.where(QuizAttempt.chapter_id == chapter_id)

        query = query.order_by(desc(QuizAttempt.created_at)).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create_bookmark(
        self,
        user_id: uuid.UUID,
        chapter_id: str,
        section_heading: Optional[str] = None,
        note: Optional[str] = None,
        highlighted_text: Optional[str] = None
    ) -> UserBookmark:
        """
        Create a bookmark for a chapter section.

        Args:
            user_id: User UUID
            chapter_id: Chapter identifier
            section_heading: Section heading
            note: Optional user note
            highlighted_text: Optional highlighted text

        Returns:
            Created bookmark
        """
        bookmark = UserBookmark(
            user_id=user_id,
            chapter_id=chapter_id,
            section_heading=section_heading,
            note=note,
            highlighted_text=highlighted_text
        )

        self.db.add(bookmark)
        await self.db.commit()
        await self.db.refresh(bookmark)

        return bookmark

    async def get_user_bookmarks(
        self,
        user_id: uuid.UUID,
        chapter_id: Optional[str] = None
    ) -> List[UserBookmark]:
        """
        Get all bookmarks for a user.

        Args:
            user_id: User UUID
            chapter_id: Optional chapter filter

        Returns:
            List of UserBookmark records
        """
        query = select(UserBookmark).where(
            UserBookmark.user_id == user_id
        )

        if chapter_id:
            query = query.where(UserBookmark.chapter_id == chapter_id)

        query = query.order_by(desc(UserBookmark.created_at))

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def delete_bookmark(
        self,
        bookmark_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> bool:
        """
        Delete a bookmark.

        Args:
            bookmark_id: Bookmark UUID
            user_id: User UUID (for authorization)

        Returns:
            True if deleted, False if not found
        """
        query = select(UserBookmark).where(
            and_(
                UserBookmark.id == bookmark_id,
                UserBookmark.user_id == user_id
            )
        )
        result = await self.db.execute(query)
        bookmark = result.scalar_one_or_none()

        if not bookmark:
            return False

        await self.db.delete(bookmark)
        await self.db.commit()

        return True

    async def get_completion_stats(
        self,
        user_id: uuid.UUID
    ) -> dict:
        """
        Get completion statistics for a user.

        Args:
            user_id: User UUID

        Returns:
            Dictionary with stats (completed_chapters, total_time, avg_quiz_score)
        """
        all_progress = await self.get_all_user_progress(user_id)

        completed_count = sum(1 for p in all_progress if p.is_completed)
        total_time = sum(p.time_spent_minutes for p in all_progress)

        quiz_scores = [p.best_quiz_score for p in all_progress if p.best_quiz_score is not None]
        avg_quiz_score = sum(quiz_scores) / len(quiz_scores) if quiz_scores else None

        return {
            "completed_chapters": completed_count,
            "total_chapters_accessed": len(all_progress),
            "total_time_minutes": total_time,
            "average_quiz_score": avg_quiz_score
        }
