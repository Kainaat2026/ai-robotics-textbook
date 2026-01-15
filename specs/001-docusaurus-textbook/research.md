# Research & Technology Decisions

**Feature**: AI-Powered Physical AI & Humanoid Robotics Textbook
**Branch**: `001-docusaurus-textbook`
**Date**: 2026-01-09
**Phase**: Phase 0 - Research and Architecture Foundation

## Overview

This document consolidates research findings and technology decisions for building an AI-powered educational textbook platform. Each decision is backed by rationale, alternatives considered, and alignment with project constraints (free tier services, <3s load time, <2s chatbot response, 100+ concurrent users).

---

## 1. Static Site Generator: Docusaurus v3

### Decision
Use **Docusaurus v3** for textbook content delivery and navigation.

### Rationale
1. **Built for Documentation**: Docusaurus is specifically designed for documentation sites with markdown content, making it ideal for textbook chapters
2. **Performance**: Static Site Generation (SSG) delivers pre-rendered HTML for instant page loads (<3s on 3G)
3. **Developer Experience**: Hot reload, MDX support (React components in markdown), built-in search
4. **Accessibility**: Built-in keyboard navigation, semantic HTML, ARIA labels (helps achieve Lighthouse 95+)
5. **Versioning**: Built-in versioning system useful if content needs to be archived across course iterations
6. **i18n Support**: First-class internationalization for Urdu translation with RTL support
7. **Free Hosting**: Static output deploys to GitHub Pages or Vercel at zero cost
8. **React Integration**: Seamlessly integrates custom React components (chatbot, quiz, auth UI)

### Alternatives Considered
- **Next.js**: More complex setup, requires server for SSR (higher cost), overkill for primarily static content
- **VuePress**: Smaller ecosystem, less TypeScript support, weaker React integration
- **GitBook**: Proprietary, limited customization, paid hosting for advanced features
- **Jekyll/Hugo**: No React integration, harder to add interactive components

### Implementation Notes
- Use Docusaurus themes for consistent styling
- Customize `DocItem` theme component for chapter rendering with personalization and translation buttons
- Configure sidebar.js to match 4-module course structure
- Enable MDX for embedding interactive components (quiz, code examples with syntax highlighting)

### Alignment with Requirements
- ✅ FR-001: 10+ chapters across 4 modules (sidebar navigation)
- ✅ FR-003: Responsive design (Docusaurus mobile-first)
- ✅ FR-004: Intuitive navigation (built-in sidebar, breadcrumbs)
- ✅ FR-030: <3s page load (SSG performance)
- ✅ SC-001: Multi-device accessibility

---

## 2. Backend Framework: FastAPI (Python 3.11+)

### Decision
Use **FastAPI** with Python 3.11+ for backend API services.

### Rationale
1. **Async/Await**: Native async support crucial for handling concurrent chatbot requests without blocking
2. **Performance**: FastAPI is one of the fastest Python frameworks (comparable to Node.js/Go), supporting 100+ concurrent users
3. **Type Safety**: Pydantic models provide automatic validation and OpenAPI schema generation
4. **OpenAI SDK**: Python has the official OpenAI SDK with excellent documentation
5. **LangChain Integration**: LangChain (Python) is the leading framework for RAG pipelines
6. **Developer Experience**: Auto-generated interactive API docs (Swagger UI), easy debugging
7. **Deployment**: Serverless-friendly (Vercel Functions, AWS Lambda) or containerized (Docker)

### Alternatives Considered
- **Node.js/Express**: Weaker typing, less mature RAG ecosystem, harder to integrate with LangChain
- **Django REST Framework**: Heavier framework with ORM baggage, slower than FastAPI for API-only workload
- **Flask**: Synchronous by default (can add async but not native), less modern than FastAPI

### Implementation Notes
- Use async/await throughout (`async def` endpoints, `asyncpg` for Postgres, async OpenAI client)
- Structure routes as APIRouter modules (chatbot.py, quiz.py, auth.py, etc.)
- Implement dependency injection for database connections and AI services
- Add request ID middleware for logging and debugging
- Use Pydantic models for request/response validation

