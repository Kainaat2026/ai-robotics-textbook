"""User model for authentication and profile management."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.db.connection import Base


class User(Base):
    """
    User model for authentication.

    Attributes:
        id: Unique user identifier (UUID)
        email: User email address (unique)
        password_hash: Hashed password using bcrypt
        created_at: Account creation timestamp
        updated_at: Last update timestamp
        is_active: Account active status
        is_verified: Email verification status
    """

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    progress = relationship("UserProgress", back_populates="user", cascade="all, delete-orphan")
    # conversations = relationship("ChatConversation", back_populates="user", cascade="all, delete-orphan")  # Disabled for demo - ChatConversation has no FK to users
    quiz_attempts = relationship("QuizAttempt", back_populates="user", cascade="all, delete-orphan")
    bookmarks = relationship("UserBookmark", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"
