"""Chat conversation and message models for RAG chatbot."""

import uuid
from datetime import datetime
from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Integer, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from src.db.connection import Base


# Enums
class Language(str, Enum):
    """Supported languages for chatbot."""
    ENGLISH = "en"
    URDU = "ur"


class MessageRole(str, Enum):
    """Role of message sender."""
    USER = "user"
    ASSISTANT = "assistant"


# SQLAlchemy Models (Database)
class ChatConversation(Base):
    """
    Chat conversation grouping messages for context retention.

    Attributes:
        id: Unique conversation identifier
        user_id: Foreign key to users table (nullable for anonymous)
        language: Conversation language (en or ur)
        created_at: Conversation start timestamp
        updated_at: Last message timestamp
    """
    __tablename__ = "chat_conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=True)  # No FK constraint for demo - users table not implemented yet
    language = Column(SQLEnum(Language), default=Language.ENGLISH, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    messages = relationship("ChatMessage", back_populates="conversation", cascade="all, delete-orphan", order_by="ChatMessage.created_at")

    def __repr__(self):
        return f"<ChatConversation(id={self.id}, language={self.language}, messages={len(self.messages)})>"


class ChatMessage(Base):
    """
    Individual message within a conversation.

    Attributes:
        id: Unique message identifier
        conversation_id: Foreign key to conversation
        role: Message sender (user or assistant)
        message: Message text content
        citations: JSONB array of source references
        tokens_used: Token count for cost tracking
        created_at: Message timestamp
    """
    __tablename__ = "chat_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("chat_conversations.id", ondelete="CASCADE"), nullable=False)
    role = Column(SQLEnum(MessageRole), nullable=False)
    message = Column(Text, nullable=False)
    citations = Column(JSONB, nullable=True)  # Array of {chapter_id, section, title}
    tokens_used = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    # Relationships
    conversation = relationship("ChatConversation", back_populates="messages")

    def __repr__(self):
        return f"<ChatMessage(id={self.id}, role={self.role}, conversation_id={self.conversation_id})>"


# Pydantic Models (API)
class Citation(BaseModel):
    """
    Source citation for chatbot response.

    Attributes:
        chapter_id: Chapter containing the source
        section: Section heading or number
        title: Chapter title for display
    """
    chapter_id: str = Field(..., max_length=100)
    section: str = Field(..., max_length=255)
    title: str = Field(..., max_length=255)

    class Config:
        json_schema_extra = {
            "example": {
                "chapter_id": "chapter-03-ros2-topics",
                "section": "2.1 Publisher-Subscriber Pattern",
                "title": "ROS 2 Topics"
            }
        }


class ChatMessageCreate(BaseModel):
    """Request to create a new chat message."""
    conversation_id: Optional[uuid.UUID] = Field(None, description="Existing conversation or null to start new")
    message: str = Field(..., min_length=1, max_length=2000)
    language: Language = Language.ENGLISH


class ChatMessageResponse(BaseModel):
    """Chatbot response with message and citations."""
    conversation_id: uuid.UUID
    message: str
    citations: List[Citation] = Field(default_factory=list)
    tokens_used: Optional[int] = None
    response_time_ms: Optional[int] = None

    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
                "message": "ROS 2 Topics enable asynchronous communication between nodes using a publish-subscribe pattern. Publishers send messages to topics without knowing who will receive them.",
                "citations": [
                    {
                        "chapter_id": "chapter-03-ros2-topics",
                        "section": "2.1 Publisher-Subscriber Pattern",
                        "title": "ROS 2 Topics"
                    }
                ],
                "tokens_used": 150,
                "response_time_ms": 1250
            }
        }


class ConversationHistoryResponse(BaseModel):
    """Conversation history with all messages."""
    conversation_id: uuid.UUID
    language: Language
    messages: List["MessageHistoryItem"]
    created_at: datetime
    updated_at: datetime


class MessageHistoryItem(BaseModel):
    """Individual message in conversation history."""
    id: uuid.UUID
    role: MessageRole
    message: str
    citations: Optional[List[Citation]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TextSelectionRequest(BaseModel):
    """Request for contextual explanation of selected text."""
    selected_text: str = Field(..., min_length=1, max_length=500)
    chapter_id: str = Field(..., max_length=100)
    surrounding_context: Optional[str] = Field(None, max_length=1000, description="Text before/after selection")
    language: Language = Language.ENGLISH


class TextSelectionResponse(BaseModel):
    """Contextual explanation response."""
    explanation: str
    citations: List[Citation] = Field(default_factory=list)
    response_time_ms: Optional[int] = None

    class Config:
        json_schema_extra = {
            "example": {
                "explanation": "URDF (Unified Robot Description Format) is an XML-based format used to describe robot kinematics, dynamics, and visual properties. It's essential for simulation in Gazebo and RViz.",
                "citations": [
                    {
                        "chapter_id": "chapter-06-gazebo-intro",
                        "section": "1.2 Robot Description",
                        "title": "Gazebo Simulation"
                    }
                ],
                "response_time_ms": 980
            }
        }


# Update forward references
ConversationHistoryResponse.model_rebuild()
