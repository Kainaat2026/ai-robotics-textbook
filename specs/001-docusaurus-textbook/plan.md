# Implementation Plan: AI-Powered Physical AI & Humanoid Robotics Textbook

**Branch**: `001-docusaurus-textbook` | **Date**: 2026-01-09 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-docusaurus-textbook/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build an interactive, AI-powered educational platform delivering Physical AI and Humanoid Robotics content through Docusaurus. The platform combines static textbook content with dynamic AI features: a RAG chatbot for instant question-answering with citations, text selection AI for contextual explanations, personalized content adaptation based on user background, Urdu translation with RTL support, and auto-generated quizzes with immediate feedback. The system uses a hybrid architecture: Docusaurus static site for content delivery, FastAPI backend for AI services and authentication, Neon Postgres for user data, and Qdrant Cloud for vector search enabling semantic RAG retrieval.

## Technical Context

**Language/Version**:
- Frontend: JavaScript/TypeScript (Node.js 18+, React 18+)
- Backend: Python 3.11+
- Content: Markdown with MDX support

**Primary Dependencies**:
- Frontend: Docusaurus v3, React 18+, Axios (HTTP client), React Context API (state management)
- Backend: FastAPI, LangChain, OpenAI Python SDK, Qdrant Client, Neon Postgres Driver (asyncpg), Better-auth.com SDK
- AI/ML: OpenAI GPT-4 API, OpenAI Embeddings (text-embedding-3-small)

**Storage**:
- User Data & Progress: Neon Serverless Postgres (hosted cloud database)
- Vector Embeddings: Qdrant Cloud Free Tier (for RAG document retrieval)
- Static Content: Markdown files in git repository
- Compiled Site: GitHub Pages or Vercel (static hosting)

**Testing**:
- Frontend: Jest + React Testing Library (component tests)
- Backend: pytest + pytest-asyncio (API tests)
- E2E: Playwright (user journey tests)
- Integration: Contract testing for API endpoints

**Target Platform**:
- Web application accessible via modern browsers (Chrome, Firefox, Safari, Edge - last 2 versions)
- Responsive design: Desktop (1920x1080), Tablet (768x1024), Mobile (375x667)
- Backend: Cloud-hosted Python service (compatible with Vercel Serverless Functions or similar)

**Project Type**: Web application (frontend + backend)

**Performance Goals**:
- Frontend: <3s initial page load on 3G, <5s Time to Interactive, LCP <2.5s, CLS <0.1, FID <100ms
- Backend: <500ms API response time for standard queries, <2s RAG chatbot response
- Database: <200ms query execution time
- Vector Search: <1s semantic search latency
- Concurrent Users: Support 100+ simultaneous users without degradation

**Constraints**:
- Free/affordable tier limits: Qdrant Cloud free tier (1GB vectors), Neon Postgres free tier (0.5GB)
- OpenAI API rate limits: Standard tier (60 requests/minute)
- Accessibility: Lighthouse score 95+, WCAG AA compliance
- Security: AES-256 encryption at rest, TLS 1.3 in transit, bcrypt password hashing (10+ rounds)
- Localization: Support English and Urdu with RTL text rendering

**Scale/Scope**:
- Content: 10+ chapters across 4 modules (Module 1: ROS 2, Module 2: Simulation, Module 3: NVIDIA Isaac, Module 4: VLA & Capstone)
- Users: Designed for 100+ concurrent learners, optimized for educational institution scale
- Features: 7 user stories (2 P1, 2 P2, 3 P3), 33 functional requirements, 8 key entities
- Development Timeline: Hackathon project (focused on core P1/P2 features for MVP, P3 as bonus)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Alignment with Core Principles

✅ **I. Accessibility First**:
- Plan includes responsive Docusaurus design supporting desktop, tablet, mobile
- Urdu translation with RTL formatting using i18n libraries
- Lighthouse 95+ accessibility target with screen reader support
- Touch-optimized mobile interactions

