# Railway Backend-Only Deployment
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Set work directory
WORKDIR /app

# Install minimal system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        postgresql-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY backend/ ./

# Create minimal static frontend
RUN mkdir -p ./static && \
    echo '<!DOCTYPE html><html><head><title>AI Chatbot</title><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>body{font-family:system-ui,sans-serif;margin:0;padding:20px;background:#f5f5f5}h1{color:#333}.container{max-width:800px;margin:0 auto;background:white;padding:30px;border-radius:8px;box-shadow:0 2px 10px rgba(0,0,0,0.1)}.status{color:#10b981;font-weight:bold}.api-link{color:#3b82f6;text-decoration:none}.api-link:hover{text-decoration:underline}</style></head><body><div class="container"><h1>🤖 AI Chatbot Platform</h1><p class="status">✅ Backend API is running successfully!</p><h2>Available Endpoints:</h2><ul><li><a href="/api/v1/health" class="api-link">Health Check</a></li><li><a href="/docs" class="api-link">API Documentation</a></li><li><a href="/api/v1/admin" class="api-link">Admin API</a></li></ul><p><strong>Admin Access:</strong> stefan@axiestudio.se</p><p><em>Frontend will be deployed separately or integrated later.</em></p></div></body></html>' > ./static/index.html

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser /app
USER appuser

# Expose port
EXPOSE $PORT

# Start command
CMD ["python3", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
