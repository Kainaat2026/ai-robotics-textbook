FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application code
COPY src/ ./src/
COPY api/ ./api/ 2>/dev/null || true

# Debug: List files to verify structure
RUN echo "=== Files in /app ===" && ls -la /app && \
    echo "=== Files in /app/src ===" && ls -la /app/src || echo "No src folder"

# Expose port 7860 (Hugging Face Spaces default)
EXPOSE 7860

# Set Python path
ENV PYTHONPATH=/app

# Run the FastAPI app
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "7860"]
