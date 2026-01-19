"""Quiz API endpoints."""

import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.connection import get_db
from src.db.repositories.quiz_repo import QuizRepository
from src.models.quiz import (
    QuizDetailResponse,
    QuizQuestionResponse,
    SubmitQuizRequest,
    QuizResultResponse,
    QuestionResult,
    QuizAttemptSummary,
    Difficulty
)
from src.models.user import User
from src.services.quiz_service import quiz_service
from src.utils.auth_dependencies import get_current_user, get_current_user_optional

router = APIRouter()


# Pydantic models for API
from pydantic import BaseModel, Field
from datetime import datetime


class StartQuizResponse(BaseModel):
    """Response when starting a quiz."""
    session_id: str
    quiz_id: str
    chapter_id: str
    title: str
    instructions: Optional[str]
    passing_score: float
    total_questions: int
    total_points: int
    questions: List[QuizQuestionResponse]


class QuizListItem(BaseModel):
    """Quiz list item for available quizzes."""
    id: str
    chapter_id: str
    title: str
    passing_score: float
    question_count: int


class UserQuizAttempt(BaseModel):
    """User's quiz attempt record."""
    session_id: str
    quiz_id: str
    chapter_id: str
    score: Optional[float]
    points_earned: int
    total_points: int
    passed: bool
    started_at: datetime
    completed_at: Optional[datetime]


@router.get("/quiz", response_model=List[QuizListItem])
async def list_available_quizzes(
    db: AsyncSession = Depends(get_db)
) -> List[QuizListItem]:
    """
    List all available quizzes.

    Returns:
        List of available quizzes with metadata

    Example:
        GET /api/quiz
    """
    quiz_repo = QuizRepository(db)
    quizzes = await quiz_repo.get_all_available_quizzes()

    return [
        QuizListItem(
            id=str(q.id),
            chapter_id=q.chapter_id,
            title=q.title,
            passing_score=q.passing_score,
            question_count=len(q.questions) if q.questions else 0
        )
        for q in quizzes
    ]


@router.get("/quiz/{chapter_id}", response_model=QuizDetailResponse)
async def get_quiz_for_chapter(
    chapter_id: str,
    db: AsyncSession = Depends(get_db)
) -> QuizDetailResponse:
    """
    Get quiz details for a chapter (without starting a session).

    Args:
        chapter_id: Chapter identifier

    Returns:
        Quiz with questions (answers hidden)

    Example:
        GET /api/quiz/chapter-01-introduction
    """
    quiz_repo = QuizRepository(db)
    quiz = await quiz_repo.get_quiz_by_chapter(chapter_id, include_questions=True)

    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No quiz found for chapter {chapter_id}"
        )

    # Convert questions (hide correct answers)
    questions = [
        QuizQuestionResponse(
            id=str(q.id),
            order_index=q.order_index,
            question_text=q.question_text,
            question_type=q.question_type,
            options=q.options,
            difficulty=q.difficulty,
            points=q.points
        )
        for q in sorted(quiz.questions, key=lambda x: x.order_index)
    ]

    return QuizDetailResponse(
        id=str(quiz.id),
        chapter_id=quiz.chapter_id,
        title=quiz.title,
        instructions=quiz.instructions,
        passing_score=quiz.passing_score,
        questions=questions
    )


@router.post("/quiz/{chapter_id}/start", response_model=StartQuizResponse)
async def start_quiz(
    chapter_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> StartQuizResponse:
    """
    Start a quiz session for a chapter.

    Requires: Authentication

    Args:
        chapter_id: Chapter identifier

    Returns:
        Quiz session with questions

    Example:
        POST /api/quiz/chapter-01-introduction/start
        Authorization: Bearer <token>
    """
    quiz_repo = QuizRepository(db)
    quiz = await quiz_repo.get_quiz_by_chapter(chapter_id, include_questions=True)

    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No quiz found for chapter {chapter_id}"
        )

    # Calculate total points
    total_points = sum(q.points for q in quiz.questions)

    # Create session
    session = await quiz_repo.create_quiz_session(
        user_id=current_user.id,
        quiz_id=quiz.id,
        total_points=total_points
    )

    # Prepare questions (optionally filter by user skill level)
    questions_data = quiz.questions
    if hasattr(current_user, 'profile') and current_user.profile:
        skill_level = current_user.profile.skill_level
        if skill_level:
            # Convert to dict format for filtering
            questions_dict = [
                {"difficulty": q.difficulty.value, **{attr: getattr(q, attr) for attr in ['id', 'order_index', 'question_text', 'question_type', 'options', 'points']}}
                for q in questions_data
            ]
            filtered = quiz_service.adjust_difficulty_for_user(questions_dict, skill_level)
            # Map back to question objects
            filtered_ids = {q.get('id') for q in filtered}
            questions_data = [q for q in quiz.questions if q.id in filtered_ids] or quiz.questions

    # Convert questions for response
    questions = [
        QuizQuestionResponse(
            id=str(q.id),
            order_index=q.order_index,
            question_text=q.question_text,
            question_type=q.question_type,
            options=q.options,
            difficulty=q.difficulty,
            points=q.points
        )
        for q in sorted(questions_data, key=lambda x: x.order_index)
    ]

    return StartQuizResponse(
        session_id=str(session.id),
        quiz_id=str(quiz.id),
        chapter_id=quiz.chapter_id,
        title=quiz.title,
        instructions=quiz.instructions,
        passing_score=quiz.passing_score,
        total_questions=len(questions),
        total_points=total_points,
        questions=questions
    )


