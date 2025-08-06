#!/bin/bash

# Production startup script for Railway
echo "🚀 Starting AI Chatbot Platform..."

# Set default values if not provided
export PORT=${PORT:-8000}
export HOST=${HOST:-0.0.0.0}
export WORKERS=${WORKERS:-4}

# Run database migrations (if needed)
echo "📊 Checking database..."

# Start the application with Uvicorn
echo "🌟 Starting application on $HOST:$PORT with $WORKERS workers..."

exec python -m uvicorn app.main:app \
    --host $HOST \
    --port $PORT \
    --workers $WORKERS \
    --access-log \
    --loop uvloop \
    --http httptools
