# Data Model

**Feature**: AI-Powered Physical AI & Humanoid Robotics Textbook
**Branch**: `001-docusaurus-textbook`
**Date**: 2026-01-09
**Phase**: Phase 1 - Data Model Design

## Overview

This document defines the data model for the AI-powered textbook platform, including entity schemas, relationships, indexes, and validation rules. The model supports user authentication, progress tracking, AI chatbot conversations, personalization, and content management.

**Database**: Neon Serverless Postgres (PostgreSQL 15+)
**ORM**: SQLAlchemy 2.0+ (async mode)
**Migrations**: Alembic

---

## Entity-Relationship Diagram

```
┌──────────────┐         ┌──────────────────┐
│    users     │1───────*│  user_profiles   │
└──────────────┘         └──────────────────┘
        │1
        │
        │*
┌──────────────────┐
│  user_progress   │
└──────────────────┘
        │*
        │
        │1
┌──────────────┐
│   chapters   │ (reference data, not DB table - stored in markdown)
└──────────────┘

┌──────────────┐         ┌──────────────────┐
│    users     │1───────*│ chat_conversations│
└──────────────┘         └──────────────────┘
                                 │1
                                 │
                                 │*
                         ┌──────────────────┐
                         │  chat_messages   │
                         └──────────────────┘

┌──────────────┐         ┌──────────────────┐
│    users     │1───────*│  user_bookmarks  │
└──────────────┘         └──────────────────┘

┌──────────────┐         ┌──────────────────┐
│   chapters   │1───────*│      quizzes     │
└──────────────┘         └──────────────────┘
                                 │1
                                 │
                                 │*
                         ┌──────────────────┐
                         │  quiz_questions  │
                         └──────────────────┘

┌──────────────┐         ┌──────────────────┐
│    users     │1───────*│  quiz_attempts   │
└──────────────┘         └──────────────────┘
        │                        │
        └────────*───────────────┘
                         ┌──────────────────┐
                         │  quiz_responses  │
                         └──────────────────┘
```

---

## Core Entities

### 1. users

Stores user authentication and account information.

**Table Name**: `users`

**Schema**:
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT valid_email CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$')
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_active ON users(is_active) WHERE is_active = TRUE;
```

**Pydantic Model**:
```python
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
import uuid

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)

class User(UserBase):
    id: uuid.UUID
    created_at: datetime
    last_login: Optional[datetime]
    is_active: bool

    class Config:
        from_attributes = True
```

**Business Rules**:
- Email must be unique and valid format
- Password minimum 8 characters (hashed with bcrypt, 10+ rounds)
- Soft delete: Set `is_deleted=TRUE`, `deleted_at=NOW()` for GDPR compliance
- Auto-generate UUID for ID (no sequential IDs exposed)

---

### 2. user_profiles

Stores user background information for personalization.

**Table Name**: `user_profiles`

**Schema**:
```sql
CREATE TYPE skill_level AS ENUM ('beginner', 'intermediate', 'advanced');

CREATE TABLE user_profiles (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    python_level skill_level DEFAULT 'intermediate',
    ai_experience skill_level DEFAULT 'beginner',
    robotics_experience skill_level DEFAULT 'beginner',
    has_rtx_gpu BOOLEAN DEFAULT FALSE,
    has_jetson BOOLEAN DEFAULT FALSE,
    has_robot BOOLEAN DEFAULT FALSE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_profiles_skill ON user_profiles(python_level, ai_experience, robotics_experience);
```

**Pydantic Model**:
```python
from enum import Enum

class SkillLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class UserProfileBase(BaseModel):
    python_level: SkillLevel = SkillLevel.INTERMEDIATE
    ai_experience: SkillLevel = SkillLevel.BEGINNER
    robotics_experience: SkillLevel = SkillLevel.BEGINNER
    has_rtx_gpu: bool = False
    has_jetson: bool = False
    has_robot: bool = False

class UserProfile(UserProfileBase):
    user_id: uuid.UUID
    updated_at: datetime

    class Config:
        from_attributes = True
```

**Business Rules**:
- Created during signup with questionnaire data
- One profile per user (1:1 relationship)
- Defaults to intermediate Python, beginner AI/robotics if not provided
- Used to determine personalization level (beginner vs advanced content)
- Hardware flags enable hardware-specific recommendations

---

### 3. user_progress

Tracks user progress through textbook chapters.

**Table Name**: `user_progress`

**Schema**:
```sql
CREATE TYPE progress_status AS ENUM ('not_started', 'in_progress', 'completed');

CREATE TABLE user_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    chapter_id VARCHAR(100) NOT NULL,  -- e.g., "chapter-03-ros2-topics"
    status progress_status DEFAULT 'not_started',
    quiz_score INTEGER CHECK (quiz_score >= 0 AND quiz_score <= 100),
    time_spent_seconds INTEGER DEFAULT 0,
    is_bookmarked BOOLEAN DEFAULT FALSE,
    last_accessed TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,

    UNIQUE(user_id, chapter_id)
);

