# Developer Quickstart Guide

**Feature**: AI-Powered Physical AI & Humanoid Robotics Textbook
**Branch**: `001-docusaurus-textbook`
**Last Updated**: 2026-01-09

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Local Development](#local-development)
4. [Running Tests](#running-tests)
5. [Deployment](#deployment)
6. [Common Tasks](#common-tasks)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

- **Node.js**: 18+ (LTS recommended)
  ```bash
  node --version  # Should be v18.x or higher
  npm --version   # Should be 9.x or higher
  ```

- **Python**: 3.11+
  ```bash
  python --version  # Should be 3.11.x or higher
  pip --version
  ```

- **Git**: Latest version
  ```bash
  git --version
  ```

### Recommended Tools

- **VS Code**: With extensions
  - Python (ms-python.python)
  - ESLint (dbaeumer.vscode-eslint)
  - Prettier (esbenp.prettier-vscode)
  - Thunder Client (rangav.vscode-thunder-client) - for API testing

- **PostgreSQL Client**: For database inspection (optional)
  ```bash
  psql --version
  ```

### External Services (Free Tiers)

You'll need API keys/credentials for:

1. **OpenAI API**: https://platform.openai.com/api-keys
   - Create account and generate API key
   - Free tier: $5 credit for new users
   - Standard tier: $0.03 per chatbot message

2. **Neon Serverless Postgres**: https://neon.tech
   - Sign up for free tier (0.5GB storage)
   - Create project and copy connection string

3. **Qdrant Cloud**: https://cloud.qdrant.io
   - Free tier: 1GB vector storage
   - Create cluster and get API key + URL

4. **Better-auth.com**: https://better-auth.com
   - Sign up for free tier
   - Create application and get client ID + secret

---

## Environment Setup

### 1. Clone Repository

```bash
git clone https://github.com/your-org/ai-textbook.git
cd ai-textbook
git checkout 001-docusaurus-textbook
```

### 2. Install Dependencies

**Frontend (Docusaurus)**:
```bash
npm install
```

**Backend (FastAPI)**:
```bash
cd backend
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Configure Environment Variables

**Root `.env` (Frontend)**:
```env
# .env
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_BETTER_AUTH_CLIENT_ID=your_client_id_here
```

**Backend `.env`**:
```env
# backend/.env

# Database
DATABASE_URL=postgresql://user:password@hostname/dbname?sslmode=require
# Example: postgresql://user:pass@ep-cool-moon-12345.us-east-2.aws.neon.tech/neondb?sslmode=require

# OpenAI
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4-turbo
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# Qdrant
QDRANT_URL=https://your-cluster.eu-central.aws.cloud.qdrant.io
QDRANT_API_KEY=your_qdrant_api_key

# Better Auth
BETTER_AUTH_CLIENT_ID=your_client_id
BETTER_AUTH_CLIENT_SECRET=your_client_secret
BETTER_AUTH_REDIRECT_URI=http://localhost:3000/auth/callback

# JWT
JWT_SECRET=your_random_secret_key_here_min_32_chars
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# App Config
ENVIRONMENT=development
LOG_LEVEL=DEBUG
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

**Generate JWT Secret**:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 4. Initialize Database

**Run Alembic Migrations**:
```bash
cd backend
alembic upgrade head
```

**Seed Test Data** (optional for development):
```bash
python scripts/seed_database.py
```

This creates:
- 2 test users (beginner@example.com / advanced@example.com, password: "TestPass123")
- Sample progress data
- Sample chat conversations

### 5. Index Textbook Content (Vector Embeddings)

```bash
cd backend
python scripts/index_chapters.py
```

This:
1. Reads all markdown files from `docs/` directory
2. Splits chapters into ~500-token chunks
3. Generates embeddings using OpenAI `text-embedding-3-small`
4. Uploads to Qdrant Cloud
5. Prints summary: `Indexed 13 chapters, 487 chunks, 1.2MB vectors`

**Estimated time**: 2-3 minutes for 13 chapters
**Estimated cost**: ~$0.10 for embeddings

---

## Local Development

### Frontend (Docusaurus)

**Start Development Server**:
```bash
npm start
```

- Opens browser at http://localhost:3000
- Hot reload enabled (changes reflect instantly)
- Access chatbot, quiz, auth features (requires backend running)

**Build for Production**:
```bash
npm run build
```

- Generates static files in `build/` directory
- Optimized, minified, ready for deployment

**Serve Production Build Locally**:
```bash
npm run serve
```

- Serves `build/` directory at http://localhost:3000
- Test production build before deployment

### Backend (FastAPI)

**Start Development Server**:
```bash
cd backend
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

- API available at http://localhost:8000
- Interactive API docs at http://localhost:8000/docs (Swagger UI)
- Alternative docs at http://localhost:8000/redoc (ReDoc)

**Hot Reload**: FastAPI auto-reloads on file changes

### Concurrent Development

Use **two terminals**:

**Terminal 1 (Frontend)**:
```bash
npm start
```

**Terminal 2 (Backend)**:
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn src.main:app --reload
```

---

## Running Tests

### Frontend Tests

**Unit Tests (Jest + React Testing Library)**:
```bash
npm test
```

- Runs all tests in `src/**/*.test.tsx`
- Watch mode: `npm test -- --watch`
- Coverage: `npm test -- --coverage`

**Component Tests**:
```bash
npm test -- Chatbot  # Test specific component
```

**Lint Check**:
```bash
npm run lint
```

**Type Check**:
```bash
npm run type-check
```

### Backend Tests

**Unit Tests (pytest)**:
```bash
cd backend
pytest tests/unit -v
```

**Integration Tests**:
```bash
pytest tests/integration -v
```

**Contract Tests** (validate OpenAPI compliance):
```bash
pytest tests/contract -v
```

**All Tests with Coverage**:
```bash
pytest --cov=src --cov-report=html
```

- Coverage report in `backend/htmlcov/index.html`

**Test Specific Module**:
```bash
pytest tests/unit/test_rag_service.py -v
```

### E2E Tests (Playwright)

**Install Playwright Browsers** (first time only):
```bash
npx playwright install
```

**Run E2E Tests**:
```bash
npm run test:e2e
```

- Tests full user journeys (chatbot, quiz, translation)
- Requires frontend and backend running

**Headless Mode**:
```bash
npm run test:e2e:headless
```

**Debug Mode** (see browser):
```bash
npx playwright test --debug
```

### CI/CD Simulation

**Run All Checks Locally** (before pushing):
```bash
# Frontend
npm run lint
npm test -- --coverage
npm run build

# Backend
cd backend
black src/ --check
flake8 src/
mypy src/
pytest --cov=src
```

---

## Deployment

### Vercel Deployment

**Prerequisites**:
- Vercel account: https://vercel.com/signup
- Vercel CLI: `npm install -g vercel`
- GitHub repository linked to Vercel

**One-Time Setup**:

1. **Link Project to Vercel**:
   ```bash
   vercel link
   ```

2. **Add Environment Variables** (Vercel Dashboard):
   - Go to Project Settings → Environment Variables
   - Add all variables from `backend/.env` (production values)
   - Mark secrets as "Sensitive" (encrypted)

3. **Configure Build Settings** (`vercel.json`):
   ```json
   {
     "buildCommand": "npm run build",
     "outputDirectory": "build",
     "devCommand": "npm start",
     "installCommand": "npm install",
     "framework": "docusaurus",
     "functions": {
       "api/**/*.py": {
         "runtime": "python3.11"
       }
     },
     "routes": [
       { "src": "/api/(.*)", "dest": "/api/main.py" },
       { "src": "/(.*)", "dest": "/$1" }
     ]
   }
   ```

**Deploy**:

**Manual Deployment**:
```bash
vercel --prod
```

**Automatic Deployment** (GitHub Integration):
- Push to `main` branch triggers production deployment
- Pull requests create preview deployments

**Check Deployment**:
- Production URL: `https://your-project.vercel.app`
- View logs: `vercel logs <deployment-url>`

### GitHub Pages (Alternative for Frontend Only)

**Build and Deploy**:
```bash
npm run build
GIT_USER=<your-github-username> npm run deploy
```

- Deploys to `gh-pages` branch
- Available at `https://<username>.github.io/<repo-name>`

**Note**: Backend must be deployed separately (Fly.io, Railway, Render)

---

## Common Tasks

### Adding a New Chapter

1. **Create Markdown File**:
   ```bash
   touch docs/module-1-ros2/chapter-06-new-topic.md
   ```

2. **Add Frontmatter**:
   ```markdown
   ---
   id: chapter-06-new-topic
   title: "New ROS 2 Topic"
   module: 1
   week: 6
   learning_objectives:
     - Objective 1
     - Objective 2
   estimated_time_minutes: 30
   ---

   # New ROS 2 Topic

   Content here...
   ```

3. **Update Sidebar** (`sidebars.js`):
   ```javascript
   module.exports = {
     tutorialSidebar: [
       {
         type: 'category',
         label: 'Module 1: ROS 2',
         items: [
           'module-1-ros2/chapter-01-intro',
           // ... other chapters
           'module-1-ros2/chapter-06-new-topic', // Add here
         ],
       },
     ],
   };
   ```

4. **Re-index for RAG**:
   ```bash
   cd backend
   python scripts/index_chapters.py --chapter chapter-06-new-topic
   ```

5. **Generate Quiz**:
   ```bash
   python scripts/generate_quiz.py --chapter chapter-06-new-topic
   ```

### Regenerating Quizzes

**Single Chapter**:
```bash
cd backend
python scripts/generate_quiz.py --chapter chapter-03-ros2-topics
```

**All Chapters**:
```bash
python scripts/generate_quiz.py --all
```

**Options**:
- `--difficulty beginner|intermediate|advanced` - Target difficulty
- `--num-questions 5` - Number of questions (default: 7)

### Updating Translations

**Translate New Content**:
```bash
cd backend
python scripts/translate_chapter.py --chapter chapter-06-new-topic --target ur
```

**Batch Translate**:
```bash
python scripts/translate_chapter.py --all --target ur
```

**Cache Management**:
- Translations cached in Postgres `translations` table
- Clear cache: `python scripts/clear_translation_cache.py`

### Database Migrations

**Create New Migration**:
```bash
cd backend
alembic revision --autogenerate -m "Add new_table"
```

**Review Migration**:
```bash
cat alembic/versions/001_add_new_table.py
```

**Apply Migration**:
```bash
alembic upgrade head
```

**Rollback Migration**:
```bash
alembic downgrade -1  # Rollback one version
```

**Migration Best Practices**:
- Always review auto-generated migrations
- Test on development database first
- Use Neon branching for safe testing

### Monitoring OpenAI API Usage

**Check Token Usage**:
```bash
cd backend
python scripts/check_api_usage.py --days 7
```

Output:
```
OpenAI API Usage (Last 7 Days)
================================
Chatbot: 142,350 tokens ($4.27)
Quiz Generation: 28,940 tokens ($0.87)
Translation: 67,200 tokens ($2.02)
Personalization: 45,100 tokens ($1.35)
--------------------------------
Total: 283,590 tokens ($8.51)
```

**Set Budget Alert**:
```bash
python scripts/set_budget_alert.py --limit 50 --email your@email.com
```

---

## Troubleshooting

### Frontend Issues

**Problem**: `npm start` fails with "Port 3000 already in use"

**Solution**:
```bash
# Find and kill process on port 3000
# Windows:
netstat -ano | findstr :3000
taskkill /PID <process_id> /F

# macOS/Linux:
lsof -ti:3000 | xargs kill -9
```

**Problem**: Chatbot not connecting to backend

**Solution**:
1. Verify backend is running: http://localhost:8000/docs
2. Check `.env` has correct `REACT_APP_API_URL=http://localhost:8000/api`
3. Check browser console for CORS errors
4. Verify `backend/.env` has `CORS_ORIGINS=http://localhost:3000`

**Problem**: Build fails with "JavaScript heap out of memory"

**Solution**:
```bash
export NODE_OPTIONS="--max-old-space-size=4096"
npm run build
```

### Backend Issues

**Problem**: `uvicorn` fails with "Address already in use"

**Solution**:
```bash
# Kill process on port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <process_id> /F

# macOS/Linux:
lsof -ti:8000 | xargs kill -9
```

**Problem**: Database connection fails

**Solution**:
1. Verify connection string in `backend/.env`
2. Check Neon dashboard - database active?
3. Test connection:
   ```bash
   psql "postgresql://user:pass@hostname/dbname?sslmode=require"
   ```
4. Check firewall/VPN not blocking connection

**Problem**: OpenAI API rate limit exceeded

**Solution**:
1. Check current usage: https://platform.openai.com/usage
2. Implement caching (already in place for translations/quizzes)
3. Add exponential backoff:
   ```python
   from tenacity import retry, wait_exponential

   @retry(wait=wait_exponential(multiplier=1, min=4, max=10))
   async def call_openai_api():
       # API call here
   ```

**Problem**: Qdrant vector search slow (>2s)

**Solution**:
1. Check Qdrant Cloud dashboard - cluster status?
2. Verify index created: `python scripts/check_qdrant_status.py`
3. Reduce `top_k` parameter (currently 3, try 2)
4. Check network latency: `ping your-cluster.cloud.qdrant.io`

### Testing Issues

**Problem**: Playwright tests fail with "Browser not found"

**Solution**:
```bash
npx playwright install chromium firefox webkit
```

**Problem**: pytest fails with "No module named 'src'"

**Solution**:
```bash
cd backend
pip install -e .  # Install package in editable mode
```

**Problem**: Tests pass locally but fail in CI

**Solution**:
1. Check environment variables set in GitHub Secrets
2. Verify database migrations run in CI:
   ```yaml
   # .github/workflows/backend-ci.yml
   - name: Run migrations
     run: alembic upgrade head
   ```
3. Check test isolation (tests modifying shared state?)

### Deployment Issues

**Problem**: Vercel deployment fails with "Build exceeded time limit"

**Solution**:
1. Optimize build: Remove unused dependencies
2. Increase timeout in Vercel dashboard (Project Settings → General → Build Timeout)
3. Split build:
   ```json
   {
     "builds": [
       { "src": "package.json", "use": "@vercel/static-build" },
       { "src": "api/**/*.py", "use": "@vercel/python" }
     ]
   }
   ```

**Problem**: Backend 500 errors in production

**Solution**:
1. Check Vercel function logs: `vercel logs --follow`
2. Verify environment variables set correctly
3. Test production build locally:
   ```bash
   vercel dev
   ```
4. Check OpenAI API key valid and has credits

---

## Additional Resources

### Documentation

- **Docusaurus**: https://docusaurus.io/docs
- **FastAPI**: https://fastapi.tiangolo.com
- **LangChain**: https://python.langchain.com/docs
- **Qdrant**: https://qdrant.tech/documentation
- **Neon**: https://neon.tech/docs
- **Playwright**: https://playwright.dev/docs/intro

### Scripts Reference

Located in `backend/scripts/`:

- `index_chapters.py` - Generate vector embeddings for chapters
- `generate_quiz.py` - Auto-generate quizzes using GPT-4
- `translate_chapter.py` - Translate chapters to Urdu
- `seed_database.py` - Create test data
- `check_api_usage.py` - Monitor OpenAI API costs
- `clear_caches.py` - Clear translation/quiz caches
- `check_qdrant_status.py` - Verify vector store health

### Support

- **GitHub Issues**: https://github.com/your-org/ai-textbook/issues
- **Slack Channel**: #ai-textbook-dev
- **Email**: dev-support@example.com

---

## Quick Reference

### Environment Variables Checklist

**Frontend `.env`**:
```
✓ REACT_APP_API_URL
✓ REACT_APP_BETTER_AUTH_CLIENT_ID
```

**Backend `.env`**:
```
✓ DATABASE_URL
✓ OPENAI_API_KEY
✓ OPENAI_MODEL
✓ OPENAI_EMBEDDING_MODEL
✓ QDRANT_URL
✓ QDRANT_API_KEY
✓ BETTER_AUTH_CLIENT_ID
✓ BETTER_AUTH_CLIENT_SECRET
✓ JWT_SECRET
✓ CORS_ORIGINS
```

### Port Reference

- **3000**: Frontend (Docusaurus)
- **8000**: Backend (FastAPI)
- **5432**: PostgreSQL (Neon - remote)
- **6333**: Qdrant (Cloud - remote)

### Key Commands

```bash
# Development
npm start                          # Start frontend
uvicorn src.main:app --reload     # Start backend

# Testing
npm test                          # Frontend tests
pytest                            # Backend tests
npm run test:e2e                  # E2E tests

# Deployment
vercel --prod                     # Deploy to Vercel
npm run deploy                    # Deploy to GitHub Pages

# Database
alembic upgrade head              # Run migrations
python scripts/seed_database.py  # Seed test data

# Content
python scripts/index_chapters.py  # Index for RAG
python scripts/generate_quiz.py   # Generate quizzes
```

---

**Need Help?** Check troubleshooting section or contact the team on Slack (#ai-textbook-dev).
