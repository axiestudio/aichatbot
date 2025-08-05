from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
from datetime import datetime
import logging
import psutil
import time
from typing import Dict, Any

from app.core.config import settings
from app.core.database import init_database
from app.core.tracing import tracing_service
from app.api.v1.api import api_router
from app.core.logging import setup_logging
from app.middleware.rate_limit import rate_limit_middleware
from app.middleware.security import security_headers_middleware, input_validation_middleware
from app.middleware.error_handler import ErrorHandlingMiddleware
from app.middleware.security_enhanced import SecurityEnhancementMiddleware
from app.services.advanced_cache_service import cache_service
from app.services.unified_monitoring_service import unified_monitoring

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("Starting up chatbot backend...")

    # Initialize application state
    app.state.start_time = time.time()

    # Initialize distributed tracing
    if settings.ENABLE_TRACING:
        try:
            tracing_service.initialize(app)
            logger.info("Distributed tracing initialized")
        except Exception as e:
            logger.error(f"Tracing initialization failed: {str(e)}")

    # Initialize cache service
    if settings.ENABLE_CACHING:
        try:
            await cache_service.initialize()
            logger.info("Cache service initialized")
        except Exception as e:
            logger.error(f"Cache initialization failed: {str(e)}")

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
    title="🤖 Modern Chatbot Backend",
    description="""
    ## Enterprise-Grade Chatbot System

    A comprehensive, production-ready chatbot system with advanced features:

    ### 🚀 Key Features
    - **RAG (Retrieval-Augmented Generation)** - Enhanced responses with document knowledge
    - **Multi-AI Provider Support** - OpenAI, Anthropic, and more
    - **Advanced Security** - Rate limiting, authentication, input validation
    - **Real-time Monitoring** - Performance metrics, error tracking, health checks
    - **Scalable Architecture** - Kubernetes-ready with auto-scaling
    - **Circuit Breaker Pattern** - Resilient external API calls
    - **Multi-layer Caching** - Redis + memory cache for optimal performance

    ### 📊 Monitoring & Observability
    - Prometheus metrics at `/metrics`
    - Health checks at `/health` and `/api/v1/health`
    - Real-time system metrics and alerts

    ### 🔒 Security Features
    - JWT authentication for admin endpoints
    - Rate limiting and DDoS protection
    - Input validation and sanitization
    """,
    version="1.0.0",
    contact={
        "name": "DevOps Team",
        "email": "devops@company.com"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    },
    openapi_tags=[
        {"name": "chat", "description": "Chat operations"},
        {"name": "admin", "description": "Admin operations"},
        {"name": "config", "description": "Configuration management"},
        {"name": "documents", "description": "Document management"},
        {"name": "health", "description": "Health checks"},
        {"name": "metrics", "description": "Performance metrics"}
    ],
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


@app.get("/health/simple")
async def simple_health_check():
    """Simple health check endpoint for Railway"""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.utcnow().isoformat(),
        "railway": bool(settings.RAILWAY_ENVIRONMENT)
    }


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint for monitoring"""
    try:
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        # Process metrics
        process = psutil.Process()
        process_memory = process.memory_info()

        metrics_data = {
            # System metrics
            "system_cpu_percent": cpu_percent,
            "system_memory_total": memory.total,
            "system_memory_available": memory.available,
            "system_memory_percent": memory.percent,
            "system_disk_total": disk.total,
            "system_disk_used": disk.used,
            "system_disk_percent": (disk.used / disk.total) * 100,

            # Process metrics
            "process_memory_rss": process_memory.rss,
            "process_memory_vms": process_memory.vms,
            "process_cpu_percent": process.cpu_percent(),
            "process_num_threads": process.num_threads(),

            # Application metrics
            "app_uptime_seconds": time.time() - app.state.start_time,
            "app_environment": settings.ENVIRONMENT,
            "timestamp": datetime.utcnow().isoformat()
        }

        return metrics_data

    except Exception as e:
        logger.error(f"Metrics collection failed: {str(e)}")
        return {
            "error": "metrics_collection_failed",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
