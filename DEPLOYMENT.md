# Deployment Configuration Guide

## AI-Powered Physical AI & Humanoid Robotics Textbook

This guide provides complete deployment instructions for the textbook platform with RAG chatbot, authentication, and text selection AI features.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Configuration](#environment-configuration)
3. [Database Setup](#database-setup)
4. [Vector Database Setup](#vector-database-setup)
5. [Backend Deployment](#backend-deployment)
6. [Frontend Deployment](#frontend-deployment)
7. [Verification & Testing](#verification--testing)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Accounts

- **Neon Postgres** - Serverless PostgreSQL database ([neon.tech](https://neon.tech))
- **Qdrant Cloud** - Vector database for RAG ([cloud.qdrant.io](https://cloud.qdrant.io))
- **OpenAI** - GPT-4 and embeddings API ([platform.openai.com](https://platform.openai.com))
- **Vercel** (optional) - Frontend hosting ([vercel.com](https://vercel.com))
- **Render/Railway** (optional) - Backend hosting ([render.com](https://render.com) or [railway.app](https://railway.app))

### Local Development Tools

```bash
# Node.js 18+ and npm
node --version  # v18.0.0+
npm --version   # 9.0.0+

# Python 3.11+
python --version  # 3.11.0+

# Git
git --version
```

---

## Environment Configuration

### 1. Backend Environment Variables

Create `backend/.env` with the following configuration:

```bash
# Database Configuration (Neon Postgres)
DATABASE_URL=postgresql+asyncpg://[user]:[password]@[host]/[database]?sslmode=require

# Example:
# DATABASE_URL=postgresql+asyncpg://user:password@ep-cool-morning-12345.us-east-2.aws.neon.tech/textbook_db?sslmode=require

# Vector Database (Qdrant Cloud)
QDRANT_URL=https://[cluster-id].us-east-1-0.aws.cloud.qdrant.io:6333
QDRANT_API_KEY=your_qdrant_api_key_here

# OpenAI API
OPENAI_API_KEY=sk-proj-...your_openai_api_key_here

# JWT Authentication
JWT_SECRET_KEY=your_very_long_random_secret_key_here_min_32_chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Application Settings
ENVIRONMENT=production
CORS_ORIGINS=https://your-frontend-domain.com,http://localhost:3000

# Optional: Logging
LOG_LEVEL=INFO
```

### 2. Frontend Environment Variables

Create `frontend/.env` for local development:

```bash
REACT_APP_API_URL=http://localhost:8000/api
```

Create `frontend/.env.production` for production:

```bash
REACT_APP_API_URL=https://your-backend-domain.com/api
```

---

## Database Setup

### 1. Create Neon Postgres Database

1. Sign up at [neon.tech](https://neon.tech)
2. Create a new project
3. Create a database named `textbook_db`
4. Copy the connection string (select "Pooled connection" and "asyncpg")
5. Update `DATABASE_URL` in `backend/.env`

### 2. Run Database Migrations

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run Alembic migrations
alembic upgrade head
```

**Expected output:**
```
INFO  [alembic.runtime.migration] Running upgrade -> 001_initial_schema
INFO  [alembic.runtime.migration] Running upgrade 001 -> 002_auth_and_progress
```

### 3. Verify Database Tables

Connect to your Neon database and verify tables were created:

```sql
-- Expected tables:
-- - chapters
-- - chat_conversations
-- - chat_messages
-- - users
-- - user_profiles
-- - user_progress
-- - quiz_attempts
-- - bookmarks

SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public';
```

---

## Vector Database Setup

### 1. Create Qdrant Cloud Cluster

1. Sign up at [cloud.qdrant.io](https://cloud.qdrant.io)
2. Create a new cluster (Free tier: 1GB storage)
3. Note the cluster URL and API key
4. Update `QDRANT_URL` and `QDRANT_API_KEY` in `backend/.env`

### 2. Index Textbook Chapters

Run the chapter indexing script to populate Qdrant with chapter content:

```bash
cd backend

# Ensure .env is configured with QDRANT_URL, QDRANT_API_KEY, OPENAI_API_KEY
python scripts/index_chapters.py
```

**Expected output:**
```
[INFO] Connecting to Qdrant at https://...
[INFO] Creating collection 'chapters' with vector size 1536
[INFO] Indexing chapter: chapter-01-physical-ai-intro.md
[INFO] - Generated 12 chunks
[INFO] Indexing chapter: chapter-02-ros2-fundamentals.md
[INFO] - Generated 15 chunks
...
[INFO] Successfully indexed 13 chapters (156 total chunks)
[INFO] Average chunk size: 450 tokens
[INFO] Indexing complete!
```

### 3. Verify Qdrant Collection

```python
# Test script: test_qdrant.py
from qdrant_client import QdrantClient
import os

client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

# Check collection
collection_info = client.get_collection("chapters")
print(f"Collection size: {collection_info.points_count} points")
print(f"Vector size: {collection_info.config.params.vectors.size}")
```

---

## Backend Deployment

### Option 1: Local Development

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run with uvicorn
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

Access API at `http://localhost:8000`
View API docs at `http://localhost:8000/docs`

### Option 2: Production (Render.com)

1. **Create `render.yaml`** in project root:

```yaml
services:
  - type: web
    name: textbook-api
    env: python
    region: oregon
    buildCommand: "cd backend && pip install -r requirements.txt"
    startCommand: "cd backend && uvicorn src.main:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: DATABASE_URL
        sync: false
      - key: QDRANT_URL
        sync: false
      - key: QDRANT_API_KEY
        sync: false
      - key: OPENAI_API_KEY
        sync: false
      - key: JWT_SECRET_KEY
        generateValue: true
      - key: ENVIRONMENT
        value: production
      - key: CORS_ORIGINS
        value: https://your-frontend-domain.vercel.app
```

2. **Deploy to Render:**
   - Push code to GitHub
   - Connect repository to Render
   - Add environment variables in Render dashboard
   - Deploy service

### Option 3: Production (Railway.app)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and init
railway login
railway init

# Deploy
cd backend
railway up
```

Add environment variables in Railway dashboard.

---

## Frontend Deployment

### Option 1: Local Development

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm start
```

Access at `http://localhost:3000`

### Option 2: Production (Vercel)

1. **Install Vercel CLI:**

```bash
npm install -g vercel
```

2. **Configure `vercel.json`:**

```json
{
  "version": 2,
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "build"
      }
    }
  ],
  "routes": [
    {
      "src": "/static/(.*)",
      "dest": "/static/$1"
    },
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ]
}
```

3. **Deploy:**

```bash
cd frontend

# Build production bundle
npm run build

# Deploy to Vercel
vercel --prod
```

4. **Set environment variable in Vercel dashboard:**
   - `REACT_APP_API_URL` = `https://your-backend-domain.com/api`

---

## Verification & Testing

### 1. Backend Health Check

```bash
# Test API is running
curl https://your-backend-domain.com/health

# Expected response:
# {"status": "healthy", "version": "1.0.0"}
```

### 2. Database Connectivity

```bash
# Test database connection
curl https://your-backend-domain.com/api/health/db

# Expected: {"status": "connected"}
```

### 3. RAG Chatbot Test

```bash
# Send test message
curl -X POST https://your-backend-domain.com/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": null,
    "message": "What are ROS 2 topics?",
    "language": "en"
  }'

# Expected: Response with explanation and citations
```

### 4. Text Selection API Test

```bash
curl -X POST https://your-backend-domain.com/api/chat/text-selection \
  -H "Content-Type: application/json" \
  -d '{
    "selected_text": "URDF format",
    "chapter_id": "chapter-06-gazebo-intro",
    "language": "en"
  }'

# Expected: Contextual explanation with citations
```

### 5. Frontend Verification

1. **Navigate to deployed URL**
2. **Test features:**
   - ✅ Chapters load correctly
   - ✅ Chatbot widget appears (bottom-right corner)
   - ✅ Send a question, verify response with citations
   - ✅ Select text in a chapter, click "Ask AI", verify explanation
   - ✅ Sign up / Login functionality
   - ✅ User menu shows after login
   - ✅ Progress tracking works

### 6. Performance Checks

```bash
# Lighthouse audit (run in Chrome DevTools)
# Expected scores:
# - Performance: 90+
# - Accessibility: 95+
# - Best Practices: 90+
# - SEO: 90+
```

---

## Troubleshooting

### Issue: Database Migration Fails

**Symptom:** `alembic upgrade head` fails with connection error

**Solution:**
1. Verify `DATABASE_URL` in `.env` is correct
2. Check Neon database is running (not paused)
3. Verify SSL mode: `?sslmode=require`
4. Test connection:
   ```python
   import asyncpg
   import asyncio

   async def test():
       conn = await asyncpg.connect("postgresql://...")
       print(await conn.fetchval("SELECT version()"))

   asyncio.run(test())
   ```

### Issue: Qdrant Indexing Fails

**Symptom:** `index_chapters.py` fails with authentication error

**Solution:**
1. Verify `QDRANT_API_KEY` is correct
2. Check cluster is active (not hibernated in free tier)
3. Verify cluster URL includes port `:6333`
4. Test connection:
   ```python
   from qdrant_client import QdrantClient
   client = QdrantClient(url="...", api_key="...")
   print(client.get_collections())
   ```

### Issue: OpenAI API Rate Limits

**Symptom:** "Rate limit exceeded" errors

**Solution:**
1. Check OpenAI usage limits: [platform.openai.com/usage](https://platform.openai.com/usage)
2. Implement exponential backoff (already in `ChatbotService.ts`)
3. Add caching for common queries
4. Reduce `top_k` in RAG retrieval (current: 3)

### Issue: CORS Errors in Production

**Symptom:** Browser shows "CORS policy" error

**Solution:**
1. Verify `CORS_ORIGINS` in backend `.env` includes frontend URL
2. Add frontend domain:
   ```bash
   CORS_ORIGINS=https://textbook-frontend.vercel.app
   ```
3. Restart backend service
4. Clear browser cache

### Issue: JWT Token Expired

**Symptom:** User logged out unexpectedly

**Solution:**
1. Check `ACCESS_TOKEN_EXPIRE_MINUTES` in `.env` (default: 1440 = 24 hours)
2. Increase token lifetime if needed
3. Implement refresh token mechanism (future enhancement)

### Issue: Chatbot Not Responding

**Symptom:** Chatbot shows loading spinner indefinitely

**Solution:**
1. Check browser console for errors
2. Verify `REACT_APP_API_URL` points to correct backend
3. Test backend API directly (see Verification section)
4. Check OpenAI API key is valid
5. Verify Qdrant collection has indexed chapters

---

## Deployment Checklist

Use this checklist before going live:

### Backend
- [ ] Environment variables configured in `.env`
- [ ] Database migrations run successfully (`alembic upgrade head`)
- [ ] Qdrant collection created and indexed
- [ ] OpenAI API key valid and has credits
- [ ] JWT secret key is strong (32+ random characters)
- [ ] CORS origins include frontend domain
- [ ] Health endpoint returns 200 OK
- [ ] API documentation accessible at `/docs`

### Frontend
- [ ] `REACT_APP_API_URL` points to production backend
- [ ] Production build completed (`npm run build`)
- [ ] Static assets served correctly
- [ ] Chatbot widget visible on all pages
- [ ] Text selection tooltip works on chapter pages
- [ ] Auth forms functional (signup/login)
- [ ] User menu displays after login
- [ ] Lighthouse scores meet targets (90+)

### Testing
- [ ] Chatbot responds to test questions
- [ ] Citations display correctly
- [ ] Text selection explanations work
- [ ] User signup/login flow complete
- [ ] Progress tracking persists across sessions
- [ ] Mobile responsive design verified
- [ ] Cross-browser testing (Chrome, Firefox, Safari)

### Monitoring
- [ ] Database monitoring enabled (Neon dashboard)
- [ ] API error logging configured
- [ ] OpenAI usage tracking setup
- [ ] Qdrant storage limits monitored
- [ ] Application analytics (optional: Google Analytics)

---

## Production URLs

After deployment, update these placeholders:

```bash
# Backend API
Production API: https://textbook-api.onrender.com
API Docs: https://textbook-api.onrender.com/docs

# Frontend
Production Site: https://textbook-frontend.vercel.app

# Admin Dashboards
Neon Database: https://console.neon.tech
Qdrant Cloud: https://cloud.qdrant.io
OpenAI Usage: https://platform.openai.com/usage
Vercel Dashboard: https://vercel.com/dashboard
Render Dashboard: https://dashboard.render.com
```

---

## Next Steps After Deployment

1. **Monitor Usage:**
   - Check OpenAI API costs daily
   - Monitor Qdrant storage limits (1GB free tier)
   - Track database queries (Neon dashboard)

2. **Optimize Performance:**
   - Add Redis caching for frequent queries
   - Implement CDN for static assets
   - Optimize vector search parameters

3. **Gather Feedback:**
   - Add analytics to track user engagement
   - Monitor chatbot question quality
   - Collect user feedback on text selection feature

4. **Scale as Needed:**
   - Upgrade Qdrant cluster if >1GB data
   - Increase Neon compute if >100k queries/month
   - Add load balancer for backend if traffic increases

---

## Support & Resources

- **Documentation:** See `README.md` for development guide
- **API Reference:** `http://localhost:8000/docs` (Swagger UI)
- **Issue Tracker:** GitHub repository issues
- **Architecture:** See `specs/001-docusaurus-textbook/plan.md`

**Happy Deploying! 🚀**