CREATE INDEX idx_progress_user ON user_progress(user_id, last_accessed DESC);
CREATE INDEX idx_progress_chapter ON user_progress(chapter_id);
CREATE INDEX idx_progress_status ON user_progress(user_id, status);
```

**Pydantic Model**:
```python
class ProgressStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class UserProgressBase(BaseModel):
    chapter_id: str = Field(..., max_length=100)
    status: ProgressStatus = ProgressStatus.NOT_STARTED
    quiz_score: Optional[int] = Field(None, ge=0, le=100)
    time_spent_seconds: int = Field(0, ge=0)
    is_bookmarked: bool = False

class UserProgress(UserProgressBase):
    id: uuid.UUID
    user_id: uuid.UUID
    last_accessed: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True
```

**Business Rules**:
- One progress record per user per chapter
- `status` transitions: not_started → in_progress → completed
- `completed_at` set when status changes to completed
- `time_spent_seconds` incremented on each chapter view
- `quiz_score` nullable until user takes quiz
- Chapter IDs match markdown file slugs (e.g., "chapter-03-ros2-topics")

---

### 4. chat_conversations

Groups chat messages into conversations for context retention.

**Table Name**: `chat_conversations`

**Schema**:
```sql
CREATE TYPE language AS ENUM ('en', 'ur');

CREATE TABLE chat_conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,  -- Nullable for anonymous users
    language language DEFAULT 'en',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_conversations_user ON chat_conversations(user_id, updated_at DESC);
CREATE INDEX idx_conversations_recent ON chat_conversations(updated_at DESC) WHERE user_id IS NOT NULL;
```

**Pydantic Model**:
```python
class Language(str, Enum):
    ENGLISH = "en"
    URDU = "ur"

class ChatConversationBase(BaseModel):
    language: Language = Language.ENGLISH

