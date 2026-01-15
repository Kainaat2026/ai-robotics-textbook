"""Progress tracking API models (Pydantic schemas)."""

import uuid
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


# Request models
class UpdateProgressRequest(BaseModel):
    """Update chapter progress request."""
    chapter_id: str = Field(..., max_length=100)
    time_spent_minutes: Optional[int] = Field(None, ge=0)
    is_completed: Optional[bool] = None


class QuizAttemptRequest(BaseModel):
    """Submit quiz attempt request."""
    chapter_id: str = Field(..., max_length=100)
    score: float = Field(..., ge=0, le=100)
    correct_answers: int = Field(..., ge=0)
    total_questions: int = Field(..., ge=1)
    time_taken_seconds: int = Field(..., ge=0)


class CreateBookmarkRequest(BaseModel):
    """Create bookmark request."""
    chapter_id: str = Field(..., max_length=100)
    section_heading: Optional[str] = Field(None, max_length=255)
    note: Optional[str] = Field(None, max_length=500)
    highlighted_text: Optional[str] = Field(None, max_length=1000)


# Response models
class ProgressResponse(BaseModel):
    """Chapter progress response."""
    id: uuid.UUID
    chapter_id: str
    is_completed: bool
    completed_at: Optional[datetime]
    quiz_score: Optional[float]
    quiz_attempts: int
    best_quiz_score: Optional[float]
    time_spent_minutes: int
    last_accessed_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "chapter_id": "chapter-01-introduction",
                "is_completed": True,
                "completed_at": "2024-01-15T14:30:00Z",
                "quiz_score": 85.5,
                "quiz_attempts": 2,
                "best_quiz_score": 90.0,
                "time_spent_minutes": 45,
                "last_accessed_at": "2024-01-15T15:00:00Z"
            }
        }


class QuizAttemptResponse(BaseModel):
    """Quiz attempt response."""
    id: uuid.UUID
    chapter_id: str
    score: float
    correct_answers: int
    total_questions: int
    time_taken_seconds: int
    created_at: datetime

    class Config:
        from_attributes = True


class BookmarkResponse(BaseModel):
    """Bookmark response."""
    id: uuid.UUID
    chapter_id: str
    section_heading: Optional[str]
    note: Optional[str]
    highlighted_text: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class CompletionStatsResponse(BaseModel):
    """User completion statistics response."""
    completed_chapters: int
    total_chapters_accessed: int
    total_time_minutes: int
    average_quiz_score: Optional[float]

    class Config:
        json_schema_extra = {
            "example": {
                "completed_chapters": 5,
                "total_chapters_accessed": 8,
                "total_time_minutes": 240,
                "average_quiz_score": 87.5
            }
        }


class UserProgressSummaryResponse(BaseModel):
    """Complete user progress summary."""
    stats: CompletionStatsResponse
    progress: List[ProgressResponse]
    recent_quiz_attempts: List[QuizAttemptResponse]
