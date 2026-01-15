---
id: 0002
title: Design AI Textbook Architecture
stage: plan
date: 2026-01-09
surface: agent
model: claude-sonnet-4-5-20250929
feature: 001-docusaurus-textbook
branch: 001-docusaurus-textbook
user: system
command: /sp.plan
labels: ["architecture", "planning", "technology-stack", "api-design", "data-model"]
links:
  spec: specs/001-docusaurus-textbook/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/001-docusaurus-textbook/plan.md
 - specs/001-docusaurus-textbook/research.md
 - specs/001-docusaurus-textbook/data-model.md
 - specs/001-docusaurus-textbook/quickstart.md
 - specs/001-docusaurus-textbook/contracts/openapi.yaml
tests:
 - Constitution Check: PASSED (all 6 core principles aligned)
 - Technology stack validated against requirements
---

## Prompt

User command: `/sp.plan`

The user requested creation of an implementation plan for the AI-powered textbook feature specified in specs/001-docusaurus-textbook/spec.md. The plan should include:
- Technical context (languages, dependencies, platform, constraints)
- Constitution compliance check
- Project structure (frontend/backend separation)
- Phase 0: Research and technology decisions with rationale
- Phase 1: Data model, API contracts, and developer quickstart guide

The plan must align with the project constitution's core principles (Accessibility First, AI-Enhanced Learning, Personalization Without Bias, Technical Excellence, Content Integrity, User Experience Excellence) and meet performance targets (<3s page load, <2s chatbot response, 100+ concurrent users).

## Response snapshot

Successfully created comprehensive implementation plan with architecture decisions:

1. **Plan.md** (333 lines):
   - Technical Context: Docusaurus v3 (frontend), FastAPI Python 3.11+ (backend), Neon Postgres, Qdrant Cloud, OpenAI GPT-4
   - Constitution Check: ✅ PASSED all 6 core principles
   - Project Structure: Web application with frontend/backend separation, detailed directory layout
   - Complexity Tracking: All complexity justified by functional requirements

2. **Research.md** (12 technology decisions with rationale):
   - Static Site Generator: Docusaurus v3 (SSG performance, React integration, i18n support)
   - Backend Framework: FastAPI (async/await, performance, OpenAI/LangChain compatibility)
   - RAG Implementation: LangChain + Qdrant Cloud (pre-built patterns, free tier 1GB vectors)
   - AI Model: GPT-4 for generation, text-embedding-3-small for embeddings (quality vs cost)
   - Database: Neon Serverless Postgres (free tier 0.5GB, branching for migrations)
   - Authentication: Better-auth.com (secure by default, custom fields for questionnaire)
   - Translation: GPT-4 with Urdu prompts (technical term handling, context-aware)
   - State Management: React Context API (simplicity, sufficient for use case)
   - Styling: Docusaurus CSS + Tailwind (RTL support, minimal bundle)
   - Testing: Jest + Playwright + pytest (component, E2E, backend coverage)
   - Deployment: Vercel (unified frontend+backend, free tier, CDN)
   - CI/CD: GitHub Actions (free, integrated, pre-built workflows)

3. **Data-Model.md** (10 entities with complete schemas):
   - Core: users, user_profiles, user_progress, chat_conversations, chat_messages, user_bookmarks
   - Quiz: quizzes, quiz_questions, quiz_attempts, quiz_responses
   - PostgreSQL schemas with indexes, constraints, Pydantic models
   - Migration strategy with Alembic
   - GDPR compliance (soft delete, data export, right to erasure)

4. **Contracts/openapi.yaml** (850+ lines OpenAPI 3.0):
   - 7 API categories: Authentication, Chatbot, Quiz, Progress, Personalization, Translation, User
   - 25+ endpoints with complete request/response schemas
   - Security: Bearer JWT authentication
   - Comprehensive error handling and rate limiting

5. **Quickstart.md** (Developer guide):
   - Prerequisites and environment setup
   - Local development workflow (frontend + backend)
   - Testing strategies (unit, integration, E2E)
   - Deployment instructions (Vercel, GitHub Pages)
   - Common tasks (adding chapters, generating quizzes, migrations)
   - Troubleshooting guide

Key Architecture Decisions:
- Hybrid architecture: Static site (Docusaurus) for content + Serverless functions (FastAPI) for AI services
- Free tier services: Qdrant (1GB), Neon (0.5GB), Better-auth, Vercel hosting
- Performance optimizations: CDN caching, vector search caching, lazy loading, code splitting
- Security: AES-256 encryption, TLS 1.3, bcrypt password hashing, rate limiting
- Scalability: Async FastAPI, connection pooling, 100+ concurrent users supported

## Outcome

- ✅ Impact: Complete architectural foundation ready for implementation. All technical decisions documented with rationale, alternatives considered, and alignment with requirements. Zero architectural ambiguities remaining. Plan enables immediate start of development with clear guidance on structure, technologies, and deployment.
- 🧪 Tests: Constitution Check validation passed (6/6 principles aligned). Technology stack validated against 33 functional requirements and 15 success criteria.
- 📁 Files: Created plan.md (architecture overview), research.md (12 technology decisions), data-model.md (10 entities with schemas), openapi.yaml (25+ endpoints), quickstart.md (developer guide), updated CLAUDE.md with technology stack
- 🔁 Next prompts: `/sp.tasks` to break down implementation into concrete, testable tasks with TDD approach, or begin implementation of P1 features (Core Textbook + RAG Chatbot)
- 🧠 Reflection: Successfully designed a pragmatic, cost-effective architecture leveraging free tiers while meeting aggressive performance targets (<3s load, <2s chatbot). The hybrid approach (static site + serverless functions) optimally separates concerns: content delivery via CDN for speed, AI processing via backend for flexibility. All 12 technology decisions justified against alternatives, avoiding over-engineering while ensuring scalability to 100+ concurrent users.

## Evaluation notes (flywheel)

- Failure modes observed: None - planning completed without architectural blockers or unresolved technical questions
- Graders run and results (PASS/FAIL): Constitution Check - PASS (6/6 principles), Technology Stack Validation - PASS (aligns with all 33 functional requirements), Performance Target Feasibility - PASS (architecture supports <3s load, <2s chatbot with caching and CDN)
- Prompt variant (if applicable): Standard spec-driven development workflow with Phase 0 (Research) and Phase 1 (Design) separation
- Next experiment (smallest change to try): For future planning phases, consider adding a "Performance Budget" section to plan.md explicitly allocating milliseconds/bytes to each system component (e.g., Frontend: 2500ms budget → Docusaurus SSG: 1500ms, React hydration: 500ms, API calls: 500ms). This would make performance targets more actionable during implementation.
