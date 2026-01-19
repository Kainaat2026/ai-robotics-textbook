"""User progress tracking model for chapter completion and quiz scores."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.db.connection import Base


class UserProgress(Base):
    """
    User progress model for tracking chapter completion and performance.

    Tracks:
    - Chapter completion status
    - Quiz scores and attempts
    - Time spent on chapters
    - Last access timestamps
    """

    __tablename__ = "user_progress"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    chapter_id = Column(String(100), nullable=False, index=True)

    # Completion tracking
    is_completed = Column(Boolean, default=False, nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Quiz performance
    quiz_score = Column(Float, nullable=True)  # Percentage (0-100)
    quiz_attempts = Column(Integer, default=0, nullable=False)
    best_quiz_score = Column(Float, nullable=True)  # Best score across attempts

    # Time tracking
    time_spent_minutes = Column(Integer, default=0, nullable=False)
    last_accessed_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="progress")

    def __repr__(self):
        return f"<UserProgress(user_id={self.user_id}, chapter={self.chapter_id}, completed={self.is_completed})>"


class QuizAttempt(Base):
    """
    Simple quiz attempt record for progress tracking.

    Tracks quiz attempts by chapter without linking to the full quiz system.
    Used by progress routes for basic score tracking.
    """

    __tablename__ = "chapter_quiz_attempts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    chapter_id = Column(String(100), nullable=False, index=True)

    # Score and performance
    score = Column(Float, nullable=False)  # Percentage (0-100)
    correct_answers = Column(Integer, nullable=False)
    total_questions = Column(Integer, nullable=False)
    time_taken_seconds = Column(Integer, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="quiz_attempts")

    def __repr__(self):
        return f"<QuizAttempt(user_id={self.user_id}, chapter={self.chapter_id}, score={self.score})>"


class UserBookmark(Base):
    """
    User bookmarks for saving important sections or passages.
    """

    __tablename__ = "user_bookmarks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    chapter_id = Column(String(100), nullable=False)
    section_heading = Column(String(255), nullable=True)

    # Bookmark content
    note = Column(String(500), nullable=True)  # Optional user note
    highlighted_text = Column(String(1000), nullable=True)  # Text they bookmarked

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="bookmarks")

    def __repr__(self):
        return f"<UserBookmark(user_id={self.user_id}, chapter={self.chapter_id})>"