### Alignment with Requirements
- ✅ FR-006 to FR-013: AI-powered features (async crucial for OpenAI API calls)
- ✅ FR-033: 100+ concurrent users (async architecture)
- ✅ Backend Performance: <500ms API response, <2s chatbot

---

## 3. RAG Implementation: LangChain + Qdrant Cloud

### Decision
Use **LangChain** for RAG orchestration with **Qdrant Cloud** (free tier) for vector storage.

### Rationale

**LangChain**:
1. **RAG Patterns**: Pre-built components for document loading, splitting, retrieval, and generation
2. **OpenAI Integration**: Native support for OpenAI embeddings and GPT-4 chat
3. **Retrieval Strategies**: Supports similarity search, MMR (Maximum Marginal Relevance), multi-query retrieval
4. **Citation Tracking**: Can track source documents for each generated response (critical for FR-007)
5. **Community**: Large ecosystem with examples for educational chatbots

**Qdrant Cloud**:
1. **Free Tier**: 1GB vector storage (sufficient for 10-13 chapters after compression)
2. **Performance**: <1s vector search latency, optimized for semantic similarity
3. **Managed Service**: Zero infrastructure management, auto-scaling
4. **Filtering**: Metadata filtering (e.g., filter by chapter, module) for scoped retrieval
5. **Python SDK**: Clean async API integrates with FastAPI

### Alternatives Considered
- **Pinecone**: Free tier limited to 1 index (may need separate indexes for English/Urdu), less generous storage
- **Weaviate**: More complex setup, self-hosting required for free tier
- **Chroma**: Open-source but requires self-hosting (adds infrastructure cost/complexity)
- **FAISS (local)**: No cloud persistence, loses indexes on restart unless managing files

### Implementation Notes
- Embed textbook chapters during build time using OpenAI `text-embedding-3-small` (cheaper, faster)
- Split chapters into ~500-token chunks with 50-token overlap for context preservation
- Store metadata: `{chapter_id, chapter_title, section_heading, content_type}`
- Implement retrieval with `top_k=3` for balance between context and response speed
- Cache embeddings to avoid re-computing on every deployment

### Alignment with Requirements
- ✅ FR-006: RAG chatbot based on textbook content
- ✅ FR-007: Citations (LangChain tracks source documents)
- ✅ FR-008: Context retention (LangChain conversation memory)
- ✅ SC-002: 95% accuracy with citations

---

## 4. OpenAI API: GPT-4 for Generation, text-embedding-3-small for Embeddings

### Decision
Use **GPT-4** (via OpenAI API) for RAG generation, quiz creation, personalization, and translation. Use **text-embedding-3-small** for vector embeddings.

### Rationale

**GPT-4**:
1. **Quality**: Superior accuracy for educational content (reduces hallucinations compared to GPT-3.5)
2. **Reasoning**: Better at multi-step reasoning required for quiz generation and personalization
3. **Technical Domain**: Strong performance on robotics/AI terminology (ROS 2, NVIDIA Isaac, etc.)
4. **Citation Compliance**: Follows instructions to cite sources more reliably
5. **Multilingual**: Excellent Urdu translation quality with technical term handling

**text-embedding-3-small**:
1. **Cost-Effective**: 5x cheaper than text-embedding-ada-002, suitable for 10+ chapters
2. **Performance**: 1536 dimensions, comparable accuracy to ada-002 for semantic search
3. **Speed**: Faster inference, helps achieve <1s vector search target

### Alternatives Considered
- **GPT-3.5-turbo**: 50% cheaper but lower quality, more hallucinations, weaker multilingual support
- **Claude 3**: Good quality but more expensive, no embeddings API (would need separate provider)
- **Open-source LLMs** (Llama 3, Mixtral): Require self-hosting (infrastructure cost), slower inference

### Cost Management
- Estimate: ~$0.03 per chatbot message (GPT-4 + embeddings)
- Rate limiting: 60 requests/minute (OpenAI standard tier)
- Caching: Cache quiz questions, translations, common queries to reduce API calls
- Fallback: If budget exceeded, gracefully degrade to cached responses or user-friendly error

