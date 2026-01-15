# Deployment Guide - AI-Powered Textbook

## Pre-Deployment Checklist

### 1. Environment Setup
- [ ] Python 3.14+ installed
- [ ] Node.js 20+ installed
- [ ] PostgreSQL database (Neon or local)
- [ ] Qdrant vector store account
- [ ] Google Gemini API key

### 2. Configuration Files
- [ ] Backend `.env` file configured
- [ ] Frontend environment variables set
- [ ] CORS origins updated for production
- [ ] Database migrations applied

---

## Local Development Deployment

### Backend Setup

```bash
# Navigate to backend
cd backend

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your credentials

# Index chapters (first time only)
python scripts/index_chapters.py --all

# Start development server
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

**Verify Backend**:
```bash
curl http://localhost:8000/health
```

### Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run start
```

**Access**: http://localhost:3000

---

## Production Deployment

### Option 1: Docker Deployment (Recommended)

#### Backend Dockerfile

```dockerfile
FROM python:3.14-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY src/ ./src/
COPY scripts/ ./scripts/

# Expose port
EXPOSE 8000

# Start server
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Frontend Dockerfile

```dockerfile
FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json ./
RUN npm ci

# Copy source
COPY . .

# Build static site
RUN npm run build

# Production image
FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

#### Docker Compose

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - QDRANT_URL=${QDRANT_URL}
      - QDRANT_API_KEY=${QDRANT_API_KEY}
    volumes:
      - ./backend:/app
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
    restart: unless-stopped
```

**Deploy**:
```bash
docker-compose up -d
```

---

### Option 2: Cloud Platform Deployment

#### Backend: Railway / Render / Fly.io

**Railway Deployment**:
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
cd backend
railway init

# Add environment variables via Railway dashboard
# Deploy
railway up
```

**Environment Variables to Set**:
- `DATABASE_URL`
- `GEMINI_API_KEY`
- `GEMINI_MODEL`
- `QDRANT_URL`
- `QDRANT_API_KEY`
- `CORS_ORIGINS` (update to frontend URL)
- `ENVIRONMENT=production`

#### Frontend: Vercel / Netlify

**Vercel Deployment**:
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
cd frontend
vercel

# Set environment variable
vercel env add REACT_APP_API_URL
# Enter your backend URL: https://your-backend.railway.app/api
```

**Netlify Deployment**:
```bash
# Install Netlify CLI
npm install -g netlify-cli

# Build and deploy
cd frontend
npm run build
netlify deploy --prod --dir=build
```

---

## Database Setup

### Neon PostgreSQL (Serverless)

1. Create account at https://neon.tech
2. Create new project
3. Copy connection string
4. Update `.env`:
   ```
   DATABASE_URL=postgresql+asyncpg://user:pass@host/db
   ```

### Run Migrations

```bash
cd backend
alembic upgrade head
```

---

## Vector Store Setup

### Qdrant Cloud

1. Create account at https://qdrant.tech
2. Create new cluster
3. Get API key and URL
4. Update `.env`:
   ```
   QDRANT_URL=https://your-cluster.qdrant.io:6333
   QDRANT_API_KEY=your-api-key
   QDRANT_COLLECTION_NAME=textbook_embeddings
   ```

### Index Chapters

```bash
cd backend
python scripts/index_chapters.py --all
```

**Expected Output**:
```
=== Indexing All Chapters ===
Found 13 chapters to index
OK Indexed 337 chunks for 13 chapters
```

---

## Security Checklist

### Before Production:

- [ ] **API Keys**: Never commit `.env` files
- [ ] **CORS**: Restrict to your domain only
- [ ] **Rate Limiting**: Enable and configure appropriately
- [ ] **HTTPS**: Use SSL certificates (Let's Encrypt)
- [ ] **Authentication**: Implement user auth if needed
- [ ] **Database**: Use strong passwords
- [ ] **Secrets**: Use environment variables or secret managers

### Update Production CORS

```env
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

---

## Performance Optimization

### Backend

1. **Enable Caching**:
   - Add Redis for translation caching
   - Cache vector search results

2. **Database Optimization**:
   - Add indexes on frequently queried fields
   - Use connection pooling

3. **Rate Limiting**:
   ```env
   RATE_LIMIT_CHAT=100
   RATE_LIMIT_QUIZ=50
   RATE_LIMIT_WINDOW_MINUTES=60
   ```

### Frontend

1. **Build Optimization**:
   ```bash
   npm run build
   ```

