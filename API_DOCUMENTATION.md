# AI-Powered Textbook API Documentation

## System Overview

This is an AI-powered interactive textbook platform for Physical AI and Humanoid Robotics with the following features:

- **RAG Chatbot**: Semantic search and question answering powered by Google Gemini 2.5 Flash
- **Translation**: English to Urdu translation with technical term preservation
- **Text-to-Speech**: Audio narration for accessibility
- **Text Selection AI**: Contextual explanations for selected text
- **Progress Tracking**: User progress, quizzes, and bookmarks
- **Personalization**: Adaptive content based on user skill level

## Architecture

### Backend Stack
- **Framework**: FastAPI (Python 3.14)
- **LLM**: Google Gemini 2.5 Flash (Free Tier)
- **Embeddings**: Google text-embedding-004 (768 dimensions)
- **Vector Store**: Qdrant Cloud
- **Database**: PostgreSQL (Neon Serverless)
- **Port**: 8000

### Frontend Stack
- **Framework**: Docusaurus (React)
- **HTTP Client**: Axios
- **Port**: 3000 (default) or 3001

### Content Indexed
- **Total Chapters**: 13/13 (100% coverage)
- **Total Chunks**: 337 searchable segments
- **Topics**: ROS 2, Gazebo, Unity, Isaac SDK, Sim-to-Real, Humanoid Development, VLA Models, Conversational Robotics

---

## API Endpoints

### Base URL
```
http://localhost:8000/api
```

### Health & Status

#### `GET /`
**Description**: Root health check

**Response**:
```json
{
  "status": "healthy",
  "service": "AI Textbook API",
  "version": "1.0.0",
  "environment": "development"
}
```

#### `GET /health`
**Description**: Detailed health status

**Response**:
```json
{
  "status": "healthy",
  "checks": {
    "api": "ok"
  }
}
```

---

### Chatbot Endpoints

#### `POST /api/chat`
**Description**: Send a message to the RAG chatbot

**Request**:
```json
{
  "conversation_id": "uuid-or-null",
  "message": "What are ROS 2 topics?",
  "language": "en"
}
```

**Response**:
```json
{
  "conversation_id": "706633e1-344b-4252-8ac1-c8af228700d0",
  "message": "ROS 2 Topics enable asynchronous communication...",
  "citations": [
    {
      "chapter_id": "chapter-03-ros2-topics",
      "section": "Introduction",
      "title": "ROS 2 Topics and Message Types"
    }
  ],
  "tokens_used": 0,
  "response_time_ms": 3505
}
```

**Features**:
- Retrieval-Augmented Generation (RAG) with Qdrant vector search
- Source citations from indexed chapters
- Conversation persistence in PostgreSQL
- Language support: English (`en`), Urdu (`ur`)

---

#### `GET /api/chat/conversation/{conversation_id}`
**Description**: Retrieve full conversation history

**Response**:
```json
{
  "conversation_id": "uuid",
  "language": "en",
  "messages": [
    {
      "id": "uuid",
      "role": "user",
      "message": "What are ROS 2 topics?",
      "created_at": "2026-01-14T16:40:00Z"
    },
    {
      "id": "uuid",
      "role": "assistant",
      "message": "ROS 2 Topics enable...",
      "citations": [...],
      "created_at": "2026-01-14T16:40:05Z"
    }
  ],
  "created_at": "2026-01-14T16:40:00Z",
  "updated_at": "2026-01-14T16:40:05Z"
}
```

---

#### `POST /api/chat/text-selection`
**Description**: Get AI explanation for selected text

**Request**:
```json
{
  "selected_text": "publish-subscribe pattern",
  "chapter_id": "chapter-03-ros2-topics",
  "surrounding_context": "ROS 2 uses the publish-subscribe pattern for communication.",
  "language": "en"
}
```

**Response**:
```json
{
  "explanation": "The publish-subscribe pattern is an asynchronous messaging pattern...",
  "citations": [
    {
      "chapter_id": "chapter-03-ros2-topics",
      "section": "Patterns",
      "title": "ROS 2 Topics and Message Types"
    }
  ],
  "response_time_ms": 2500
}
```

---

### Translation Endpoint

#### `POST /api/translate`
**Description**: Translate content from English to Urdu

**Request**:
```json
{
  "content": "ROS 2 Topics enable asynchronous communication between nodes.",
  "target_language": "ur",
  "content_type": "chapter"
}
```

**Response**:
```json
{
  "translated_content": "ROS 2 ٹاپکس نوڈز کے درمیان...",
  "source_language": "en",
  "target_language": "ur",
  "cached": false,
  "response_time_ms": 3264
}
```

**Features**:
- Preserves markdown structure and code blocks
- Technical term transliteration (Robot → روبوٹ)
- Keeps acronyms in English (ROS 2, AI, GPU)
- RTL (Right-to-Left) text direction support

---

## Frontend Integration

### Chatbot Service

**File**: `frontend/src/components/Chatbot/ChatbotService.ts`