### Implementation Notes
- Use `gpt-4-turbo` for cost optimization (cheaper than gpt-4, similar quality)
- Set `temperature=0.3` for RAG (more deterministic), `temperature=0.7` for quiz generation (more creative)
- Implement streaming responses for chatbot (improves perceived speed)
- Add retry logic with exponential backoff for rate limit errors

### Alignment with Requirements
- ✅ FR-006 to FR-013: All AI features (RAG, text selection, quizzes)
- ✅ FR-020 to FR-024: Personalization
- ✅ FR-025 to FR-029: Translation
- ✅ SC-002: 95% accuracy, <2s response time

---

## 5. Database: Neon Serverless Postgres

### Decision
Use **Neon Serverless Postgres** (free tier) for user data, progress tracking, and chat history.

### Rationale
1. **Free Tier**: 0.5GB storage (sufficient for 1000+ users with progress data)
2. **Serverless**: Auto-scaling, no infrastructure management, pay-per-use beyond free tier
3. **Postgres Compatibility**: Full Postgres features (foreign keys, transactions, JSON columns)
4. **Performance**: Connection pooling, <200ms queries with proper indexing
5. **Branching**: Database branching useful for testing migrations without affecting production
6. **Python Integration**: Excellent `asyncpg` driver for FastAPI async operations

### Schema Design
- **users**: `id, email, password_hash, created_at, last_login`
- **user_profiles**: `user_id, python_level, ai_level, robotics_level, has_rtx_gpu, has_jetson, has_robot`
- **user_progress**: `user_id, chapter_id, status, quiz_score, time_spent, last_accessed`
- **chat_conversations**: `id, user_id, language, created_at`
- **chat_messages**: `conversation_id, role, message, citations, timestamp`
- **user_bookmarks**: `user_id, chapter_id, section, notes, created_at`

### Alternatives Considered
- **Supabase**: Includes auth built-in, but we're using Better-auth.com (redundant), heavier with extra features
- **PlanetScale**: MySQL-based (lose Postgres features like JSONB, better text search)
- **MongoDB Atlas**: NoSQL complicates relational data (user -> progress -> chapters), less mature for Python async

### Implementation Notes
- Use Alembic for database migrations (version-controlled schema changes)
- Index frequently queried columns: `user_progress(user_id, chapter_id)`, `chat_conversations(user_id)`
- Use JSONB column for `citations` in chat_messages (flexible structure)
- Implement soft deletes for GDPR compliance (mark deleted, purge after 30 days)

### Alignment with Requirements
- ✅ FR-014 to FR-019: Authentication and user management
- ✅ FR-019: Progress tracking
- ✅ FR-018: Account deletion (GDPR)
- ✅ Backend Performance: <200ms query time

---

## 6. Authentication: Better-auth.com

### Decision
Use **Better-auth.com** for authentication with custom background questionnaire.

### Rationale
1. **Secure by Default**: Pre-built password hashing (bcrypt), JWT token management, session handling
2. **Customizable**: Supports custom signup fields (software background, hardware access)
3. **Rate Limiting**: Built-in protection against brute force attacks (5 attempts per 15 minutes)
4. **Compliance**: GDPR-compliant user data handling
5. **Developer Experience**: Simple SDK integration with FastAPI, clear documentation
6. **Free Tier**: Generous limits for educational projects (1000+ users)

