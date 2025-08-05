from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
from datetime import datetime
import logging

from app.core.config import settings
from app.core.database import init_database
from app.api.v1.api import api_router
from app.core.logging import setup_logging
from app.middleware.rate_limit import rate_limit_middleware
from app.middleware.security import security_headers_middleware, input_validation_middleware
from app.middleware.error_handler import ErrorHandlingMiddleware
from app.middleware.security_enhanced import SecurityEnhancementMiddleware

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("Starting up chatbot backend...")

    # Initialize database
    try:
        init_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")

    yield

    logger.info("Shutting down chatbot backend...")

    # Cleanup database connections
    try:
        from app.core.database import db_manager
        await db_manager.cleanup()
        logger.info("Database connections cleaned up")
    except Exception as e:
        logger.error(f"Database cleanup failed: {str(e)}")


# Create FastAPI application
app = FastAPI(
    title="Modern Chatbot Backend",
    description="A comprehensive chatbot system with RAG capabilities",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware
if not settings.DEBUG:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS
    )

# Add enhanced security and error handling middleware
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(SecurityEnhancementMiddleware)

# Add existing security middleware
app.middleware("http")(security_headers_middleware)
app.middleware("http")(input_validation_middleware)
app.middleware("http")(rate_limit_middleware)

# Include API router
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Modern Chatbot Backend API",
        "version": "1.0.0",
        "status": "running",
        "features": [
            "Enhanced RAG System",
            "Document Management",
            "Real-time Chat Monitoring",
            "Advanced Security",
            "Comprehensive Analytics",
            "Multi-provider AI Support"
        ]
    }


@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint"""
    try:
        from app.core.database import db_manager
        from app.services.embedding_service import EmbeddingService

        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "environment": settings.ENVIRONMENT
        }

        # Check database
        try:
            db_connected = await db_manager.check_connection()
            health_status["database"] = "healthy" if db_connected else "unhealthy"
        except Exception as e:
            health_status["database"] = f"error: {str(e)}"

        # Check embedding service
        try:
            embedding_service = EmbeddingService()
            embedding_healthy = await embedding_service.health_check()
            health_status["embedding_service"] = "healthy" if embedding_healthy else "unhealthy"
        except Exception as e:
            health_status["embedding_service"] = f"error: {str(e)}"

        # Overall status
        if any("unhealthy" in str(v) or "error" in str(v) for v in health_status.values()):
            health_status["status"] = "unhealthy"

        return health_status

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