✅ **II. AI-Enhanced Learning**:
- RAG chatbot using LangChain + Qdrant for sourced answers with citations
- Text selection AI using OpenAI API with context-aware prompts
- Auto-generated quizzes using GPT-4 aligned with learning objectives
- <2s chatbot response time enforced through API optimization and caching

✅ **III. Personalization Without Bias**:
- Better-auth.com for secure authentication with background questionnaire
- User profile stores skill level (beginner/intermediate/advanced) and hardware access
- Content adaptation using OpenAI API with skill-level prompts (no algorithmic bias)
- AES-256 encryption for user data, minimal data collection (email, background only)

✅ **IV. Technical Excellence**:
- Modern stack: Docusaurus (React), FastAPI (Python), Neon Postgres, Qdrant Cloud, Better-auth.com
- Multi-agent architecture: Separate concerns (content delivery, AI services, auth, storage)
- Clean code: DRY principles, TypeScript for type safety, Python type hints, comprehensive comments
- Documentation: inline code comments, API documentation (OpenAPI), developer quickstart guide

✅ **V. Content Integrity**:
- 13-week course structure: 4 modules covering ROS 2, Simulation, NVIDIA Isaac, VLA & Capstone
- Markdown-based content with code examples (Python, ROS 2) using syntax highlighting
- Diagrams embedded as images with alt text for accessibility
- Content validation: Each chapter includes learning objectives, exercises, quiz aligned with objectives

✅ **VI. User Experience Excellence**:
- Intuitive Docusaurus sidebar navigation following module structure
- Progress indicators using React state + Postgres persistence
- Floating chatbot button accessible from any page
- One-click actions: "Translate to Urdu", "Personalize", "Take Quiz"
- Performance optimizations: image compression, lazy loading, CDN caching

### Performance Standards Compliance

✅ **Frontend Performance**:
- Docusaurus build optimization with code splitting
- Image optimization using Sharp (built into Docusaurus)
- Lazy loading for heavy components (chatbot, quiz)
- CDN hosting (GitHub Pages/Vercel) for static assets

✅ **Backend Performance**:
- FastAPI async/await for concurrent request handling
- Database connection pooling (asyncpg)
- Vector search optimized with Qdrant indexing
- Caching layer for frequent queries (in-memory LRU cache)

✅ **Quality Metrics**:
- Code coverage: pytest for backend (target 80%+), Jest for frontend
- Accessibility: Automated Lighthouse CI checks in GitHub Actions
- Security: Dependency scanning (Dependabot), secrets management (environment variables)

### Technology Stack Compliance

✅ **Constitution-Specified Technologies**:
- ✅ Docusaurus: Static site generator for textbook
- ✅ FastAPI: Backend API framework
- ✅ Neon Serverless Postgres: Database
- ✅ Qdrant Cloud: Vector store for RAG
- ✅ Better-auth.com: Authentication service

### Gate Status: ✅ PASSED

All core principles are addressed in the technical design. No constitution violations. Ready to proceed to Phase 0 research.

## Project Structure

### Documentation (this feature)