2. **CDN**: Deploy to Vercel/Netlify for automatic CDN

3. **Code Splitting**: Already handled by Docusaurus

---

## Monitoring & Logging

### Backend Logging

**Configure Log Level**:
```env
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
LOG_FORMAT=json
```

### Health Checks

**Set up monitoring** for:
- `GET /health` - API health
- Database connection
- Qdrant connection
- Response times

**Recommended Tools**:
- UptimeRobot (free)
- BetterUptime
- Pingdom

---

## Backup Strategy

### Database Backups

**Neon Auto-Backups**: Enabled by default (7 days retention)

**Manual Backup**:
```bash
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql
```

### Vector Store Backups

**Qdrant Snapshots**:
```python
# scripts/backup_qdrant.py
from src.utils.vector_store import vector_store

snapshot = vector_store.client.create_snapshot(
    collection_name="textbook_embeddings"
)
```

---

## Scaling Considerations

### Horizontal Scaling

**Backend**:
- Run multiple FastAPI instances behind load balancer
- Use gunicorn with uvicorn workers:
  ```bash
  gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker
  ```

**Database**:
- Neon auto-scales
- Consider read replicas for heavy read workloads

**Vector Store**:
- Qdrant Cloud scales automatically
- Consider dedicated cluster for production

---

## Cost Estimation

### Free Tier Components

- **Google Gemini API**: Free tier (15 requests/minute)
- **Neon PostgreSQL**: Free tier (0.5 GB storage)
- **Qdrant Cloud**: Free tier (1 GB)
- **Vercel/Netlify**: Free tier for frontend hosting

### Production Costs (Estimated Monthly)

- **Backend Hosting**: $5-20 (Railway/Render)
- **Frontend Hosting**: $0-5 (Vercel/Netlify)
- **Database**: $0-10 (Neon)
- **Vector Store**: $0-25 (Qdrant)
- **Gemini API**: $0 (within free tier limits)

**Total**: $5-60/month depending on usage

---

## Troubleshooting

### Common Issues

**Issue**: Chatbot timeout
- **Solution**: Increase timeout in frontend ChatbotService:
  ```typescript
  timeout: 60000  // 60 seconds
  ```

**Issue**: Database connection fails
- **Solution**: Check DATABASE_URL format:
  ```
  postgresql+asyncpg://user:pass@host:5432/db
  ```

**Issue**: Qdrant 404 errors
- **Solution**: Verify collection exists:
  ```bash
  python scripts/index_chapters.py --all
  ```

**Issue**: CORS errors
- **Solution**: Update backend CORS_ORIGINS to include frontend URL

---

## CI/CD Pipeline

### GitHub Actions Example

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.14'
      - name: Deploy to Railway
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
        run: |
          npm install -g @railway/cli
          railway up

  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '20'
      - name: Deploy to Vercel
        env:
          VERCEL_TOKEN: ${{ secrets.VERCEL_TOKEN }}
        run: |
          npm install -g vercel
          cd frontend
          vercel --prod --token=$VERCEL_TOKEN
```

---

## Post-Deployment Verification

### Checklist

1. **Health Check**:
   ```bash
   curl https://your-api.com/health
   ```

2. **Test Chatbot**:
   ```bash
   curl -X POST https://your-api.com/api/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "What is ROS 2?", "language": "en"}'
   ```

3. **Test Frontend**:
   - Visit https://your-frontend.com
   - Open chatbot widget
   - Send test message
   - Verify response and citations

4. **Monitor Logs**:
   - Check backend logs for errors
   - Monitor response times
   - Verify database connections

---

## Rollback Procedure

### Quick Rollback

**Railway**:
```bash
railway rollback
```

**Vercel**:
```bash
vercel rollback
```

**Docker**:
```bash
docker-compose down
git checkout previous-commit
docker-compose up -d
```

---

## Maintenance

### Regular Tasks

**Weekly**:
- Review error logs
- Check API usage and quotas
- Monitor response times

**Monthly**:
- Database backups verification
- Security updates
- Dependency updates

**Quarterly**:
- Review and optimize costs
- Update documentation
- Performance testing

---

## Support Resources

- **API Documentation**: `/API_DOCUMENTATION.md`
- **Setup Guide**: `/SETUP_GUIDE.md`
- **Backend Docs**: http://localhost:8000/docs (when running)
- **Docusaurus Docs**: https://docusaurus.io
- **FastAPI Docs**: https://fastapi.tiangolo.com

---

**Version**: 1.0.0
**Last Updated**: January 14, 2026