class ChatConversation(ChatConversationBase):
    id: uuid.UUID
    user_id: Optional[uuid.UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

**Business Rules**:
- `user_id` nullable to support anonymous chatbot usage (pre-login)
- `language` determines chatbot response language
- `updated_at` reflects last message timestamp
- Conversations auto-archived after 24 hours of inactivity (soft delete or mark inactive)

---

### 5. chat_messages

Stores individual messages within conversations.

**Table Name**: `chat_messages`

**Schema**:
```sql
CREATE TYPE message_role AS ENUM ('user', 'assistant');

CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES chat_conversations(id) ON DELETE CASCADE,
    role message_role NOT NULL,
    message TEXT NOT NULL,
    citations JSONB,  -- Array of {chapter_id, section, title}
    tokens_used INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT message_not_empty CHECK (LENGTH(TRIM(message)) > 0)
);

CREATE INDEX idx_messages_conversation ON chat_messages(conversation_id, created_at ASC);
CREATE INDEX idx_messages_citations ON chat_messages USING GIN(citations) WHERE citations IS NOT NULL;
```

**Pydantic Model**:
```python
class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

class Citation(BaseModel):
    chapter_id: str
    section: str
    title: str

class ChatMessageBase(BaseModel):
    role: MessageRole
    message: str = Field(..., min_length=1, max_length=2000)
    citations: Optional[list[Citation]] = None

class ChatMessage(ChatMessageBase):
    id: uuid.UUID
    conversation_id: uuid.UUID
    tokens_used: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True
```

**Business Rules**:
- Messages ordered by `created_at` ASC (chronological)
- User messages have empty `citations`
- Assistant messages must include `citations` for sourced answers
- `tokens_used` for cost tracking (OpenAI API usage)
- Message truncated client-side to 2000 chars (enforced by Pydantic)
- JSONB `citations` enables efficient querying for which chapters are most referenced

---

### 6. user_bookmarks

Stores user-created bookmarks for quick navigation.

**Table Name**: `user_bookmarks`

**Schema**:
```sql
CREATE TABLE user_bookmarks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    chapter_id VARCHAR(100) NOT NULL,
    section_heading VARCHAR(255),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    UNIQUE(user_id, chapter_id, section_heading)
);

CREATE INDEX idx_bookmarks_user ON user_bookmarks(user_id, created_at DESC);
```

**Pydantic Model**:
```python
class UserBookmarkBase(BaseModel):
    chapter_id: str = Field(..., max_length=100)
    section_heading: Optional[str] = Field(None, max_length=255)
    notes: Optional[str] = Field(None, max_length=1000)

class UserBookmark(UserBookmarkBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True
```

**Business Rules**:
- Users can bookmark entire chapters or specific sections
- `section_heading` nullable for chapter-level bookmarks
- `notes` for user's personal annotations
- Unique constraint prevents duplicate bookmarks
- Displayed in user's progress dashboard

---

## Quiz System Entities

### 7. quizzes

Stores quiz metadata for each chapter (one quiz per chapter).

**Table Name**: `quizzes`

**Schema**:
```sql
CREATE TABLE quizzes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chapter_id VARCHAR(100) NOT NULL UNIQUE,
    title VARCHAR(255) NOT NULL,
    instructions TEXT,
    passing_score INTEGER DEFAULT 70 CHECK (passing_score >= 0 AND passing_score <= 100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_quizzes_chapter ON quizzes(chapter_id);
```

**Pydantic Model**:
```python
class QuizBase(BaseModel):
    chapter_id: str = Field(..., max_length=100)
    title: str = Field(..., max_length=255)
    instructions: Optional[str] = None
    passing_score: int = Field(70, ge=0, le=100)

class Quiz(QuizBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

**Business Rules**:
- One quiz per chapter (enforced by UNIQUE constraint on chapter_id)
- `passing_score` default 70% (customizable per chapter)
- Quizzes auto-generated via OpenAI GPT-4 based on chapter learning objectives
- `updated_at` reflects last regeneration timestamp

---

### 8. quiz_questions

Stores individual quiz questions (5-10 per quiz).

**Table Name**: `quiz_questions`

**Schema**:
```sql
CREATE TYPE question_type AS ENUM ('multiple_choice', 'true_false', 'code_completion');
CREATE TYPE difficulty_level AS ENUM ('beginner', 'intermediate', 'advanced');

CREATE TABLE quiz_questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    quiz_id UUID NOT NULL REFERENCES quizzes(id) ON DELETE CASCADE,
    question_text TEXT NOT NULL,
    question_type question_type NOT NULL,
    options JSONB,  -- Array of answer options for multiple_choice
    correct_answer TEXT NOT NULL,
    explanation TEXT NOT NULL,
    difficulty difficulty_level DEFAULT 'intermediate',
    section_reference VARCHAR(255),  -- Chapter section for review
    order_index INTEGER NOT NULL,

    CONSTRAINT valid_options CHECK (
        (question_type = 'multiple_choice' AND options IS NOT NULL) OR
        (question_type != 'multiple_choice' AND options IS NULL)
    )
);

CREATE INDEX idx_questions_quiz ON quiz_questions(quiz_id, order_index ASC);
CREATE INDEX idx_questions_difficulty ON quiz_questions(quiz_id, difficulty);
```

**Pydantic Model**:
```python
class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    CODE_COMPLETION = "code_completion"

class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class QuizQuestionBase(BaseModel):
    question_text: str = Field(..., min_length=10)
    question_type: QuestionType
    options: Optional[list[str]] = None
    correct_answer: str
    explanation: str
    difficulty: DifficultyLevel = DifficultyLevel.INTERMEDIATE
    section_reference: Optional[str] = Field(None, max_length=255)
    order_index: int = Field(..., ge=0)

class QuizQuestion(QuizQuestionBase):
    id: uuid.UUID
    quiz_id: uuid.UUID

    class Config:
        from_attributes = True
```

**Business Rules**:
- `options` required for multiple_choice, null otherwise (CHECK constraint)
- `correct_answer` format depends on `question_type`:
  - multiple_choice: option index (e.g., "0", "1", "2")
  - true_false: "true" or "false"
  - code_completion: expected code snippet
- `explanation` shown after user answers (always provided)
- `section_reference` links to chapter section for review (e.g., "2.1 ROS 2 Topics")
- `difficulty` aligns with user's skill level (beginner/advanced personalization)
- `order_index` determines question sequence (ASC)

---

### 9. quiz_attempts

Tracks user quiz attempts (allows retakes).

**Table Name**: `quiz_attempts`

**Schema**:
```sql
CREATE TABLE quiz_attempts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    quiz_id UUID NOT NULL REFERENCES quizzes(id) ON DELETE CASCADE,
    score INTEGER NOT NULL CHECK (score >= 0 AND score <= 100),
    passed BOOLEAN NOT NULL,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE NOT NULL,
    time_spent_seconds INTEGER
);

