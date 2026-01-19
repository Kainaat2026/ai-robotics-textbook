"""Quiz repository for quiz data operations."""

import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import select, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.quiz import Quiz, QuizQuestion, QuizSession, QuizResponse


class QuizRepository:
    """Repository for quiz operations."""

    def __init__(self, db: AsyncSession):
        """
        Initialize repository with database session.

        Args:
            db: Async database session
        """
        self.db = db

    async def get_quiz_by_chapter(
        self,
        chapter_id: str,
        include_questions: bool = True
    ) -> Optional[Quiz]:
        """
        Get quiz for a specific chapter.

        Args:
            chapter_id: Chapter identifier
            include_questions: Whether to load questions

        Returns:
            Quiz or None
        """
        query = select(Quiz).where(Quiz.chapter_id == chapter_id)

        if include_questions:
            query = query.options(selectinload(Quiz.questions))

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_quiz_by_id(
        self,
        quiz_id: uuid.UUID,
        include_questions: bool = True
    ) -> Optional[Quiz]:
        """
        Get quiz by ID.

        Args:
            quiz_id: Quiz UUID
            include_questions: Whether to load questions

        Returns:
            Quiz or None
        """
        query = select(Quiz).where(Quiz.id == quiz_id)

        if include_questions:
            query = query.options(selectinload(Quiz.questions))

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_quiz_session(
        self,
        user_id: uuid.UUID,
        quiz_id: uuid.UUID,
        total_points: int
    ) -> QuizSession:
        """
        Create a new quiz session for a user.

        Args:
            user_id: User UUID
            quiz_id: Quiz UUID
            total_points: Total points possible

        Returns:
            Created QuizSession
        """
        session = QuizSession(
            user_id=user_id,
            quiz_id=quiz_id,
            total_points=total_points,
            started_at=datetime.utcnow()
        )

        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)

        return session

    async def get_quiz_session(
        self,
        session_id: uuid.UUID,
        user_id: Optional[uuid.UUID] = None
    ) -> Optional[QuizSession]:
        """
        Get a quiz session by ID.

        Args:
            session_id: Session UUID
            user_id: Optional user ID for authorization check

        Returns:
            QuizSession or None
        """
        query = select(QuizSession).where(QuizSession.id == session_id)

        if user_id:
            query = query.where(QuizSession.user_id == user_id)

        query = query.options(
            selectinload(QuizSession.responses),
            selectinload(QuizSession.quiz).selectinload(Quiz.questions)
        )

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def submit_quiz_responses(
        self,
        session_id: uuid.UUID,
        answers: List[dict]
    ) -> QuizSession:
        """
        Submit quiz responses and calculate score.

        Args:
            session_id: Session UUID
            answers: List of dicts with question_id and user_answer

        Returns:
            Updated QuizSession with score
        """
        # Get session with quiz and questions
        session = await self.get_quiz_session(session_id)
        if not session:
            raise ValueError(f"Quiz session {session_id} not found")

        # Build question lookup
        questions = {str(q.id): q for q in session.quiz.questions}

        # Process each answer
        points_earned = 0
        for answer in answers:
            question_id = answer["question_id"]
            user_answer = answer["user_answer"]

            question = questions.get(question_id)
            if not question:
                continue

            # Check if correct
            is_correct = user_answer.strip().lower() == question.correct_answer.strip().lower()
            points = question.points if is_correct else 0
            points_earned += points

            # Create response record
            response = QuizResponse(
                attempt_id=session_id,
                question_id=uuid.UUID(question_id),
                user_answer=user_answer,
                is_correct=is_correct,
                points_awarded=points
            )
            self.db.add(response)

        # Update session with results
        session.points_earned = points_earned
        session.score = (points_earned / session.total_points * 100) if session.total_points > 0 else 0
        session.passed = session.score >= session.quiz.passing_score
        session.completed_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(session)

        return session

    async def get_user_quiz_sessions(
        self,
        user_id: uuid.UUID,
        chapter_id: Optional[str] = None,
        limit: int = 10
    ) -> List[QuizSession]:
        """
        Get quiz sessions for a user.

        Args:
            user_id: User UUID
            chapter_id: Optional chapter filter
            limit: Maximum sessions to return

        Returns:
            List of QuizSession records
        """
        query = select(QuizSession).where(QuizSession.user_id == user_id)

        if chapter_id:
            # Join with Quiz to filter by chapter
            query = query.join(Quiz).where(Quiz.chapter_id == chapter_id)

        query = query.options(
            selectinload(QuizSession.quiz)
        ).order_by(desc(QuizSession.started_at)).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_quiz_summary_for_chapter(
        self,
        user_id: uuid.UUID,
        chapter_id: str
    ) -> dict:
        """
        Get quiz summary for a user on a specific chapter.

        Args:
            user_id: User UUID
            chapter_id: Chapter identifier

        Returns:
            Summary dict with attempts, best score, passed status
        """
        sessions = await self.get_user_quiz_sessions(user_id, chapter_id, limit=100)

        if not sessions:
            return {
                "chapter_id": chapter_id,
                "total_attempts": 0,
                "best_score": None,
                "passed": False,
                "last_attempt_date": None
            }

        best_score = max(s.score for s in sessions if s.score is not None) if sessions else None
        passed = any(s.passed for s in sessions)
        last_attempt = sessions[0].started_at if sessions else None

        return {
            "chapter_id": chapter_id,
            "total_attempts": len(sessions),
            "best_score": best_score,
            "passed": passed,
            "last_attempt_date": last_attempt
        }

    async def get_all_available_quizzes(self) -> List[Quiz]:
        """
        Get all available quizzes.

        Returns:
            List of Quiz records with questions loaded
        """
        query = select(Quiz).options(selectinload(Quiz.questions)).order_by(Quiz.chapter_id)
        result = await self.db.execute(query)
        return list(result.scalars().all())
