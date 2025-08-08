#!/usr/bin/env python3
"""
PRODUCTION-READY STARTUP SCRIPT
Optimized for Digital Ocean App Platform deployment
"""

import uvicorn
import sys
import os
import logging
from pathlib import Path

# Ensure we're in the correct directory
backend_dir = Path(__file__).parent.absolute()
os.chdir(backend_dir)
sys.path.insert(0, str(backend_dir))

# Setup basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Production-ready main function"""
    try:
        logger.info("🔍 Step 1: Importing settings...")
        # Import settings after path setup
        from app.core.config import settings
        logger.info("✅ Settings imported successfully")

        logger.info("🔍 Step 2: Importing main app...")
        from app.main import app
        logger.info("✅ Main app imported successfully")

        logger.info("🚀 STARTING AI CHATBOT PLATFORM")
        logger.info(f"Environment: {settings.ENVIRONMENT}")
        logger.info(f"Debug mode: {settings.DEBUG}")
        logger.info(f"Log level: {settings.LOG_LEVEL}")
        logger.info(f"Working directory: {os.getcwd()}")

        # Get port from environment
        port = int(os.getenv("PORT", "8000"))
        logger.info(f"Starting server on port: {port}")

        # Production uvicorn configuration
        uvicorn_config = {
            "app": "app.main:app",
            "host": "0.0.0.0",
            "port": port,
            "log_level": settings.LOG_LEVEL.lower(),
            "access_log": True,
            "reload": False,  # Never reload in production
            "workers": 1,  # Single worker for Digital Ocean
        }

        # Add production optimizations
        if settings.ENVIRONMENT == "production":
            uvicorn_config.update({
                "loop": "uvloop",
                "http": "httptools",
                "lifespan": "on",
                "timeout_keep_alive": 5,
                "timeout_graceful_shutdown": 30,
            })

        logger.info("✅ Starting uvicorn server...")
        uvicorn.run(**uvicorn_config)

    except ImportError as e:
        logger.error(f"❌ IMPORT FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ STARTUP FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