### Alternatives Considered
- **Auth0**: More complex setup, paid tier required for custom fields, overkill for hackathon
- **Supabase Auth**: Tied to Supabase database (we're using Neon), less flexible
- **Roll-your-own**: Security risks (password handling, session management), time-consuming

### Implementation Notes
- Extend signup form with custom fields: `python_level`, `ai_level`, `robotics_level`, `has_rtx_gpu`, `has_jetson`, `has_robot`
- Store extended profile in Neon Postgres `user_profiles` table
- Use JWT tokens (24-hour expiration) with refresh token rotation
- Implement middleware to verify tokens on protected routes
- Add user context to FastAPI dependency injection

### Alignment with Requirements
- ✅ FR-014: Signup with background questionnaire
- ✅ FR-015: Secure authentication (bcrypt, JWT)
- ✅ FR-016: Rate limiting
- ✅ FR-017: Encryption and TLS
- ✅ SC-003: 90% successful login on first attempt

---

## 7. Translation: OpenAI GPT-4 with Urdu Prompt Engineering

### Decision
Use **OpenAI GPT-4** for Urdu translation with custom prompts for technical terminology handling.

### Rationale
1. **Quality**: GPT-4 handles technical content better than generic translation APIs (Google Translate, DeepL)
2. **Context-Aware**: Can preserve code blocks, maintain markdown formatting, handle mixed content
3. **Terminology Control**: Prompt engineering ensures IEEE Urdu terminology guide compliance
4. **Cost-Effective**: Already using OpenAI API for other features (no additional service integration)
5. **Customization**: Can specify transliteration rules (e.g., "Robot" → "روبوٹ") in prompt

### Alternatives Considered
- **Google Translate API**: Free tier limited, poor handling of technical terms, loses markdown formatting
- **DeepL**: Better quality than Google but still weaker on technical content, paid API
- **Azure Translator**: Good quality but separate service adds complexity, paid

### Implementation Notes
- Cache translations in Postgres or Redis to avoid re-translating same content
- Translate markdown chunks (not HTML) to preserve structure
- Prompt template:
  ```
  Translate the following Physical AI & Humanoid Robotics textbook content from English to Urdu.
  Follow these rules:
  1. Preserve all markdown formatting (headers, lists, links, code blocks)
  2. Keep all code blocks in English (do not translate code)
  3. Use IEEE Urdu terminology for computing terms where available
  4. Transliterate English technical terms without Urdu equivalents (e.g., "Robot" → "روبوٹ")
  5. Maintain technical accuracy - do not simplify or paraphrase

  Content:
  {content}
  ```
- Implement RTL CSS for Urdu: `direction: rtl; text-align: right;`

### Alignment with Requirements
- ✅ FR-025: One-click Urdu translation
- ✅ FR-026: Technical terminology accuracy (95%+)
- ✅ FR-027: Code in English, text in Urdu
- ✅ FR-028: RTL formatting
- ✅ SC-006: 95% technical term accuracy

---

## 8. Frontend State Management: React Context API

### Decision
Use **React Context API** (built into React) for client-side state management.

### Rationale
1. **Simplicity**: No external library needed, reduces bundle size
2. **Sufficient**: User state (auth, language, personalization) is simple enough for Context
3. **Performance**: Avoid re-renders with context splitting (UserContext, LanguageContext, ChatContext)
4. **Docusaurus Compatible**: Works seamlessly with Docusaurus theme system
5. **TypeScript Support**: Strong typing for context values

### Alternatives Considered
- **Redux**: Overkill for simple state, adds 20KB+ to bundle, boilerplate-heavy
- **Zustand**: Lightweight but external dependency, Context is sufficient
- **Jotai/Recoil**: Atomic state management unnecessary for this use case

### Implementation Notes
- Create contexts:
  - `UserContext`: Auth state, user profile (skill level, hardware)
  - `LanguageContext`: Current language (en/ur), translation toggle
  - `ChatContext`: Chatbot state (open/closed, messages, loading)
- Use `useReducer` for complex state updates (chatbot messages)
- Persist user preferences in localStorage (language, personalization)
- Sync auth state with backend on page load (verify JWT)

### Alignment with Requirements
- ✅ Frontend Performance: Minimal bundle size impact
- ✅ FR-019: Progress tracking (state synced with backend)
- ✅ SC-005: <1s personalization response (cached in context)

---

## 9. Styling: Docusaurus Custom CSS + Tailwind Utility Classes

### Decision
Use **Docusaurus custom CSS** with optional **Tailwind CSS** utility classes for component styling.

### Rationale
1. **Docusaurus Themes**: Built-in dark mode, responsive breakpoints, color system
2. **Customization**: Override theme variables in `custom.css` for branding
3. **Tailwind Utilities**: Rapid prototyping for custom components (chatbot, quiz, auth forms)
4. **RTL Support**: Separate `rtl.css` for Urdu-specific styles
5. **Performance**: Tailwind purges unused classes (minimal CSS in production)

### Alternatives Considered
- **Material-UI (MUI)**: Heavy (300KB+), opinionated design, increases bundle size
- **Ant Design**: Large bundle, more suited for enterprise apps than educational content
- **Styled-components**: Runtime CSS-in-JS has performance cost, conflicts with SSG

### Implementation Notes
- Install Tailwind as Docusaurus plugin
- Configure `tailwind.config.js` with RTL support: `plugins: [require('tailwindcss-rtl')]`
- Use CSS variables for theme colors (light/dark mode)
- Implement responsive breakpoints: `sm: 640px, md: 768px, lg: 1024px, xl: 1280px`
- Create `rtl.css` for Urdu-specific overrides:
  ```css
  html[dir="rtl"] .sidebar { right: 0; left: auto; }
  html[dir="rtl"] .main-content { margin-right: 250px; margin-left: 0; }
  ```

### Alignment with Requirements
- ✅ FR-003: Responsive design
- ✅ FR-028: RTL formatting for Urdu
- ✅ FR-032: Mobile-friendly, touch-optimized
- ✅ Frontend Performance: <3s page load

---

## 10. Testing Strategy: Jest + Playwright + pytest

### Decision
Use **Jest + React Testing Library** (frontend), **Playwright** (E2E), **pytest** (backend).

### Rationale

**Frontend (Jest + React Testing Library)**:
1. **Docusaurus Standard**: Jest is pre-configured in Docusaurus
2. **Component Testing**: React Testing Library focuses on user behavior (not implementation details)
3. **Fast**: Unit tests run in milliseconds, suitable for CI/CD
4. **TypeScript Support**: Native TypeScript support via ts-jest

**E2E (Playwright)**:
1. **Multi-Browser**: Tests Chrome, Firefox, Safari (ensures cross-browser compatibility)
2. **Modern API**: Async/await, auto-wait for elements, built-in screenshots/videos on failure
3. **Performance Testing**: Can measure page load times, LCP, FID (validates performance requirements)
4. **Headless**: Runs in CI without display server

**Backend (pytest)**:
1. **Python Standard**: Most popular Python testing framework
2. **Async Support**: pytest-asyncio for testing FastAPI async endpoints
3. **Fixtures**: Reusable test setup (database, mock OpenAI responses)
4. **Coverage**: pytest-cov for code coverage reports (target 80%+)

### Alternatives Considered
- **Cypress** (E2E): Slower than Playwright, no Safari support, larger community but dated architecture
- **Mocha/Chai** (frontend): Less React-specific than Jest + RTL
- **unittest** (backend): Standard library but less ergonomic than pytest

### Test Coverage Strategy
- **Frontend**: 70%+ coverage focusing on critical paths (chatbot, auth, quiz)
- **Backend**: 80%+ coverage (all service methods, API endpoints)
- **E2E**: 7 user stories = 7 E2E test suites (one per story)

### Alignment with Requirements
- ✅ Quality Metrics: >80% code coverage for critical paths
- ✅ Contract Testing: Validate OpenAPI schema compliance
- ✅ Performance Testing: Measure <3s page load, <2s chatbot response

---

## 11. Deployment: Vercel (Frontend + Backend)

### Decision
Deploy **frontend (Docusaurus)** and **backend (FastAPI)** both to **Vercel**.

### Rationale
1. **Unified Platform**: Single deployment pipeline for frontend + backend
2. **Serverless Functions**: FastAPI converts to Vercel serverless functions (Python support)
3. **Free Tier**: Generous limits for hackathon project (100GB bandwidth, 1000 hours compute)
4. **CDN**: Global edge network for <3s page load worldwide
5. **Environment Variables**: Secure secret management (OpenAI keys, database credentials)
6. **GitHub Integration**: Auto-deploy on push to main branch, preview deployments for PRs
7. **Performance**: Edge caching, automatic compression, image optimization

### Alternatives Considered
- **GitHub Pages + Separate Backend Hosting**:
  - Frontend: GitHub Pages (free, simple for static sites)
  - Backend: Fly.io (free tier), Railway, Render
  - Complexity: Two deployment pipelines, CORS configuration, separate monitoring
- **Netlify**: Similar to Vercel but weaker Python support (Netlify Functions primarily Node.js)
- **AWS (S3 + Lambda)**: More complex setup, requires AWS expertise, overkill for hackathon

### Implementation Notes
- Structure for Vercel:
  ```
  /                    # Docusaurus site (auto-detected)
  /api/               # FastAPI backend (Vercel Python runtime)
  vercel.json         # Configuration file
  ```
- Configure `vercel.json`:
  ```json
  {
    "builds": [
      { "src": "api/**/*.py", "use": "@vercel/python" },
      { "src": "package.json", "use": "@vercel/static-build" }
    ],
    "routes": [
      { "src": "/api/(.*)", "dest": "/api/main.py" },
      { "src": "/(.*)", "dest": "/$1" }
    ]
  }
  ```
- Environment variables in Vercel dashboard:
  - `OPENAI_API_KEY`
  - `NEON_DATABASE_URL`
  - `QDRANT_API_KEY`, `QDRANT_URL`
  - `BETTER_AUTH_SECRET`

### Alignment with Requirements
- ✅ Frontend Performance: <3s page load (CDN)
- ✅ Backend Performance: <500ms API response (edge functions)
- ✅ FR-033: 100+ concurrent users (auto-scaling)
- ✅ Security: TLS 1.3 by default

---

## 12. Development Workflow: GitHub + GitHub Actions CI/CD

### Decision
Use **GitHub** for version control with **GitHub Actions** for CI/CD pipelines.

### Rationale
1. **Free**: Unlimited private repos, 2000 CI/CD minutes/month (sufficient for hackathon)
2. **Integration**: Seamless with Vercel (auto-deploy), Dependabot (security), GitHub Pages
3. **Workflow Templates**: Pre-built actions for Node.js, Python, Playwright
4. **Branch Protection**: Enforce tests pass before merge (quality gate)
5. **Collaboration**: Issues, PRs, code review tools

### CI/CD Pipeline
**Frontend CI** (`.github/workflows/frontend-ci.yml`):
- Trigger: Push to `main` or PR to `main`
- Steps:
  1. Install dependencies (`npm ci`)
  2. Lint (ESLint + TypeScript check)
  3. Test (Jest unit tests)
  4. Build (Docusaurus build)
  5. Lighthouse CI (accessibility, performance checks)

**Backend CI** (`.github/workflows/backend-ci.yml`):
- Trigger: Push to `main` or PR to `main`
- Steps:
  1. Install dependencies (`pip install -r requirements.txt`)
  2. Lint (Black, Flake8, mypy)
  3. Test (pytest with coverage report)
  4. Contract test (validate OpenAPI schema)

**Deploy** (`.github/workflows/deploy.yml`):
- Trigger: Push to `main` (after CI passes)
- Steps:
  1. Deploy to Vercel (automatic via Vercel GitHub integration)
  2. Run E2E tests (Playwright) against production URL
  3. Notify on failure (GitHub Issues)

### Alignment with Requirements
- ✅ Quality Metrics: Automated code coverage, linting
- ✅ Accessibility: Lighthouse CI ensures 95+ score
- ✅ Security: Dependabot for dependency vulnerabilities

---

## Summary of Key Decisions

| Component | Technology | Rationale |
|-----------|------------|-----------|
| Frontend Framework | Docusaurus v3 | SSG performance, docs-focused, React integration, free hosting |
| Backend Framework | FastAPI (Python 3.11+) | Async support, OpenAI/LangChain compatibility, performance |
| RAG Implementation | LangChain + Qdrant Cloud | Pre-built RAG patterns, free tier vector storage, <1s search |
| AI Model | OpenAI GPT-4 + text-embedding-3-small | Quality, cost balance, multilingual, technical domain strength |
| Database | Neon Serverless Postgres | Free tier, Postgres features, <200ms queries, branching |
| Authentication | Better-auth.com | Secure by default, custom fields, rate limiting, GDPR compliant |
| Translation | GPT-4 with Urdu prompts | Context-aware, technical term handling, markdown preservation |
| State Management | React Context API | Simplicity, zero bundle size impact, sufficient for use case |
| Styling | Docusaurus CSS + Tailwind | Theme system, RTL support, rapid prototyping, minimal bundle |
| Testing | Jest + Playwright + pytest | Component, E2E, backend coverage, multi-browser, async support |
| Deployment | Vercel (unified) | Free tier, serverless, CDN, unified pipeline, GitHub integration |
| CI/CD | GitHub Actions | Free, integrated, pre-built workflows, branch protection |

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Browser                             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Docusaurus Static Site (React + TypeScript)             │  │
│  │  - Textbook chapters (markdown)                          │  │
│  │  - Chatbot widget, Quiz, Auth forms                      │  │
│  │  - Language toggle (EN/UR), Personalization button      │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │ HTTPS
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Vercel Edge Network                         │
│  ┌────────────────┐           ┌──────────────────────────────┐ │
│  │  Static Assets │           │  Serverless Functions        │ │
│  │  (CDN Cached)  │           │  (FastAPI Python Runtime)    │ │
│  │  - HTML        │           │  - /api/chat (RAG)           │ │
│  │  - CSS/JS      │           │  - /api/quiz (generation)    │ │
│  │  - Images      │           │  - /api/auth (login/signup)  │ │
│  └────────────────┘           │  - /api/personalize          │ │
│                               │  - /api/translate            │ │
│                               └──────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │       External Services                  │
        │  ┌──────────────────────────────────┐  │
        │  │  OpenAI API                       │  │
        │  │  - GPT-4 (RAG, quiz, translate)  │  │
        │  │  - text-embedding-3-small        │  │
        │  └──────────────────────────────────┘  │
        │  ┌──────────────────────────────────┐  │
        │  │  Qdrant Cloud (Vector Store)     │  │
        │  │  - Chapter embeddings             │  │
        │  │  - Semantic search                │  │
        │  └──────────────────────────────────┘  │
        │  ┌──────────────────────────────────┐  │
        │  │  Neon Serverless Postgres        │  │
        │  │  - Users, Progress, Chats        │  │
        │  │  - Bookmarks                      │  │
        │  └──────────────────────────────────┘  │
        │  ┌──────────────────────────────────┐  │
        │  │  Better-auth.com                 │  │
        │  │  - Auth, JWT tokens              │  │
        │  └──────────────────────────────────┘  │
        └─────────────────────────────────────────┘
```

---

## Risk Mitigation

### Risk 1: OpenAI API Rate Limits (60 req/min standard tier)
- **Mitigation**: Implement caching for common queries, rate limiting on client side, queue system for quiz generation
- **Fallback**: Display cached responses or friendly error message during high traffic

### Risk 2: Qdrant/Neon Free Tier Limits
- **Mitigation**: Monitor usage, compress embeddings, implement soft limits before hitting hard limits
- **Upgrade Path**: Paid tiers affordable ($10-20/month) if project succeeds

### Risk 3: Translation Quality (GPT-4 hallucinations)
- **Mitigation**: Validate translations with Urdu speaker, cache approved translations, fall back to English on error
- **Quality Check**: Sample review of key technical terms (ROS 2, NVIDIA Isaac, etc.)

### Risk 4: Performance (<3s page load, <2s chatbot)
- **Mitigation**: Lighthouse CI checks, caching strategy, lazy loading, code splitting
- **Monitoring**: Add performance monitoring (Vercel Analytics) to catch regressions

### Risk 5: Accessibility (95+ Lighthouse score)
- **Mitigation**: Lighthouse CI in GitHub Actions, manual screen reader testing, ARIA labels
- **Testing**: Test with NVDA (Windows), VoiceOver (Mac), keyboard navigation

---

## Next Steps (Phase 1)

1. **data-model.md**: Define database schemas, entity relationships, indexes
2. **contracts/**: Generate OpenAPI specifications for all API endpoints
3. **quickstart.md**: Write developer setup guide (local development, environment variables, running tests)
4. **Update agent context**: Run `.specify/scripts/bash/update-agent-context.sh` to add technology stack to agent memory

---

**Phase 0 Complete**: All technology decisions resolved with rationale. Ready to proceed to Phase 1 (Design & Contracts).
