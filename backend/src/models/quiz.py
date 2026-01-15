"""Quiz models for knowledge assessment."""

import uuid
from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Boolean, Float, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from src.db.connection import Base


# Enums
class QuestionType(str, Enum):
    """Type of quiz question."""
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    CODE_COMPLETION = "code_completion"


class Difficulty(str, Enum):
    """Question difficulty level."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


# SQLAlchemy Models (Database)
class Quiz(Base):
    """
    Quiz for a chapter.

    Attributes:
        id: Unique quiz identifier
        chapter_id: Associated chapter
        title: Quiz title
        instructions: Instructions for quiz takers
        passing_score: Minimum percentage to pass
        created_at: Quiz creation timestamp
    """
    __tablename__ = "quizzes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chapter_id = Column(String(100), nullable=False, unique=True, index=True)
    title = Column(String(255), nullable=False)
    instructions = Column(String(1000), nullable=True)
    passing_score = Column(Float, default=70.0, nullable=False)  # Percentage
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    # Relationships
    questions = relationship("QuizQuestion", back_populates="quiz", cascade="all, delete-orphan", order_by="QuizQuestion.order_index")
    attempts = relationship("QuizAttempt", back_populates="quiz", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Quiz(id={self.id}, chapter={self.chapter_id}, questions={len(self.questions)})>"


class QuizQuestion(Base):
    """
    Individual question in a quiz.

    Attributes:
        id: Unique question identifier
        quiz_id: Foreign key to quiz
        order_index: Question order in quiz
        question_text: Question prompt
        question_type: Type of question
        options: JSONB array of answer options
        correct_answer: Correct answer text
        explanation: Explanation of correct answer
        difficulty: Question difficulty level
        points: Points awarded for correct answer
    """
    __tablename__ = "quiz_questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quiz_id = Column(UUID(as_uuid=True), ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False)
    order_index = Column(Integer, nullable=False)
    question_text = Column(String(1000), nullable=False)
    question_type = Column(SQLEnum(QuestionType), nullable=False)
    options = Column(JSONB, nullable=True)  # Array of option strings
    correct_answer = Column(String(500), nullable=False)
    explanation = Column(String(2000), nullable=True)
    difficulty = Column(SQLEnum(Difficulty), default=Difficulty.INTERMEDIATE, nullable=False)
    points = Column(Integer, default=1, nullable=False)

    # Relationships
    quiz = relationship("Quiz", back_populates="questions")
    responses = relationship("QuizResponse", back_populates="question")

    def __repr__(self):
        return f"<QuizQuestion(id={self.id}, type={self.question_type}, difficulty={self.difficulty})>"


class QuizAttempt(Base):
    """
    User's quiz attempt.

    Attributes:
        id: Unique attempt identifier
        user_id: Foreign key to users table
        quiz_id: Foreign key to quiz
        score: Percentage score achieved
        points_earned: Total points earned
        total_points: Total points possible
        passed: Whether attempt passed
        started_at: Attempt start timestamp
        completed_at: Attempt completion timestamp
    """
    __tablename__ = "quiz_attempts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    quiz_id = Column(UUID(as_uuid=True), ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False)
    score = Column(Float, nullable=True)  # Percentage
    points_earned = Column(Integer, default=0, nullable=False)
    total_points = Column(Integer, nullable=False)
    passed = Column(Boolean, default=False, nullable=False)
    started_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    quiz = relationship("Quiz", back_populates="attempts")
    responses = relationship("QuizResponse", back_populates="attempt", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<QuizAttempt(id={self.id}, score={self.score}%, passed={self.passed})>"


class QuizResponse(Base):
    """
    User's response to a quiz question.

    Attributes:
        id: Unique response identifier
        attempt_id: Foreign key to quiz attempt
        question_id: Foreign key to question
        user_answer: User's submitted answer
        is_correct: Whether answer was correct
        points_awarded: Points earned for this question
        answered_at: Response timestamp
    """
    __tablename__ = "quiz_responses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    attempt_id = Column(UUID(as_uuid=True), ForeignKey("quiz_attempts.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(UUID(as_uuid=True), ForeignKey("quiz_questions.id", ondelete="CASCADE"), nullable=False)
    user_answer = Column(String(500), nullable=False)
    is_correct = Column(Boolean, nullable=False)
    points_awarded = Column(Integer, default=0, nullable=False)
    answered_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    # Relationships
    attempt = relationship("QuizAttempt", back_populates="responses")
    question = relationship("QuizQuestion", back_populates="responses")

    def __repr__(self):
        return f"<QuizResponse(id={self.id}, correct={self.is_correct})>"


# Pydantic Models (API)
class QuestionOption(BaseModel):
    """Quiz question option."""
    text: str
    is_correct: bool


class QuizQuestionResponse(BaseModel):
    """Question response for API."""
    id: str
    order_index: int
    question_text: str
    question_type: QuestionType
    options: Optional[List[str]] = None
    difficulty: Difficulty
    points: int

    class Config:
        from_attributes = True


class QuizDetailResponse(BaseModel):
    """Detailed quiz response."""
    id: str
    chapter_id: str
    title: str
    instructions: Optional[str]
    passing_score: float
    questions: List[QuizQuestionResponse]

    class Config:
        from_attributes = True


class SubmitQuizRequest(BaseModel):
    """Request to submit quiz answers."""
    attempt_id: str = Field(..., description="Quiz attempt ID")
    answers: List["QuizAnswerSubmission"] = Field(..., description="User's answers")


class QuizAnswerSubmission(BaseModel):
    """Single answer submission."""
    question_id: str
    user_answer: str


class QuizResultResponse(BaseModel):
    """Quiz result after submission."""
    attempt_id: str
    score: float
    points_earned: int
    total_points: int
    passed: bool
    results: List["QuestionResult"]


class QuestionResult(BaseModel):
    """Individual question result."""
    question_id: str
    question_text: str
    user_answer: str
    correct_answer: str
    is_correct: bool
    points_awarded: int
    explanation: Optional[str]


class QuizAttemptSummary(BaseModel):
    """Summary of quiz attempts."""
    chapter_id: str
    total_attempts: int
    best_score: Optional[float]
    passed: bool
    last_attempt_date: Optional[datetime]

    class Config:
        from_attributes = True


# Update forward references
SubmitQuizRequest.model_rebuild()
QuizResultResponse.model_rebuild()
