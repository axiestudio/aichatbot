# 🚀 AI CHATBOT PLATFORM - DOCKER HUB IMAGE
# Production-ready Docker image for axiestudio/aichatbot
# Optimized multi-stage build for minimal size and maximum security

# ============================================================================
# STAGE 1: BUILD STAGE
# ============================================================================
FROM python:3.11-slim as builder

# Build environment
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Install build dependencies (minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* \
    && rm -rf /var/tmp/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy backend requirements and install
COPY backend/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /tmp/requirements.txt && \
    rm -rf /tmp/* && \
    rm -rf /root/.cache

# ============================================================================
# STAGE 2: PRODUCTION STAGE
# ============================================================================
FROM python:3.11-slim as production

# Image metadata
LABEL maintainer="stefan@axiestudio.se"
LABEL version="1.0.0"
LABEL description="AI Chatbot Platform - Enterprise Grade"
LABEL org.opencontainers.image.source="https://github.com/axiestudio/aichatbot"
LABEL org.opencontainers.image.url="https://hub.docker.com/r/axiestudio/aichatbot"
LABEL org.opencontainers.image.documentation="https://github.com/axiestudio/aichatbot/blob/main/README.md"
LABEL org.opencontainers.image.vendor="Axie Studio"
LABEL org.opencontainers.image.licenses="MIT"

# Production environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
ENV ENVIRONMENT=production
ENV PATH="/opt/venv/bin:$PATH"
ENV PORT=8000

# Install runtime dependencies (minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* \
    && rm -rf /var/tmp/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Create application directory
WORKDIR /app

# Create non-root user for security
RUN groupadd -r chatbot && \
    useradd -r -g chatbot -d /app -s /bin/bash chatbot

# Copy backend application code
COPY --chown=chatbot:chatbot backend/ .

# Create necessary directories with proper permissions
RUN mkdir -p /app/uploads /app/logs /app/static && \
    chown -R chatbot:chatbot /app && \
    chmod -R 755 /app

# Switch to non-root user
USER chatbot

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Production startup
CMD ["python", "start.py"]