@router.post("/quiz/submit", response_model=QuizResultResponse)
async def submit_quiz(
    request: SubmitQuizRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> QuizResultResponse:
    """
    Submit quiz answers and get results.

    Requires: Authentication

    Args:
        request: Quiz submission with session ID and answers

    Returns:
        Quiz results with score and detailed feedback

    Example:
        POST /api/quiz/submit
        Authorization: Bearer <token>
        {
            "attempt_id": "session-uuid",
            "answers": [
                {"question_id": "q1-uuid", "user_answer": "Option A"},
                {"question_id": "q2-uuid", "user_answer": "True"}
            ]
        }
    """
    quiz_repo = QuizRepository(db)

    # Get session and verify ownership
    session = await quiz_repo.get_quiz_session(
        session_id=uuid.UUID(request.attempt_id),
        user_id=current_user.id
    )

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz session not found or unauthorized"
        )

    if session.completed_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quiz session already completed"
        )

    # Convert answers to expected format
    answers = [
        {"question_id": a.question_id, "user_answer": a.user_answer}
        for a in request.answers
    ]

    # Submit and calculate score
    completed_session = await quiz_repo.submit_quiz_responses(
        session_id=session.id,
        answers=answers
    )

    # Build question results
    questions_lookup = {str(q.id): q for q in session.quiz.questions}
    responses_lookup = {str(r.question_id): r for r in completed_session.responses}

    results = []
    for q_id, question in questions_lookup.items():
        response = responses_lookup.get(q_id)
        results.append(
            QuestionResult(
                question_id=q_id,
                question_text=question.question_text,
                user_answer=response.user_answer if response else "",
                correct_answer=question.correct_answer,
                is_correct=response.is_correct if response else False,
                points_awarded=response.points_awarded if response else 0,
                explanation=question.explanation
            )
        )

    return QuizResultResponse(
        attempt_id=str(completed_session.id),
        score=completed_session.score or 0,
        points_earned=completed_session.points_earned,
        total_points=completed_session.total_points,
        passed=completed_session.passed,
        results=results
    )


@router.get("/quiz/history", response_model=List[UserQuizAttempt])
async def get_quiz_history(
    chapter_id: Optional[str] = None,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[UserQuizAttempt]:
    """
    Get user's quiz attempt history.

    Requires: Authentication

    Args:
        chapter_id: Optional chapter filter
        limit: Maximum attempts to return (default 10)

    Returns:
        List of quiz attempts

    Example:
        GET /api/quiz/history?chapter_id=chapter-01-introduction&limit=5
        Authorization: Bearer <token>
    """
    quiz_repo = QuizRepository(db)

    sessions = await quiz_repo.get_user_quiz_sessions(
        user_id=current_user.id,
        chapter_id=chapter_id,
        limit=limit
    )

    return [
        UserQuizAttempt(
            session_id=str(s.id),
            quiz_id=str(s.quiz_id),
            chapter_id=s.quiz.chapter_id if s.quiz else "",
            score=s.score,
            points_earned=s.points_earned,
            total_points=s.total_points,
            passed=s.passed,
            started_at=s.started_at,
            completed_at=s.completed_at
        )
        for s in sessions
    ]


@router.get("/quiz/summary/{chapter_id}", response_model=QuizAttemptSummary)
async def get_quiz_summary(
    chapter_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> QuizAttemptSummary:
    """
    Get quiz summary for a specific chapter.

    Requires: Authentication

    Args:
        chapter_id: Chapter identifier

    Returns:
        Summary with attempts, best score, pass status

    Example:
        GET /api/quiz/summary/chapter-01-introduction
        Authorization: Bearer <token>
    """
    quiz_repo = QuizRepository(db)

    summary = await quiz_repo.get_quiz_summary_for_chapter(
        user_id=current_user.id,
        chapter_id=chapter_id
    )

    return QuizAttemptSummary(
        chapter_id=summary["chapter_id"],
        total_attempts=summary["total_attempts"],
        best_score=summary["best_score"],
        passed=summary["passed"],
        last_attempt_date=summary["last_attempt_date"]
    )


@router.get("/quiz/results/{session_id}", response_model=QuizResultResponse)
async def get_quiz_results(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> QuizResultResponse:
    """
    Get detailed results for a completed quiz session.

    Requires: Authentication

    Args:
        session_id: Quiz session UUID

    Returns:
        Detailed quiz results

    Example:
        GET /api/quiz/results/session-uuid
        Authorization: Bearer <token>
    """
    quiz_repo = QuizRepository(db)

    session = await quiz_repo.get_quiz_session(
        session_id=uuid.UUID(session_id),
        user_id=current_user.id
    )

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz session not found or unauthorized"
        )

    if not session.completed_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quiz session not yet completed"
        )

    # Build question results
    questions_lookup = {str(q.id): q for q in session.quiz.questions}
    responses_lookup = {str(r.question_id): r for r in session.responses}

    results = []
    for q_id, question in questions_lookup.items():
        response = responses_lookup.get(q_id)
        results.append(
            QuestionResult(
                question_id=q_id,
                question_text=question.question_text,
                user_answer=response.user_answer if response else "",
                correct_answer=question.correct_answer,
                is_correct=response.is_correct if response else False,
                points_awarded=response.points_awarded if response else 0,
                explanation=question.explanation
            )
        )

    return QuizResultResponse(
        attempt_id=str(session.id),
        score=session.score or 0,
        points_earned=session.points_earned,
        total_points=session.total_points,
        passed=session.passed,
        results=results
    )
