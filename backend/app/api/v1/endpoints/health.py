"""
Health Check API Endpoints
Production-grade health monitoring endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
import time

from ....services.health_service import health_service

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/")
async def basic_health_check():
    """Basic health check endpoint for load balancers"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "chatbot-backend"
    }


@router.get("/live")
async def liveness_probe():
    """Kubernetes liveness probe endpoint"""
    return {
        "status": "alive",
        "timestamp": time.time()
    }


@router.get("/ready")
async def readiness_probe():
    """Kubernetes readiness probe endpoint"""
    try:
        # Quick database check
        from ....core.database import get_db
        from sqlalchemy import text
        
        db = next(get_db())
        db.execute(text("SELECT 1")).scalar()
        
        return {
            "status": "ready",
            "timestamp": time.time()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service not ready: {str(e)}"
        )


@router.get("/detailed")
async def detailed_health_check():
    """Detailed health check with all system components"""
    health_data = await health_service.get_comprehensive_health()
    
    # Return appropriate HTTP status based on health
    if health_data["status"] == "critical":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=health_data
        )
    elif health_data["status"] == "degraded":
        raise HTTPException(
            status_code=status.HTTP_206_PARTIAL_CONTENT,
            detail=health_data
        )
    
    return health_data


@router.get("/metrics")
async def health_metrics():
    """Prometheus-compatible metrics endpoint"""
    health_data = await health_service.get_comprehensive_health()
    
    # Convert to Prometheus format
    metrics = []
    
    # System metrics
    if "system_resources" in health_data["checks"]:
        sys_data = health_data["checks"]["system_resources"]
        if "cpu_percent" in sys_data:
            metrics.append(f"system_cpu_usage_percent {sys_data['cpu_percent']}")
        if "memory_percent" in sys_data:
            metrics.append(f"system_memory_usage_percent {sys_data['memory_percent']}")
        if "disk_percent" in sys_data:
            metrics.append(f"system_disk_usage_percent {sys_data['disk_percent']}")
    
    # Database metrics
    if "database" in health_data["checks"]:
        db_data = health_data["checks"]["database"]
        if "response_time_ms" in db_data:
            metrics.append(f"database_response_time_ms {db_data['response_time_ms']}")
        if "table_counts" in db_data:
            for table, count in db_data["table_counts"].items():
                metrics.append(f"database_table_count{{table=\"{table}\"}} {count}")
    
    # WebSocket metrics
    if "websocket" in health_data["checks"]:
        ws_data = health_data["checks"]["websocket"]
        if "total_connections" in ws_data:
            metrics.append(f"websocket_connections_total {ws_data['total_connections']}")
        if "total_instances" in ws_data:
            metrics.append(f"websocket_instances_total {ws_data['total_instances']}")
    
    # Uptime
    metrics.append(f"system_uptime_seconds {health_data['uptime_seconds']}")
    
    # Health status (1 = healthy, 0.5 = degraded, 0 = critical)
    status_value = 1 if health_data["status"] == "healthy" else 0.5 if health_data["status"] == "degraded" else 0
    metrics.append(f"system_health_status {status_value}")
    
    return "\n".join(metrics)


@router.get("/database")
async def database_health():
    """Database-specific health check"""
    health_data = await health_service.get_comprehensive_health()
    db_health = health_data["checks"].get("database", {})
    
    if db_health.get("status") == "critical":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=db_health
        )
    
    return db_health


@router.get("/redis")
async def redis_health():
    """Redis-specific health check"""
    health_data = await health_service.get_comprehensive_health()
    redis_health = health_data["checks"].get("redis", {})
    
    return redis_health


@router.get("/websocket")
async def websocket_health():
    """WebSocket-specific health check"""
    health_data = await health_service.get_comprehensive_health()
    ws_health = health_data["checks"].get("websocket", {})
    
    return ws_health


@router.get("/system")
async def system_health():
    """System resources health check"""
    health_data = await health_service.get_comprehensive_health()
    system_health = health_data["checks"].get("system_resources", {})
    
    if system_health.get("status") == "critical":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=system_health
        )
    
    return system_health
