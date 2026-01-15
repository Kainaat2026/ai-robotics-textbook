"""User progress tracking API endpoints."""

import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.connection import get_db
from src.db.repositories.progress_repo import ProgressRepository
from src.models.progress import (
    UpdateProgressRequest,
    QuizAttemptRequest,
    CreateBookmarkRequest,
    ProgressResponse,
    QuizAttemptResponse,
    BookmarkResponse,
    CompletionStatsResponse,
    UserProgressSummaryResponse
)
from src.models.user import User
from src.utils.auth_dependencies import get_current_user

router = APIRouter()


@router.get("/progress", response_model=List[ProgressResponse])
async def get_all_progress(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[ProgressResponse]:
    """
    Get all progress records for current user.

    Requires: Authentication

    Returns:
        List of progress records

    Example:
        GET /api/progress
        Authorization: Bearer <token>
    """
    progress_repo = ProgressRepository(db)
    progress_records = await progress_repo.get_all_user_progress(current_user.id)

    return [ProgressResponse.model_validate(p) for p in progress_records]


@router.get("/progress/{chapter_id}", response_model=ProgressResponse)
async def get_chapter_progress(
    chapter_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> ProgressResponse:
    """
    Get progress for a specific chapter.

    Requires: Authentication

    Args:
        chapter_id: Chapter identifier

    Returns:
        Progress record

    Example:
        GET /api/progress/chapter-01-introduction
    """
    progress_repo = ProgressRepository(db)
    progress = await progress_repo.get_user_progress(current_user.id, chapter_id)

    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No progress found for chapter {chapter_id}"
        )

    return ProgressResponse.model_validate(progress)


@router.post("/progress", response_model=ProgressResponse, status_code=status.HTTP_201_CREATED)
async def update_progress(
    request: UpdateProgressRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> ProgressResponse:
    """
    Update chapter progress (time spent, completion status).

    Requires: Authentication

    Args:
        request: Progress update data

    Returns:
        Updated progress record

    Example:
        POST /api/progress
        {
            "chapter_id": "chapter-01-introduction",
            "time_spent_minutes": 15,
            "is_completed": true
        }
    """
    progress_repo = ProgressRepository(db)

    updates = {}
    if request.time_spent_minutes is not None:
        # Add time to existing time
        progress = await progress_repo.update_time_spent(
            current_user.id,
            request.chapter_id,
            request.time_spent_minutes
        )
    elif request.is_completed is not None and request.is_completed:
        # Mark as complete
        progress = await progress_repo.mark_chapter_complete(
            current_user.id,
            request.chapter_id
        )
    else:
        # Just update last accessed
        progress = await progress_repo.create_or_update_progress(
            current_user.id,
            request.chapter_id
        )

    return ProgressResponse.model_validate(progress)


@router.post("/progress/quiz", response_model=QuizAttemptResponse, status_code=status.HTTP_201_CREATED)
async def submit_quiz_attempt(
    request: QuizAttemptRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> QuizAttemptResponse:
    """
    Submit a quiz attempt.

    Requires: Authentication

    Args:
        request: Quiz attempt data

    Returns:
        Created quiz attempt record

    Example:
        POST /api/progress/quiz
        {
            "chapter_id": "chapter-01-introduction",
            "score": 85.5,
            "correct_answers": 17,
            "total_questions": 20,
            "time_taken_seconds": 180
        }
    """
    progress_repo = ProgressRepository(db)

    attempt = await progress_repo.record_quiz_attempt(
        user_id=current_user.id,
        chapter_id=request.chapter_id,
        score=request.score,
        correct_answers=request.correct_answers,
        total_questions=request.total_questions,
        time_taken_seconds=request.time_taken_seconds
    )

    return QuizAttemptResponse.model_validate(attempt)


@router.get("/progress/quiz/history", response_model=List[QuizAttemptResponse])
async def get_quiz_history(
    chapter_id: str = None,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[QuizAttemptResponse]:
    """
    Get quiz attempt history.

    Requires: Authentication

    Args:
        chapter_id: Optional chapter filter
        limit: Maximum number of attempts (default 10)

    Returns:
        List of quiz attempts

    Example:
        GET /api/progress/quiz/history?chapter_id=chapter-01-introduction&limit=5
    """
    progress_repo = ProgressRepository(db)

    attempts = await progress_repo.get_quiz_attempts(
        user_id=current_user.id,
        chapter_id=chapter_id,
        limit=limit
    )

    return [QuizAttemptResponse.model_validate(a) for a in attempts]


@router.get("/progress/stats", response_model=CompletionStatsResponse)
async def get_completion_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> CompletionStatsResponse:
    """
    Get user completion statistics.

    Requires: Authentication

    Returns:
        Completion stats (chapters completed, time spent, avg score)

    Example:
        GET /api/progress/stats
    """
    progress_repo = ProgressRepository(db)

    stats = await progress_repo.get_completion_stats(current_user.id)

    return CompletionStatsResponse(**stats)


@router.get("/progress/summary", response_model=UserProgressSummaryResponse)
async def get_progress_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> UserProgressSummaryResponse:
    """
    Get complete user progress summary.

    Requires: Authentication

    Returns:
        Complete summary with stats, progress, and recent quiz attempts

    Example:
        GET /api/progress/summary
    """
    progress_repo = ProgressRepository(db)

    # Get stats
    stats = await progress_repo.get_completion_stats(current_user.id)

    # Get all progress
    progress_records = await progress_repo.get_all_user_progress(current_user.id)

    # Get recent quiz attempts
    quiz_attempts = await progress_repo.get_quiz_attempts(
        user_id=current_user.id,
        limit=5
    )

    return UserProgressSummaryResponse(
        stats=CompletionStatsResponse(**stats),
        progress=[ProgressResponse.model_validate(p) for p in progress_records],
        recent_quiz_attempts=[QuizAttemptResponse.model_validate(a) for a in quiz_attempts]
    )


@router.post("/bookmarks", response_model=BookmarkResponse, status_code=status.HTTP_201_CREATED)
async def create_bookmark(
    request: CreateBookmarkRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> BookmarkResponse:
    """
    Create a bookmark for a chapter section.

    Requires: Authentication

    Args:
        request: Bookmark data

    Returns:
        Created bookmark

    Example:
        POST /api/bookmarks
        {
            "chapter_id": "chapter-01-introduction",
            "section_heading": "What is Physical AI?",
            "note": "Important concept to review",
            "highlighted_text": "Physical AI represents the next frontier..."
        }
    """
    progress_repo = ProgressRepository(db)

    bookmark = await progress_repo.create_bookmark(
        user_id=current_user.id,
        chapter_id=request.chapter_id,
        section_heading=request.section_heading,
        note=request.note,
        highlighted_text=request.highlighted_text
    )

    return BookmarkResponse.model_validate(bookmark)


@router.get("/bookmarks", response_model=List[BookmarkResponse])
async def get_bookmarks(
    chapter_id: str = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[BookmarkResponse]:
    """
    Get all bookmarks for current user.

    Requires: Authentication

    Args:
        chapter_id: Optional chapter filter

    Returns:
        List of bookmarks

    Example:
        GET /api/bookmarks?chapter_id=chapter-01-introduction
    """
    progress_repo = ProgressRepository(db)

    bookmarks = await progress_repo.get_user_bookmarks(
        user_id=current_user.id,
        chapter_id=chapter_id
    )

    return [BookmarkResponse.model_validate(b) for b in bookmarks]


@router.delete("/bookmarks/{bookmark_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bookmark(
    bookmark_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a bookmark.

    Requires: Authentication

    Args:
        bookmark_id: Bookmark UUID

    Returns:
        204 No Content

    Example:
        DELETE /api/bookmarks/123e4567-e89b-12d3-a456-426614174000
    """
    progress_repo = ProgressRepository(db)

    deleted = await progress_repo.delete_bookmark(bookmark_id, current_user.id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bookmark not found"
        )