```text
specs/001-docusaurus-textbook/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output - technology decisions and rationale
├── data-model.md        # Phase 1 output - entities, schemas, relationships
├── quickstart.md        # Phase 1 output - developer setup guide
├── contracts/           # Phase 1 output - API contracts
│   ├── openapi.yaml     # OpenAPI 3.0 specification for REST APIs
│   ├── chatbot.yaml     # Chatbot service contract
│   ├── auth.yaml        # Authentication endpoints
│   ├── personalization.yaml  # Content personalization API
│   └── translation.yaml # Translation service contract
├── checklists/          # Quality validation checklists
│   └── requirements.md  # Spec quality checklist (completed)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
# Web application structure (Docusaurus + FastAPI backend)

# Frontend - Docusaurus static site
docs/                           # Textbook content (markdown files)
├── intro.md                    # Homepage / introduction
├── module-1-ros2/             # Module 1: ROS 2 (Weeks 1-5)
│   ├── chapter-01-intro-physical-ai.md
│   ├── chapter-02-ros2-fundamentals.md
│   ├── chapter-03-ros2-topics.md
│   ├── chapter-04-ros2-services.md
│   └── chapter-05-ros2-actions.md
├── module-2-simulation/       # Module 2: Gazebo & Unity (Weeks 6-7)
│   ├── chapter-06-gazebo-intro.md
│   └── chapter-07-unity-robotics.md
├── module-3-isaac/            # Module 3: NVIDIA Isaac (Weeks 8-10)
│   ├── chapter-08-isaac-sdk.md
│   ├── chapter-09-isaac-sim.md
│   └── chapter-10-sim-to-real.md
└── module-4-vla-capstone/     # Module 4: VLA & Capstone (Weeks 11-13)
    ├── chapter-11-humanoid-dev.md
    ├── chapter-12-conversational-robotics.md
    └── chapter-13-capstone-project.md

src/                           # Docusaurus custom components and pages
├── components/
│   ├── Chatbot/              # RAG chatbot component
│   │   ├── ChatbotWidget.tsx  # Floating chat button
│   │   ├── ChatbotInterface.tsx  # Chat UI
│   │   └── ChatbotService.ts  # API communication
│   ├── TextSelection/         # Text selection AI feature
│   │   ├── SelectionHandler.tsx  # Text selection detection
│   │   └── SelectionTooltip.tsx  # "Ask AI" tooltip
│   ├── Quiz/                  # Quiz components
│   │   ├── QuizWidget.tsx     # Quiz UI
│   │   ├── QuestionCard.tsx   # Individual question
│   │   └── QuizResults.tsx    # Score and feedback
│   ├── Auth/                  # Authentication UI
│   │   ├── SignupForm.tsx     # Signup with background questionnaire
│   │   ├── LoginForm.tsx      # Login form
│   │   └── UserProfile.tsx    # Profile and progress
│   ├── Translation/           # Urdu translation
│   │   └── LanguageToggle.tsx # One-click translation button
│   └── Personalization/       # Content personalization
│       └── PersonalizeButton.tsx  # One-click personalization
├── pages/                     # Custom Docusaurus pages
│   └── progress.tsx           # User progress dashboard
├── css/                       # Custom styles
│   ├── custom.css             # Global styles
│   └── rtl.css                # RTL styles for Urdu
└── theme/                     # Docusaurus theme customizations
    └── DocItem/               # Custom chapter rendering

docusaurus.config.js          # Docusaurus configuration
sidebars.js                   # Sidebar navigation structure
package.json                  # Frontend dependencies
tsconfig.json                 # TypeScript configuration

# Backend - FastAPI service
backend/
├── src/
│   ├── main.py               # FastAPI app entry point
│   ├── config.py             # Configuration (env vars)
│   ├── models/               # Data models (Pydantic + SQLAlchemy)
│   │   ├── user.py           # User entity
│   │   ├── progress.py       # User progress tracking
│   │   ├── quiz.py           # Quiz and questions
│   │   ├── chat.py           # Chat conversations
│   │   └── bookmark.py       # User bookmarks
│   ├── services/             # Business logic layer
│   │   ├── rag_service.py    # RAG chatbot logic (LangChain + Qdrant)
│   │   ├── quiz_service.py   # Quiz generation (OpenAI GPT-4)
│   │   ├── personalization_service.py  # Content adaptation
│   │   ├── translation_service.py      # Urdu translation
│   │   └── auth_service.py   # Authentication (Better-auth.com)
│   ├── api/                  # API endpoints (FastAPI routers)
│   │   ├── chatbot.py        # /api/chat endpoints
│   │   ├── quiz.py           # /api/quiz endpoints
│   │   ├── auth.py           # /api/auth endpoints
│   │   ├── progress.py       # /api/progress endpoints
│   │   ├── personalization.py # /api/personalize endpoints
│   │   └── translation.py    # /api/translate endpoints
│   ├── db/                   # Database layer
│   │   ├── connection.py     # Neon Postgres connection
│   │   ├── migrations/       # Database migrations (Alembic)
│   │   └── repositories/     # Data access layer
│   │       ├── user_repo.py
│   │       ├── progress_repo.py
│   │       └── chat_repo.py
│   └── utils/                # Utilities
│       ├── vector_store.py   # Qdrant client wrapper
│       ├── embeddings.py     # OpenAI embeddings
│       └── security.py       # Encryption, hashing utilities
└── tests/                    # Backend tests
    ├── unit/                 # Unit tests (pytest)
    │   ├── test_rag_service.py
    │   ├── test_quiz_service.py
    │   └── test_auth_service.py
    ├── integration/          # Integration tests
    │   ├── test_api_chatbot.py
    │   └── test_api_auth.py
    └── contract/             # Contract tests
        └── test_openapi_compliance.py

requirements.txt              # Python dependencies
pyproject.toml               # Python project configuration
.env.example                 # Environment variables template

# Shared
.github/
└── workflows/
    ├── frontend-ci.yml      # Frontend CI (build, test, lint)
    ├── backend-ci.yml       # Backend CI (pytest, lint)
    └── deploy.yml           # Deployment pipeline

# Testing
tests/                       # E2E tests (separate from unit/integration)
└── e2e/
    ├── test_chatbot_flow.spec.ts    # Playwright E2E tests
    ├── test_quiz_flow.spec.ts
    └── test_translation_flow.spec.ts

playwright.config.ts         # Playwright configuration

# Documentation
README.md                    # Project overview and setup instructions
CONTRIBUTING.md              # Contribution guidelines
docs-images/                 # Diagrams and screenshots for chapters
└── [chapter-specific-images]

# Configuration
.gitignore                   # Git ignore patterns
.env                         # Environment variables (not committed)
.env.example                 # Template for environment setup
```