**Usage**:
```typescript
import { chatbotService, Language } from '@/components/Chatbot/ChatbotService';

// Send a message
const response = await chatbotService.sendMessage(
  "What is Gazebo simulation?",
  null, // conversation_id (null for new conversation)
  Language.ENGLISH
);

console.log(response.message);
console.log(response.citations);

// Get conversation history
const history = await chatbotService.getConversationHistory(
  response.conversation_id
);

// Explain selected text
const explanation = await chatbotService.explainTextSelection(
  "domain randomization",
  "chapter-10-sim-to-real",
  "Context around the selected text..."
);
```

---

## Environment Variables

### Backend `.env`

```env
# Database (Neon Postgres)
DATABASE_URL=postgresql+asyncpg://user:pass@host/db

# Google Gemini API (FREE)
GEMINI_API_KEY=your-api-key
GEMINI_MODEL=models/gemini-2.5-flash
GEMINI_EMBEDDING_MODEL=models/text-embedding-004

# Qdrant Vector Store
QDRANT_URL=https://your-cluster.qdrant.io:6333
QDRANT_API_KEY=your-qdrant-api-key
QDRANT_COLLECTION_NAME=textbook_embeddings

# Application Settings
ENVIRONMENT=development
DEBUG=true
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
API_PORT=8000
API_HOST=0.0.0.0

# Rate Limiting
RATE_LIMIT_CHAT=20
RATE_LIMIT_QUIZ=10
RATE_LIMIT_WINDOW_MINUTES=60

# Feature Flags
ENABLE_URDU_TRANSLATION=true
ENABLE_QUIZ_GENERATION=true
ENABLE_TEXT_SELECTION_AI=true
ENABLE_PERSONALIZATION=true

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

---

## Running the System

### Backend

```bash
cd backend
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

Access API docs: http://localhost:8000/docs

### Frontend

```bash
cd frontend
npm run start
```

Access UI: http://localhost:3000

---

## Testing

### Test Chatbot

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are ROS 2 topics?",
    "language": "en"
  }'
```

### Test Translation

```bash
curl -X POST http://localhost:8000/api/translate \
  -H "Content-Type: application/json" \
  -d '{
    "content": "ROS 2 is a robotics framework.",
    "target_language": "ur",
    "content_type": "chapter"
  }'
```

---

## Performance Metrics

### Chatbot Performance
- **Average Response Time**: 3-5 seconds
- **Vector Search**: ~500ms (Qdrant Cloud)
- **LLM Generation**: 2-4 seconds (Gemini 2.5 Flash)
- **Chunks Retrieved**: 5 most relevant per query

### Translation Performance
- **Average Response Time**: 3-4 seconds
- **Model**: Gemini 2.5 Flash with low temperature (0.2) for consistency

### Indexing Stats
- **Total Chapters**: 13
- **Total Chunks**: 337
- **Average Chunks/Chapter**: 25.9
- **Embedding Dimensions**: 768
- **Chunk Size**: ~1000 characters with 200-character overlap

---

## Troubleshooting

### Backend Won't Start
1. Check if port 8000 is in use: `netstat -ano | findstr :8000`
2. Verify environment variables in `.env`
3. Check database connection (DATABASE_URL)
4. Verify Qdrant API key and URL

### Frontend Can't Connect to Backend
1. Verify backend is running: `curl http://localhost:8000/health`
2. Check CORS settings in backend `.env`
3. Verify API_BASE_URL in `ChatbotService.ts`

### Chatbot Returns "Couldn't find information"
1. Verify chapters are indexed: Check Qdrant collection
2. Re-index chapters: `python scripts/index_chapters.py --all`
3. Check vector store connection

### Translation Fails
1. Verify GEMINI_API_KEY is valid
2. Check GEMINI_MODEL is set to `models/gemini-2.5-flash`
3. Ensure sufficient API quota

---

## API Rate Limits

**Default Limits**:
- Chat: 20 requests per 60 minutes
- Quiz: 10 requests per 60 minutes

**Configurable via**:
- `RATE_LIMIT_CHAT`
- `RATE_LIMIT_QUIZ`
- `RATE_LIMIT_WINDOW_MINUTES`

---

## Database Schema

### `chat_conversations`
- `id` (UUID, PK)
- `user_id` (UUID, FK to users, nullable for demo)
- `language` (ENUM: en, ur)
- `created_at`, `updated_at`

### `chat_messages`
- `id` (UUID, PK)
- `conversation_id` (UUID, FK)
- `role` (ENUM: user, assistant)
- `message` (VARCHAR)
- `citations` (JSONB)
- `tokens_used` (INTEGER)
- `created_at`

---

## Next Steps

### Recommended Enhancements
1. **Quiz Generation Endpoint**: Expose quiz service via API
2. **User Authentication**: Implement user accounts and progress tracking
3. **Analytics Dashboard**: Track usage metrics and popular topics
4. **Caching Layer**: Redis for translation caching
5. **Advanced Search**: Filters by chapter, module, difficulty

### Deployment Considerations
1. **Environment**: Production environment variables
2. **Secrets Management**: Use secret manager for API keys
3. **Scaling**: Consider load balancer for multiple backend instances
4. **Monitoring**: Set up health checks and alerting
5. **CI/CD**: Automated testing and deployment pipeline

---

## Support & Contact

For issues or questions:
- GitHub Issues: [Repository URL]
- Documentation: This file
- API Reference: http://localhost:8000/docs (when running)

---

**Last Updated**: January 14, 2026
**Version**: 1.0.0
