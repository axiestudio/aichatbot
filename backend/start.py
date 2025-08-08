#!/usr/bin/env python3
"""
Startup script for the Modern Chatbot Backend
"""

import uvicorn
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings

if __name__ == "__main__":
    print("🚀 Starting Modern Chatbot Backend...")
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Debug mode: {settings.DEBUG}")
    print(f"Log level: {settings.LOG_LEVEL}")

    # Get port from environment or default to 8000
    port = int(os.getenv("PORT", "8000"))

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True
    )
