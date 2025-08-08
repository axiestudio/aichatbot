"""
Enterprise Monitoring API - Comprehensive system monitoring and metrics
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta

from app.services.enterprise_service_manager import enterprise_service_manager
from app.core.dependencies import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/health/comprehensive")
async def comprehensive_health_check():
    """
    Comprehensive health check for all enterprise services
    Returns detailed health status for each service
    """
    try:
        health_status = await enterprise_service_manager.health_check_all_services()
        return health_status
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Health check failed")


@router.get("/metrics/all")
async def get_all_service_metrics():
    """
    Get comprehensive metrics from all enterprise services
    """
    try:
        metrics = enterprise_service_manager.get_service_metrics()
        return metrics
    except Exception as e:
        logger.error(f"Failed to get service metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve metrics")


@router.get("/services/status")
async def get_services_status():
    """
    Get current status of all registered services
    """
    try:
        services_info = {}
        
        for service_name, service in enterprise_service_manager.services.items():
            service_info = {
                "name": service_name,
                "type": type(service).__name__,
                "health_status": enterprise_service_manager.service_health.get(service_name, {}),
                "has_health_check": hasattr(service, 'health_check'),
                "has_metrics": hasattr(service, 'get_stats') or hasattr(service, 'get_metrics'),
                "has_shutdown": hasattr(service, 'shutdown') or hasattr(service, 'stop_monitoring')
            }
            services_info[service_name] = service_info
        
        return {
            "total_services": len(services_info),
            "services": services_info,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get services status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get services status")


@router.post("/services/{service_name}/restart")
async def restart_service(
    service_name: str,
    current_user: str = Depends(get_current_user)
):
    """
    Restart a specific service (admin only)
    """
    try:
        if service_name not in enterprise_service_manager.services:
            raise HTTPException(status_code=404, detail=f"Service {service_name} not found")
        
        service = enterprise_service_manager.services[service_name]
        
        # Stop the service
        if hasattr(service, 'shutdown'):
            await service.shutdown()
        elif hasattr(service, 'stop_monitoring'):
            await service.stop_monitoring()
        
        # Start the service
        if hasattr(service, 'initialize'):
            await service.initialize()
        elif hasattr(service, 'start_monitoring'):
            await service.start_monitoring()
        
        # Update health status
        enterprise_service_manager.service_health[service_name] = {
            "status": "restarted",
            "last_check": datetime.utcnow(),
            "restarted_at": datetime.utcnow(),
            "restarted_by": current_user
        }
        
        logger.info(f"Service {service_name} restarted by {current_user}")
        
        return {
            "message": f"Service {service_name} restarted successfully",
            "timestamp": datetime.utcnow().isoformat(),
            "restarted_by": current_user
        }
        
    except Exception as e:
        logger.error(f"Failed to restart service {service_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to restart service: {str(e)}")


@router.get("/performance/summary")
async def get_performance_summary():
    """
    Get performance summary across all services
    """
    try:
        metrics = enterprise_service_manager.get_service_metrics()
        
        # Aggregate performance data
        summary = {
            "timestamp": datetime.utcnow().isoformat(),
            "overall_performance": "good",  # This would be calculated based on metrics
            "service_count": len(metrics.get("services", {})),
            "healthy_services": 0,
            "degraded_services": 0,
            "failed_services": 0,
            "key_metrics": {}
        }
        
        # Analyze service health
        for service_name, service_metrics in metrics.get("services", {}).items():
            if "error" in service_metrics:
                summary["failed_services"] += 1
            elif "status" in service_metrics and service_metrics["status"] == "degraded":
                summary["degraded_services"] += 1
            else:
                summary["healthy_services"] += 1
        
        # Calculate overall performance
        if summary["failed_services"] > 0:
            summary["overall_performance"] = "critical" if summary["failed_services"] > summary["healthy_services"] else "degraded"
        elif summary["degraded_services"] > 0:
            summary["overall_performance"] = "degraded"
        
        return summary
        
    except Exception as e:
        logger.error(f"Failed to get performance summary: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get performance summary")


@router.get("/alerts/active")
async def get_active_alerts():
    """
    Get active alerts from all services
    """
    try:
        alerts = []
        
        # Check service health for alerts
        for service_name, health_info in enterprise_service_manager.service_health.items():
            if health_info.get("status") == "failed":
                alerts.append({
                    "service": service_name,
                    "type": "service_failure",
                    "severity": "critical",
                    "message": f"Service {service_name} has failed",
                    "error": health_info.get("error"),
                    "timestamp": health_info.get("last_check")
                })
        
        return {
            "active_alerts": alerts,
            "alert_count": len(alerts),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get active alerts: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get active alerts")


@router.get("/system/info")
async def get_system_info():
    """
    Get comprehensive system information
    """
    try:
        import psutil
        import platform
        
        system_info = {
            "platform": {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor()
            },
            "resources": {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory": {
                    "total": psutil.virtual_memory().total,
                    "available": psutil.virtual_memory().available,
                    "percent": psutil.virtual_memory().percent
                },
                "disk": {
                    "total": psutil.disk_usage('/').total,
                    "free": psutil.disk_usage('/').free,
                    "percent": psutil.disk_usage('/').percent
                }
            },
            "services": {
                "total": len(enterprise_service_manager.services),
                "healthy": len([h for h in enterprise_service_manager.service_health.values() if h.get("status") == "healthy"]),
                "failed": len([h for h in enterprise_service_manager.service_health.values() if h.get("status") == "failed"])
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return system_info
        
    except ImportError:
        # psutil not available
        return {
            "services": {
                "total": len(enterprise_service_manager.services),
                "healthy": len([h for h in enterprise_service_manager.service_health.values() if h.get("status") == "healthy"]),
                "failed": len([h for h in enterprise_service_manager.service_health.values() if h.get("status") == "failed"])
            },
            "timestamp": datetime.utcnow().isoformat(),
            "note": "System resource monitoring requires psutil package"
        }
    except Exception as e:
        logger.error(f"Failed to get system info: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get system information")