CREATE INDEX idx_attempts_user_quiz ON quiz_attempts(user_id, quiz_id, completed_at DESC);
CREATE INDEX idx_attempts_recent ON quiz_attempts(user_id, completed_at DESC);
```

**Pydantic Model**:
```python
class QuizAttemptBase(BaseModel):
    quiz_id: uuid.UUID
    score: int = Field(..., ge=0, le=100)
    passed: bool
    time_spent_seconds: Optional[int] = Field(None, ge=0)

class QuizAttempt(QuizAttemptBase):
    id: uuid.UUID
    user_id: uuid.UUID
    started_at: datetime
    completed_at: datetime

    class Config:
        from_attributes = True
```

**Business Rules**:
- Users can retake quizzes (multiple attempts allowed)
- `passed` computed: `score >= quiz.passing_score`
- Best score per quiz shown in progress tracking
- `time_spent_seconds` measured from first question view to last submission
- `completed_at` set when user finishes quiz

---

### 10. quiz_responses

Stores individual answers within a quiz attempt.

**Table Name**: `quiz_responses`

**Schema**:
```sql
CREATE TABLE quiz_responses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    attempt_id UUID NOT NULL REFERENCES quiz_attempts(id) ON DELETE CASCADE,
    question_id UUID NOT NULL REFERENCES quiz_questions(id) ON DELETE CASCADE,
    user_answer TEXT NOT NULL,
    is_correct BOOLEAN NOT NULL,
    answered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    UNIQUE(attempt_id, question_id)
);

CREATE INDEX idx_responses_attempt ON quiz_responses(attempt_id, answered_at ASC);
CREATE INDEX idx_responses_correctness ON quiz_responses(attempt_id, is_correct);
```

**Pydantic Model**:
```python
class QuizResponseBase(BaseModel):
    question_id: uuid.UUID
    user_answer: str
    is_correct: bool

class QuizResponse(QuizResponseBase):
    id: uuid.UUID
    attempt_id: uuid.UUID
    answered_at: datetime

    class Config:
        from_attributes = True
```

**Business Rules**:
- One response per question per attempt (UNIQUE constraint)
- `is_correct` computed by comparing `user_answer` to `quiz_questions.correct_answer`
- `user_answer` format matches question_type (option index, true/false, code snippet)
- Responses persisted for review and analytics

---

## Reference Data (Not Stored in Database)

### Chapters

Chapters are stored as markdown files in the repository, not in the database. The backend references chapters by their `chapter_id` (markdown filename slug).

**Chapter Metadata** (extracted from markdown frontmatter):
```yaml
---
id: chapter-03-ros2-topics
title: "ROS 2 Topics: Publisher-Subscriber Communication"
module: 1
week: 3
learning_objectives:
  - Understand publish-subscribe pattern
  - Create publishers and subscribers in Python
  - Visualize topic communication with rqt_graph
