"""
Advanced Monitoring API Endpoints
Comprehensive system monitoring, metrics, and health checks
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta

from app.services.unified_monitoring_service import unified_monitoring
from app.services.circuit_breaker_service import circuit_manager
from app.services.advanced_cache_service import cache_service
from app.services.performance_monitoring_service import performance_service
from app.services.error_tracking_service import error_tracker
from app.core.dependencies import get_current_user
from app.core.tracing import trace_async_function, get_trace_context

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/health/detailed", response_model=Dict[str, Any])
@trace_async_function("monitoring.detailed_health_check")
async def get_detailed_health():
    """Get comprehensive system health status"""
    
    try:
        health_data = unified_monitoring.get_health_status()
        
        # Add trace context for debugging
        trace_context = get_trace_context()
        if trace_context.get("trace_id"):
            health_data["trace_id"] = trace_context["trace_id"]
        
        return health_data
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")


@router.get("/metrics/system", response_model=Dict[str, Any])
@trace_async_function("monitoring.system_metrics")
async def get_system_metrics(current_user: str = Depends(get_current_user)):
    """Get detailed system metrics (admin only)"""
    
    try:
        return unified_monitoring.get_system_metrics()
        
    except Exception as e:
        logger.error(f"System metrics collection failed: {e}")
        raise HTTPException(status_code=500, detail="Metrics collection failed")


@router.get("/metrics/application", response_model=Dict[str, Any])
@trace_async_function("monitoring.application_metrics")
async def get_application_metrics(
    time_range_hours: int = Query(24, ge=1, le=168),
    current_user: str = Depends(get_current_user)
):
    """Get application performance metrics (admin only)"""
    
    try:
        app_metrics = unified_monitoring.get_application_metrics()
        
        # Add additional metrics
        app_metrics["performance_analytics"] = performance_service.get_request_analytics(time_range_hours)
        app_metrics["database_analytics"] = performance_service.get_database_analytics(time_range_hours)
        app_metrics["error_analytics"] = error_tracker.get_error_analytics(time_range_hours)
        
        return app_metrics
        
    except Exception as e:
        logger.error(f"Application metrics collection failed: {e}")
        raise HTTPException(status_code=500, detail="Application metrics collection failed")


@router.get("/metrics/dashboard", response_model=Dict[str, Any])
@trace_async_function("monitoring.dashboard_data")
async def get_dashboard_data(current_user: str = Depends(get_current_user)):
    """Get comprehensive dashboard data (admin only)"""
    
    try:
        return unified_monitoring.get_comprehensive_dashboard_data()
        
    except Exception as e:
        logger.error(f"Dashboard data collection failed: {e}")
        raise HTTPException(status_code=500, detail="Dashboard data collection failed")


@router.get("/alerts", response_model=List[Dict[str, Any]])
@trace_async_function("monitoring.get_alerts")
async def get_current_alerts(current_user: str = Depends(get_current_user)):
    """Get current system alerts (admin only)"""
    
    try:
        alerts = unified_monitoring.get_alerts()
        
        # Add performance alerts
        perf_alerts = performance_service.get_performance_alerts()
        for alert in perf_alerts:
            alerts.append({
                "type": "performance",
                "severity": alert.get("severity", "warning"),
                "message": f"Performance issue: {alert.get('type', 'unknown')}",
                "details": alert,
                "timestamp": datetime.utcnow().isoformat()
            })
        
        return alerts
        
    except Exception as e:
        logger.error(f"Alerts collection failed: {e}")
        raise HTTPException(status_code=500, detail="Alerts collection failed")


@router.get("/circuit-breakers", response_model=Dict[str, Any])
@trace_async_function("monitoring.circuit_breakers")
async def get_circuit_breaker_status(current_user: str = Depends(get_current_user)):
    """Get circuit breaker status (admin only)"""
    
    try:
        return {
            "health_summary": circuit_manager.get_health_summary(),
            "detailed_stats": circuit_manager.get_all_stats(),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Circuit breaker status collection failed: {e}")
        raise HTTPException(status_code=500, detail="Circuit breaker status collection failed")


@router.post("/circuit-breakers/reset", response_model=Dict[str, str])
@trace_async_function("monitoring.reset_circuit_breakers")
async def reset_circuit_breakers(
    breaker_name: Optional[str] = None,
    current_user: str = Depends(get_current_user)
):
    """Reset circuit breakers (admin only)"""
    
    try:
        if breaker_name:
            breaker = circuit_manager.get_breaker(breaker_name)
            breaker.reset()
            message = f"Circuit breaker '{breaker_name}' reset successfully"
        else:
            circuit_manager.reset_all()
            message = "All circuit breakers reset successfully"
        
        logger.info(f"Circuit breaker reset by {current_user}: {message}")
        
        return {
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Circuit breaker reset failed: {e}")
        raise HTTPException(status_code=500, detail="Circuit breaker reset failed")


@router.get("/cache/stats", response_model=Dict[str, Any])
@trace_async_function("monitoring.cache_stats")
async def get_cache_statistics(current_user: str = Depends(get_current_user)):
    """Get cache performance statistics (admin only)"""
    
    try:
        return cache_service.get_stats()
        
    except Exception as e:
        logger.error(f"Cache statistics collection failed: {e}")
        raise HTTPException(status_code=500, detail="Cache statistics collection failed")


@router.post("/cache/clear", response_model=Dict[str, Any])
@trace_async_function("monitoring.clear_cache")
async def clear_cache(
    pattern: Optional[str] = None,
    current_user: str = Depends(get_current_user)
):
    """Clear cache entries (admin only)"""
    
    try:
        cleared_count = await cache_service.clear(pattern)
        
        message = f"Cleared {cleared_count} cache entries"
        if pattern:
            message += f" matching pattern '{pattern}'"
        
        logger.info(f"Cache cleared by {current_user}: {message}")
        
        return {
            "message": message,
            "cleared_count": cleared_count,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Cache clear failed: {e}")
        raise HTTPException(status_code=500, detail="Cache clear failed")


@router.get("/errors/analytics", response_model=Dict[str, Any])
@trace_async_function("monitoring.error_analytics")
async def get_error_analytics(
    time_range_hours: int = Query(24, ge=1, le=168),
    current_user: str = Depends(get_current_user)
):
    """Get error analytics and trends (admin only)"""
    
    try:
        return error_tracker.get_error_analytics(time_range_hours)
        
    except Exception as e:
        logger.error(f"Error analytics collection failed: {e}")
        raise HTTPException(status_code=500, detail="Error analytics collection failed")


@router.get("/performance/summary", response_model=Dict[str, Any])
@trace_async_function("monitoring.performance_summary")
async def get_performance_summary(
    time_range_hours: int = Query(24, ge=1, le=168),
    current_user: str = Depends(get_current_user)
):
    """Get performance summary and analytics (admin only)"""
    
    try:
        return {
            "request_analytics": performance_service.get_request_analytics(time_range_hours),
            "database_analytics": performance_service.get_database_analytics(time_range_hours),
            "performance_alerts": performance_service.get_performance_alerts(),
            "time_range_hours": time_range_hours,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Performance summary collection failed: {e}")
        raise HTTPException(status_code=500, detail="Performance summary collection failed")


@router.post("/metrics/business", response_model=Dict[str, str])
@trace_async_function("monitoring.track_business_metric")
async def track_business_metric(
    metric_name: str,
    value: float,
    tags: Optional[Dict[str, str]] = None,
    current_user: str = Depends(get_current_user)
):
    """Track custom business metric (admin only)"""
    
    try:
        unified_monitoring.track_business_metric(metric_name, value, tags)
        
        logger.info(f"Business metric tracked by {current_user}: {metric_name} = {value}")
        
        return {
            "message": f"Business metric '{metric_name}' tracked successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Business metric tracking failed: {e}")
        raise HTTPException(status_code=500, detail="Business metric tracking failed")


@router.get("/trace/{trace_id}", response_model=Dict[str, Any])
@trace_async_function("monitoring.get_trace")
async def get_trace_details(
    trace_id: str,
    current_user: str = Depends(get_current_user)
):
    """Get trace details for debugging (admin only)"""
    
    try:
        # This would integrate with your tracing backend (Jaeger, etc.)
        # For now, return basic trace information
        
        return {
            "trace_id": trace_id,
            "message": "Trace details would be retrieved from tracing backend",
            "jaeger_url": f"http://localhost:16686/trace/{trace_id}",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Trace details retrieval failed: {e}")
        raise HTTPException(status_code=500, detail="Trace details retrieval failed")
