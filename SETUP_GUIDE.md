# Complete Setup Guide: Database Migrations & Quiz Generation

## Overview

This guide walks you through setting up the AI-Powered Physical AI & Humanoid Robotics Textbook platform, including:
- Running database migrations to create all necessary tables
- Generating quizzes for all 13 chapters
- Indexing chapters for the RAG chatbot
- Verifying everything works correctly

**Estimated Time:** 20-30 minutes

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start (If You Have Credentials)](#quick-start-if-you-have-credentials)
3. [Detailed Setup Steps](#detailed-setup-steps)
4. [Running Migrations](#running-migrations)
5. [Generating Quizzes](#generating-quizzes)
6. [Indexing Chapters (Optional)](#indexing-chapters-optional)
7. [Verification & Testing](#verification--testing)
8. [Troubleshooting](#troubleshooting)
9. [Cost Estimates](#cost-estimates)

---

## Prerequisites

### What You Need

#### 1. Database (Required)

You need a PostgreSQL database. Two options:

**Option A: Neon Postgres (Recommended - Free Tier)**
- Website: [neon.tech](https://neon.tech)
- Free tier: 3GB storage, 512MB RAM
- Serverless (auto-scales, auto-pauses)
- No credit card required for free tier

**Option B: Local PostgreSQL**
- Install PostgreSQL 14+ locally
- Requires technical setup
- Good for development/testing

#### 2. OpenAI API Key (Required)

- Website: [platform.openai.com](https://platform.openai.com)
- Needed for: Quiz generation, personalization, translation, chatbot
- Cost: ~$0.50 one-time for quiz generation, ~$20-50/month operational
- Requires credit card (even for trial)

#### 3. Qdrant Cloud (Optional - For Chatbot Only)

- Website: [cloud.qdrant.io](https://cloud.qdrant.io)
- Needed for: RAG chatbot with citations
- Free tier: 1GB storage
- Not needed for quiz generation

---

## Quick Start (If You Have Credentials)

If you already have your credentials, follow these steps:

### 1. Update Environment Variables

Edit `backend/.env`:

```bash
# Database - Replace with your actual Neon connection string
DATABASE_URL=postgresql+asyncpg://your_user:your_password@your_host.neon.tech/textbook_db?sslmode=require

# OpenAI - Replace with your actual API key
OPENAI_API_KEY=sk-proj-your_actual_key_here

# Qdrant (optional - for chatbot)
QDRANT_URL=https://your_cluster.cloud.qdrant.io:6333
QDRANT_API_KEY=your_actual_key_here
```

### 2. Run Setup Commands

```bash
cd backend

# Verify prerequisites
python scripts/verify_setup.py

# Run migrations
alembic upgrade head

# Generate quizzes
python scripts/generate_quizzes.py --all

# (Optional) Index chapters for chatbot
python scripts/index_chapters.py --all
```

### 3. Done!

If all commands succeeded, skip to [Verification & Testing](#verification--testing).

---

## Detailed Setup Steps

### Step 1: Get a Database (Neon Postgres)

#### 1.1 Sign Up for Neon

1. Go to [neon.tech](https://neon.tech)
2. Click "Sign Up" (free, no credit card needed)
3. Sign up with GitHub, Google, or email

#### 1.2 Create a Project

1. After login, click "New Project"
2. Enter project name: `robotics-textbook`
3. Select region: Choose closest to you (e.g., `US East (Ohio)`)
4. Click "Create Project"

#### 1.3 Create Database

1. In your new project, you'll see a default database
2. Click "Databases" in left sidebar
3. Click "New Database"
4. Database name: `textbook_db`
5. Click "Create"

#### 1.4 Get Connection String

1. Click "Connection Details" (top right)
2. Select **"Pooled connection"** (important!)
3. Select **"asyncpg"** from driver dropdown
4. Copy the connection string (looks like):
   ```
   postgresql://user:password@ep-cool-morning-12345.us-east-2.aws.neon.tech/textbook_db?sslmode=require
   ```

#### 1.5 Update .env File

Open `backend/.env` and replace the DATABASE_URL:

```bash
# Before (placeholder)
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/textbook_dev

# After (your actual Neon URL - add +asyncpg after postgresql)
DATABASE_URL=postgresql+asyncpg://user:password@ep-cool-morning-12345.us-east-2.aws.neon.tech/textbook_db?sslmode=require
```

**Note:** The connection string from Neon starts with `postgresql://`. You need to change it to `postgresql+asyncpg://` for SQLAlchemy to work.

---

### Step 2: Get OpenAI API Key

#### 2.1 Sign Up for OpenAI

1. Go to [platform.openai.com](https://platform.openai.com)
2. Click "Sign Up" or "Log In"
3. Complete registration (requires phone verification)

#### 2.2 Add Payment Method

1. Go to Settings → Billing
2. Click "Add payment method"
3. Enter credit card details
4. Set usage limit (recommended: $50/month to start)

#### 2.3 Create API Key

1. Click your profile (top right) → "API Keys"
2. Click "+ Create new secret key"
3. Name it: `robotics-textbook`
4. Click "Create secret key"
5. **IMPORTANT:** Copy the key immediately (starts with `sk-proj-` or `sk-`)
6. You won't be able to see it again!

#### 2.4 Update .env File

Open `backend/.env` and replace the OPENAI_API_KEY:

```bash
# Before (placeholder)
OPENAI_API_KEY=sk-placeholder

# After (your actual key)
OPENAI_API_KEY=sk-proj-ABC123XYZ789yourActualKeyHere
```

---

### Step 3: Get Qdrant Cloud Account (Optional)

**Skip this step if you only want quizzes and not the chatbot.**

#### 3.1 Sign Up for Qdrant Cloud

1. Go to [cloud.qdrant.io](https://cloud.qdrant.io)
2. Click "Sign Up" (free tier available)
3. Sign up with GitHub or email

#### 3.2 Create a Cluster

1. After login, click "Create Cluster"
2. Cluster name: `textbook-vectors`
3. Select free tier (1GB)
4. Select region: Choose closest to you
5. Click "Create"
6. Wait 1-2 minutes for cluster to provision

#### 3.3 Get Credentials

1. Click on your cluster name
2. Copy the **Cluster URL** (looks like):
   ```
   https://abc123xyz.us-east-1-0.aws.cloud.qdrant.io:6333
   ```
3. Click "API Keys" tab
4. Click "Create API Key"
5. Copy the API key

#### 3.4 Update .env File

Open `backend/.env` and replace Qdrant settings:

```bash
# Before (placeholder)
QDRANT_URL=https://placeholder.qdrant.io
QDRANT_API_KEY=placeholder

# After (your actual credentials)
QDRANT_URL=https://abc123xyz.us-east-1-0.aws.cloud.qdrant.io:6333
QDRANT_API_KEY=your_actual_qdrant_api_key_here
```

---

### Step 4: Install Dependencies

Make sure you have Python dependencies installed:

```bash
cd backend

# Create virtual environment (if not already done)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Expected output:**
```
Successfully installed alembic-1.x.x sqlalchemy-2.x.x fastapi-0.x.x ...
```

---

## Running Migrations

Now that everything is configured, let's create the database tables.

### Verify Setup First

Before running migrations, verify your configuration:

```bash
cd backend
python scripts/verify_setup.py
```

**Expected output:**
```
=== Setup Verification ===

✓ .env file: OK
✓ Chapter files: OK (Found 13 chapters)
✓ Database connection: OK
✓ OpenAI API key: OK
✓ Qdrant connection: OK (or note about it being optional)

=== Summary ===

✓ All required prerequisites met!

You can now run:
  alembic upgrade head  (run migrations)
  python scripts/generate_quizzes.py --all  (generate quizzes)
```

If you see errors, see [Troubleshooting](#troubleshooting) section.

### Run Migrations

```bash
cd backend
alembic upgrade head
```

**Expected output:**
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 001, Initial schema
INFO  [alembic.runtime.migration] Running upgrade 001 -> 002, Add translations and quiz system tables
```

**What this does:**
- Creates `users`, `user_profiles`, `user_progress` tables (from migration 001)
- Creates `chat_conversations`, `chat_messages` tables (from migration 001)
- Creates `translations` table (from migration 002)
- Creates `quizzes`, `quiz_questions`, `quiz_attempts`, `quiz_responses` tables (from migration 002)

### Verify Tables Were Created

You can verify in Neon dashboard:

1. Go to [neon.tech](https://neon.tech)
2. Open your project
3. Click "SQL Editor" in left sidebar
4. Run this query:
   ```sql
   SELECT table_name
   FROM information_schema.tables
   WHERE table_schema = 'public'
   ORDER BY table_name;
   ```

**Expected result:** List of 10+ tables including:
- bookmarks
- chat_conversations
- chat_messages
- quiz_attempts
- quiz_questions
- quiz_responses
- quizzes
- translations
- user_profiles
- user_progress
- users

---

## Generating Quizzes

Now let's generate quizzes for all 13 chapters using GPT-4.

### Generate All Quizzes

```bash
cd backend
python scripts/generate_quizzes.py --all
```

**Expected output:**
```
=== Generating Quizzes for All Chapters ===

Found 13 chapters

Generating quiz for: chapter-01-physical-ai-intro.md
  Generating questions...
  Generated 8 questions
  ✓ Saved quiz with 8 questions

Generating quiz for: chapter-02-ros2-fundamentals.md
  Generating questions...
  Generated 8 questions
  ✓ Saved quiz with 8 questions

Generating quiz for: chapter-03-ros2-topics.md
  Generating questions...
  Generated 8 questions
  ✓ Saved quiz with 8 questions

... [continues for all 13 chapters] ...

Generating quiz for: chapter-13-capstone-project.md
  Generating questions...
  Generated 8 questions
  ✓ Saved quiz with 8 questions


=== Summary ===
Successfully generated: 13/13 quizzes
```

**Time:** 2-3 minutes (depends on OpenAI API response time)

**Cost:** ~$0.50 total (one-time)

### What Gets Created

For each chapter, the script:
1. Reads chapter content and learning objectives
2. Calls GPT-4 to generate 8 questions
3. Saves to database with:
   - Multiple choice questions (60%)
   - True/false questions (20%)
   - Code completion questions (20%)
   - Mix of beginner/intermediate/advanced difficulty
   - Detailed explanations for each answer

### Verify Quizzes Were Created

Check quiz count in database:

```bash
cd backend
python -c "
import asyncio
from src.db.connection import get_async_session
from src.models.quiz import Quiz
from sqlalchemy import select, func

async def count():
    async for db in get_async_session():
        result = await db.execute(select(func.count(Quiz.id)))
        print(f'Total quizzes: {result.scalar()}')
        break

asyncio.run(count())
"
```

**Expected output:**
```
Total quizzes: 13
```

Or check in Neon SQL Editor:
```sql
SELECT chapter_id, title,
       (SELECT COUNT(*) FROM quiz_questions WHERE quiz_id = quizzes.id) as question_count
FROM quizzes
ORDER BY chapter_id;
```

**Expected:** 13 rows, each with 8 questions

---

## Indexing Chapters (Optional)

**Skip this section if you don't need the RAG chatbot feature.**

If you have Qdrant configured and want the chatbot to work:

```bash
cd backend
python scripts/index_chapters.py --all
```

**Expected output:**
```
=== Indexing All Chapters ===

Found 13 chapters to index

✓ Qdrant collection ready

Indexing: chapter-01-physical-ai-intro.md
  Created 12 chunks
  Generating embeddings...
  Generated 12 embeddings
  Uploading to Qdrant...
  ✓ Indexed 12 chunks for Introduction to Physical AI

... [continues for all chapters] ...

=== Summary ===
Total chapters: 13
Total chunks: 156
Average chunks per chapter: 12.0
```

**Time:** 5-10 minutes

**Cost:** ~$0.20 (one-time for embeddings)

---

## Verification & Testing

After completing setup, test that everything works:

### Test 1: Database Connection

```bash
cd backend
python -c "
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def test():
    url = os.getenv('DATABASE_URL').replace('postgresql+asyncpg://', 'postgresql://')
    url = url.replace('?sslmode=require', '?ssl=require')
    conn = await asyncpg.connect(url)
    version = await conn.fetchval('SELECT version()')
    print('✓ Database connected:', version[:50])
    await conn.close()

asyncio.run(test())
"
```

**Expected:** `✓ Database connected: PostgreSQL 15.x on x86_64...`

### Test 2: OpenAI API

```bash
cd backend
python -c "
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model='gpt-4-turbo')
print('✓ OpenAI API key valid')
"
```

**Expected:** `✓ OpenAI API key valid`

### Test 3: Quiz Data

```bash
cd backend
python -c "
import asyncio
from src.db.connection import get_async_session
from src.models.quiz import Quiz, QuizQuestion
from sqlalchemy import select, func

async def check():
    async for db in get_async_session():
        # Count quizzes
        quiz_count = await db.execute(select(func.count(Quiz.id)))
        print(f'✓ Quizzes created: {quiz_count.scalar()}')

        # Count questions
        q_count = await db.execute(select(func.count(QuizQuestion.id)))
        print(f'✓ Questions created: {q_count.scalar()}')

        # Sample quiz
        result = await db.execute(select(Quiz).limit(1))
        quiz = result.scalar_one_or_none()
        if quiz:
            print(f'✓ Sample quiz: {quiz.title} ({quiz.chapter_id})')
        break

asyncio.run(check())
"
```

**Expected output:**
```
✓ Quizzes created: 13
✓ Questions created: 104
✓ Sample quiz: Introduction to Physical AI Quiz (chapter-01-physical-ai-intro)
```

### Test 4: Start Backend Server

```bash
cd backend
uvicorn src.main:app --reload
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
Starting up AI Textbook API...
INFO:     Application startup complete.
```

Open browser to `http://localhost:8000/docs` - you should see the API documentation.

**Press CTRL+C to stop the server.**

---

## Troubleshooting

### Error: "ConnectionRefusedError" when running migrations

**Symptoms:**
```
ConnectionRefusedError: The remote computer refused the network connection
```

**Cause:** Database URL is incorrect or database isn't reachable.

**Solutions:**

1. **Check DATABASE_URL format:**
   - Must start with `postgresql+asyncpg://` (not just `postgresql://`)
   - For Neon, must end with `?sslmode=require`
   - Example:
     ```
     postgresql+asyncpg://user:pass@host.neon.tech/db?sslmode=require
     ```

2. **Test connection manually:**
   ```bash
   python -c "
   import asyncpg
   import asyncio
   # Replace with your URL (remove +asyncpg, change sslmode to ssl)
   asyncio.run(asyncpg.connect('postgresql://user:pass@host/db?ssl=require'))
   print('Connected!')
   "
   ```

3. **For Neon users:**
   - Make sure your Neon project isn't paused (it auto-pauses after inactivity)
   - Go to Neon dashboard and click on your project to wake it up
   - Wait 30 seconds and try again

4. **Check firewall:**
   - Make sure port 5432 (PostgreSQL) isn't blocked
   - Try from a different network if possible

---

### Error: "AuthenticationError" when generating quizzes

**Symptoms:**
```
openai.AuthenticationError: Incorrect API key provided
```

**Cause:** OpenAI API key is invalid or not set.

**Solutions:**

1. **Verify key in .env:**
   ```bash
   cat backend/.env | grep OPENAI_API_KEY
   ```
   - Should show: `OPENAI_API_KEY=sk-proj-...`
   - Must NOT be `sk-placeholder`

2. **Check key is valid:**
   - Go to [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
   - Verify your key is listed and active
   - If not, create a new one

3. **Check billing:**
   - Go to [platform.openai.com/settings/organization/billing](https://platform.openai.com/settings/organization/billing)
   - Verify payment method is added
   - Check you have available credits or usage limits

4. **Environment variable not loaded:**
   ```bash
   # Make sure you're in backend directory
   cd backend

   # Try loading .env explicitly
   python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('OPENAI_API_KEY'))"
   ```

---

### Error: "No chapters found" when generating quizzes

**Symptoms:**
```
No chapter files found!
```

**Cause:** Script can't find chapter markdown files.

**Solutions:**

1. **Verify directory structure:**
   ```bash
   ls ../frontend/docs/module-*/chapter-*.md
   ```
   - Should list 13 chapter files
   - If no files found, check you're in `backend` directory

2. **Specify docs directory explicitly:**
   ```bash
   python scripts/generate_quizzes.py --docs-dir ../frontend/docs --all
   ```

3. **Check file permissions:**
   ```bash
   # On Mac/Linux:
   chmod -R 755 ../frontend/docs
   ```

---

### Error: "Failed to generate questions" for a chapter

**Symptoms:**
```
Generating quiz for: chapter-03-ros2-topics.md
  ⚠ Skipping: No learning objectives defined
```

**Cause:** Chapter frontmatter missing `learning_objectives` field.

**Solution:**

1. **Open the chapter file:**
   ```bash
   nano ../frontend/docs/module-01/chapter-03-ros2-topics.md
   ```

2. **Check frontmatter has learning_objectives:**
   ```yaml
   ---
   id: chapter-03-ros2-topics
   title: ROS 2 Topics
   module: 1
   week: 2
   learning_objectives:
     - Understand publish-subscribe pattern
     - Create publishers and subscribers
     - Use ROS 2 command-line tools
   estimated_time_minutes: 60
   ---
   ```

3. **If missing, add learning objectives** (3-5 bullet points)

4. **Re-run quiz generation for that chapter:**
   ```bash
   python scripts/generate_quizzes.py --chapter chapter-03-ros2-topics
   ```

---

### Error: "Table already exists" when running migrations

**Symptoms:**
```
sqlalchemy.exc.ProgrammingError: (asyncpg.exceptions.DuplicateTableError) relation "quizzes" already exists
```

**Cause:** Migrations were already run, or tables exist from previous attempts.

**Solutions:**

1. **Check current migration version:**
   ```bash
   alembic current
   ```
   - If it shows `002 (head)`, migrations are already done
   - You can skip to quiz generation

2. **If stuck at wrong version:**
   ```bash
   # Downgrade to base
   alembic downgrade base

   # Re-run all migrations
   alembic upgrade head
   ```

3. **Nuclear option (start fresh):**
   ```sql
   -- In Neon SQL Editor, run:
   DROP SCHEMA public CASCADE;
   CREATE SCHEMA public;
   ```
   Then run migrations again.

---

### Quiz generation is very slow (>5 minutes)

**Cause:** OpenAI API rate limits or high load.

**Solutions:**

1. **Check your OpenAI tier:**
   - Free tier: 3 requests/minute (very slow for 13 chapters)
   - Tier 1: 500 requests/minute (much faster)
   - Upgrade if needed: [platform.openai.com/settings/organization/billing](https://platform.openai.com/settings/organization/billing)

2. **Generate quizzes one at a time:**
   ```bash
   python scripts/generate_quizzes.py --chapter chapter-01-physical-ai-intro
   python scripts/generate_quizzes.py --chapter chapter-02-ros2-fundamentals
   # ... etc
   ```

3. **Wait and retry:**
   - Rate limits reset every minute
   - Script will eventually complete

---

## Cost Estimates

### One-Time Setup Costs

| Item | Cost | Frequency |
|------|------|-----------|
| Quiz generation (13 chapters) | $0.40-0.60 | Once |
| Chapter indexing (156 chunks) | $0.15-0.25 | Once |
| **Total Setup** | **~$0.75** | **Once** |

### Monthly Operational Costs (100 users)

| Service | Cost | Notes |
|---------|------|-------|
| Neon Postgres | Free | Up to 3GB storage (plenty for MVP) |
| Qdrant Cloud | Free | Up to 1GB vectors (covers 13 chapters) |
| OpenAI API | $20-50 | Depends on usage (chatbot, personalization, translation) |
| **Total Monthly** | **$20-50** | **Scales with usage** |

### Cost Optimization Tips

1. **Translation caching:** Urdu translations are cached - each translation only costs once
2. **Quiz caching:** Quizzes generated once, served infinite times
3. **User limits:** Set usage limits per user (e.g., 10 chatbot messages/day)
4. **OpenAI budget:** Set monthly budget in OpenAI dashboard to prevent surprises

---

## Next Steps After Setup

Once setup is complete:

### 1. Start Backend Server

```bash
cd backend
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Access at: `http://localhost:8000`
API docs: `http://localhost:8000/docs`

### 2. Start Frontend

```bash
cd frontend
npm install  # First time only
npm start
```

Access at: `http://localhost:3000`

### 3. Test All Features

- ✅ Sign up for an account
- ✅ Read a chapter
- ✅ Ask chatbot a question
- ✅ Select text, get AI explanation
- ✅ Click "Personalize for Me"
- ✅ Switch to Urdu language
- ✅ Take a quiz, see results

### 4. Deploy to Production

See `DEPLOYMENT.md` for:
- Vercel frontend deployment
- Render/Railway backend deployment
- Environment variable configuration
- Production checklist

---

## Summary

**What you accomplished:**

✅ Set up PostgreSQL database (Neon)
✅ Configured OpenAI API
✅ Configured Qdrant (optional)
✅ Ran database migrations (10+ tables created)
✅ Generated 13 quizzes (104 total questions)
✅ Indexed chapters for chatbot (optional)
✅ Verified all features work

**Your platform now has:**

- 🎓 13 comprehensive textbook chapters
- 💬 RAG-powered chatbot with citations
- ✨ Text selection AI for instant explanations
- 🔐 User authentication and progress tracking
- 🎯 Personalized content based on skill level
- 🌍 Urdu translation with RTL support
- 📝 Auto-generated quizzes with immediate feedback

**Ready for deployment!** 🚀

Need help? Check:
- `DEPLOYMENT.md` - Production deployment guide
- `IMPLEMENTATION_SUMMARY.md` - What was built
- `EXAMPLE_QUIZ_OUTPUT.md` - Sample quiz format
- GitHub issues - Report problems