**Structure Decision**:

We've selected a **web application structure** with clear frontend/backend separation:

1. **Frontend (Docusaurus)**: Handles static textbook content, navigation, and React-based interactive components. Docusaurus provides built-in optimizations (code splitting, lazy loading, SSG) and excellent developer experience with hot reload.

2. **Backend (FastAPI)**: Provides REST APIs for AI services (RAG chatbot, quiz generation, personalization, translation) and handles authentication + user data persistence. FastAPI's async support enables high concurrency for chatbot requests.

3. **Separation Rationale**:
   - Static content (markdown chapters) served via CDN (GitHub Pages/Vercel) for fast global delivery
   - Dynamic AI features (chatbot, personalization) require backend processing with OpenAI API and vector search
   - Clear API contracts enable independent frontend/backend development and testing
   - Backend can scale independently if user load increases

4. **Deployment Model**:
   - Frontend: Static site deployed to GitHub Pages or Vercel (free hosting)
   - Backend: FastAPI deployed as serverless functions (Vercel) or containerized service (Fly.io)
   - Database: Neon Serverless Postgres (managed, auto-scaling)
   - Vector Store: Qdrant Cloud (managed)

This structure aligns with the constitution's Technical Excellence principle (modern, maintainable technologies) and supports the performance goals (<3s page load, <2s chatbot response).

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No constitution violations detected. All complexity is justified by feature requirements:

1. **Multi-service architecture** (Docusaurus + FastAPI + Neon + Qdrant): Required for separating static content delivery from dynamic AI processing. Simpler monolithic architecture rejected because mixing static site generation with AI inference would compromise performance goals (<3s page load).

2. **Multiple AI service integrations** (OpenAI for RAG/quiz/translation, Qdrant for vectors): Required to meet functional requirements (FR-006 to FR-013, FR-020 to FR-029). Building custom NLP models rejected due to development time constraints and inferior quality compared to GPT-4.

3. **Dual language support** (English + Urdu with RTL): Required by FR-025 to FR-029 and constitution principle I (Accessibility First). Single-language solution rejected as it excludes Urdu-speaking learners in target market (Pakistan).

All complexity directly traces to user stories and functional requirements. No premature optimization or over-engineering detected.