estimated_time_minutes: 45
---
```

**Chapter Structure**:
- `docs/module-1-ros2/chapter-03-ros2-topics.md`
- Chapter ID: `chapter-03-ros2-topics` (used in user_progress, bookmarks)

**Why Not in Database**:
- Content managed via git (version control, collaboration)
- Static site generation (Docusaurus) optimized for markdown
- No need for CRUD operations (content updated via git commits)
- Separation of concerns: content (git) vs. user data (database)

---

## Indexes Strategy

### Performance-Critical Indexes

1. **user_progress(user_id, last_accessed DESC)**:
   - Query: "Show user's recent chapters"
   - Frequency: Every page load for authenticated users
   - Impact: <50ms query time for 1000+ progress records per user

2. **chat_messages(conversation_id, created_at ASC)**:
   - Query: "Load conversation history for chatbot context"
   - Frequency: Every chatbot message
   - Impact: <100ms query time for 100+ messages per conversation

3. **quiz_attempts(user_id, quiz_id, completed_at DESC)**:
   - Query: "Show quiz attempt history, best score"
   - Frequency: Every quiz page load
   - Impact: <50ms query time for multiple attempts per user

4. **user_bookmarks(user_id, created_at DESC)**:
   - Query: "Load user's bookmarks"
   - Frequency: Progress dashboard page load
   - Impact: <30ms query time for 50+ bookmarks

### Composite Indexes

- `user_profiles(python_level, ai_experience, robotics_experience)`:
  - Query: "Find users with similar skill profiles" (future analytics)
  - Low frequency but useful for cohort analysis

### GIN Indexes (JSONB)

- `chat_messages USING GIN(citations)`:
  - Query: "Find all messages citing chapter X"
  - Frequency: Low (analytics use case)
  - Enables efficient JSONB searching: `citations @> '[{"chapter_id": "chapter-03"}]'`

---

## Data Validation Rules

### Email Validation (users.email)
- Regex: `^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$`
- Enforced at database CHECK constraint + Pydantic `EmailStr`

### Password Requirements
- Minimum 8 characters
- Hashed with bcrypt (10+ rounds) before storage
- Never stored in plaintext or logs

### Score Validation
- `quiz_score`, `quiz_attempts.score`: 0-100 range (CHECK constraint)
- Computed as: `(correct_answers / total_questions) * 100`

### Chapter ID Format
- Lowercase, hyphen-separated slug: `chapter-03-ros2-topics`
- Matches markdown filename without `.md` extension
- Validated against existing chapter list in backend

### Message Length Limits
- `chat_messages.message`: 2000 characters (Pydantic validation)
- Truncated client-side with user warning

---

## Migrations Strategy

### Alembic Configuration

**Initial Migration** (`alembic/versions/001_initial_schema.py`):
1. Create ENUM types (skill_level, progress_status, language, message_role, question_type, difficulty_level)
2. Create tables in dependency order:
   - users → user_profiles, user_progress, chat_conversations, user_bookmarks
   - chat_conversations → chat_messages
   - quizzes → quiz_questions
   - quiz_attempts → quiz_responses
3. Create indexes
4. Add CHECK constraints

**Migration Best Practices**:
- Always test migrations on development database first
- Use Neon branching feature for migration testing
- Never drop columns (add, deprecate, then remove in later migration)
- Add indexes CONCURRENTLY in production (non-blocking)

---

## Data Retention & Privacy (GDPR Compliance)

### Soft Delete (users)
- Set `is_deleted=TRUE`, `deleted_at=NOW()`
- Cascade to related tables: `ON DELETE CASCADE` or `ON DELETE SET NULL`
- Purge deleted user data after 30 days (scheduled job)

### Data Minimization
- Only collect necessary fields (email, skill levels, hardware access)
- No PII beyond email
- No tracking cookies or analytics without consent

### Right to Access
- API endpoint: `GET /api/user/data` returns JSON export of all user data
- Includes: profile, progress, bookmarks, chat history, quiz attempts

### Right to Erasure
- API endpoint: `DELETE /api/user/account` triggers soft delete
- Background job purges data after 30-day grace period
- Anonymize chat messages: Set `user_id=NULL` in `chat_conversations`

---

## Database Seeding (Development)

### Seed Data for Testing

**Users** (`seeds/users.sql`):
```sql
INSERT INTO users (id, email, password_hash) VALUES
('00000000-0000-0000-0000-000000000001', 'beginner@example.com', '$2b$10$...'),
('00000000-0000-0000-0000-000000000002', 'advanced@example.com', '$2b$10$...');
```

**User Profiles**:
```sql
INSERT INTO user_profiles (user_id, python_level, ai_experience, robotics_experience, has_rtx_gpu) VALUES
('00000000-0000-0000-0000-000000000001', 'beginner', 'beginner', 'beginner', FALSE),
('00000000-0000-0000-0000-000000000002', 'advanced', 'advanced', 'advanced', TRUE);
```

**Quizzes & Questions** (generated via script):
- Run `python scripts/generate_quizzes.py` to create quizzes for all chapters
- Uses OpenAI GPT-4 to generate questions aligned with learning objectives

---

## Performance Targets

| Operation | Target | Strategy |
|-----------|--------|----------|
| User login | <200ms | Indexed `users(email)`, connection pooling |
| Load progress | <100ms | Composite index `user_progress(user_id, last_accessed)` |
| Load chatbot history | <150ms | Index `chat_messages(conversation_id, created_at)` |
| Save quiz attempt | <250ms | Transaction with `quiz_attempts` + `quiz_responses` bulk insert |
| Load quiz questions | <100ms | Index `quiz_questions(quiz_id, order_index)` |

---

**Phase 1 Data Model Complete**: All entities defined with schemas, relationships, indexes, and validation rules. Ready to proceed to API contracts.
