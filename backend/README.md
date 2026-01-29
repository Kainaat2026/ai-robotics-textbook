---
title: AI Robotics Textbook API
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
---

# AI-Powered Physical AI & Robotics Textbook API

Backend API for the AI-enhanced interactive textbook with:
- Translation to Urdu using Google Gemini
- RAG-powered chatbot
- Quiz generation
- Progress tracking
- User authentication

## Endpoints

- `GET /` - Health check
- `GET /health` - Detailed health status
- `GET /docs` - Swagger API documentation
- `POST /api/translate` - Translate content to Urdu
- `POST /api/chat` - Chat with AI assistant
- `GET /api/quiz/{chapter_id}` - Get chapter quiz

## Environment Variables

Required secrets (set in HF Space settings):
- `GOOGLE_API_KEY` - Google Gemini API key
- `DATABASE_URL` - PostgreSQL connection string
- `JWT_SECRET_KEY` - Secret for JWT tokens
