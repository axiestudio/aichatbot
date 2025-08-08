# Railway Optimized - Frontend build stage
FROM node:18-alpine AS frontend-build

WORKDIR /app

# Copy package files
COPY frontend/package*.json ./

# Install dependencies with memory optimization
RUN npm install --silent

# Copy frontend source
COPY frontend/ ./

# Build with memory constraints for Railway
RUN NODE_OPTIONS="--max-old-space-size=512" npm run build

# Backend stage
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

# Copy built frontend from build stage
COPY --from=frontend-build /app/dist ./static

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser /app
USER appuser

# Expose port
EXPOSE $PORT

# Start command
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
