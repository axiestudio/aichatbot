"""
Enterprise Operations API
Netflix/Google-style operational endpoints for enterprise management
"""

from fastapi import APIRouter, HTTPException, Depends, Request, BackgroundTasks
from fastapi.responses import PlainTextResponse
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging

from app.core.service_registry import service_registry
from app.core.observability import observability
from app.core.event_streaming import event_bus, real_time_analytics, EventType
from app.core.chaos_engineering import chaos_monkey, resilience_validator
from app.core.zero_trust_security import zero_trust_engine
from app.services.enterprise_service_manager import EnterpriseServiceManager

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ops", tags=["enterprise-operations"])

# Initialize enterprise manager
enterprise_manager = EnterpriseServiceManager()


@router.get("/health/comprehensive")
async def get_comprehensive_health():
    """
    Comprehensive health check across all enterprise services
    Similar to Netflix's health endpoints
    """
    try:
        health_data = await enterprise_manager.health_check_all_services()
        
        # Add enterprise-specific health checks
        enterprise_health = {
            "observability": "unknown",
            "event_streaming": "unknown",
            "chaos_engineering": "unknown",
            "zero_trust_security": "unknown"
        }
        
        # Check observability stack
        if service_registry.is_service_available("observability_stack"):
            try:
                obs_health = observability.get_health_dashboard()
                enterprise_health["observability"] = "healthy"
            except Exception as e:
                enterprise_health["observability"] = f"error: {str(e)}"
        else:
            enterprise_health["observability"] = "unavailable"
            
        # Check event streaming
        if service_registry.is_service_available("event_bus"):
            try:
                analytics = await event_bus.get_analytics()
                enterprise_health["event_streaming"] = "healthy"
            except Exception as e:
                enterprise_health["event_streaming"] = f"error: {str(e)}"
        else:
            enterprise_health["event_streaming"] = "unavailable"
            
        # Check chaos engineering
        if service_registry.is_service_available("chaos_engineering"):
            try:
                chaos_status = chaos_monkey.get_chaos_status()
                enterprise_health["chaos_engineering"] = "healthy"
            except Exception as e:
                enterprise_health["chaos_engineering"] = f"error: {str(e)}"
        else:
            enterprise_health["chaos_engineering"] = "unavailable"
            
        # Check zero trust security
        if service_registry.is_service_available("zero_trust_security"):
            try:
                security_metrics = zero_trust_engine.get_security_metrics()
                enterprise_health["zero_trust_security"] = "healthy"
            except Exception as e:
                enterprise_health["zero_trust_security"] = f"error: {str(e)}"
        else:
            enterprise_health["zero_trust_security"] = "unavailable"
            
        health_data["enterprise_services"] = enterprise_health
        
        return health_data
        
    except Exception as e:
        logger.error(f"Comprehensive health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")


@router.get("/metrics/prometheus", response_class=PlainTextResponse)
async def get_prometheus_metrics():
    """
    Prometheus metrics endpoint
    """
    try:
        if service_registry.is_service_available("observability_stack"):
            return observability.metrics.export_prometheus_metrics()
        else:
            return "# Observability stack not available\n"
    except Exception as e:
        logger.error(f"Failed to export Prometheus metrics: {e}")
        return f"# Error exporting metrics: {str(e)}\n"


@router.get("/analytics/real-time")
async def get_real_time_analytics():
    """
    Real-time analytics dashboard
    """
    try:
        analytics_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "service_metrics": service_registry.get_service_stats(),
            "event_analytics": {},
            "real_time_metrics": {},
            "observability_summary": {}
        }
        
        # Event streaming analytics
        if service_registry.is_service_available("event_bus"):
            analytics_data["event_analytics"] = await event_bus.get_analytics()
            
        # Real-time metrics
        if service_registry.is_service_available("real_time_analytics"):
            analytics_data["real_time_metrics"] = real_time_analytics.get_real_time_metrics()
            
        # Observability summary
        if service_registry.is_service_available("observability_stack"):
            analytics_data["observability_summary"] = observability.get_health_dashboard()
            
        return analytics_data
        
    except Exception as e:
        logger.error(f"Failed to get real-time analytics: {e}")
        raise HTTPException(status_code=500, detail="Analytics retrieval failed")


@router.get("/chaos/status")
async def get_chaos_status():
    """
    Chaos engineering status and controls
    """
    try:
        if not service_registry.is_service_available("chaos_engineering"):
            return {"status": "unavailable", "message": "Chaos engineering not enabled"}
            
        return chaos_monkey.get_chaos_status()
        
    except Exception as e:
        logger.error(f"Failed to get chaos status: {e}")
        raise HTTPException(status_code=500, detail="Chaos status retrieval failed")


@router.post("/chaos/enable")
async def enable_chaos_engineering(safety_mode: bool = True):
    """
    Enable chaos engineering
    """
    try:
        if not service_registry.is_service_available("chaos_engineering"):
            raise HTTPException(status_code=404, detail="Chaos engineering not available")
            
        chaos_monkey.enable_chaos(safety_mode=safety_mode)
        
        # Start chaos loop in background
        import asyncio
        asyncio.create_task(chaos_monkey.start_chaos_loop())
        
        return {
            "status": "enabled",
            "safety_mode": safety_mode,
            "message": "Chaos engineering enabled"
        }
        
    except Exception as e:
        logger.error(f"Failed to enable chaos engineering: {e}")
        raise HTTPException(status_code=500, detail="Failed to enable chaos engineering")


@router.post("/chaos/disable")
async def disable_chaos_engineering():
    """
    Disable chaos engineering
    """
    try:
        if not service_registry.is_service_available("chaos_engineering"):
            raise HTTPException(status_code=404, detail="Chaos engineering not available")
            
        chaos_monkey.disable_chaos()
        
        return {
            "status": "disabled",
            "message": "Chaos engineering disabled"
        }
        
    except Exception as e:
        logger.error(f"Failed to disable chaos engineering: {e}")
        raise HTTPException(status_code=500, detail="Failed to disable chaos engineering")


@router.get("/security/threats")
async def get_security_threats(limit: int = 100):
    """
    Get recent security threats and analysis
    """
    try:
        if not service_registry.is_service_available("zero_trust_security"):
            return {"status": "unavailable", "message": "Zero trust security not enabled"}
            
        security_metrics = zero_trust_engine.get_security_metrics()
        
        # Get recent events from event bus if available
        recent_security_events = []
        if service_registry.is_service_available("event_bus"):
            security_stream = event_bus.get_stream("security")
            if security_stream:
                events = await security_stream.get_events(
                    event_type=EventType.SECURITY_ALERT,
                    limit=limit
                )
                recent_security_events = [event.to_dict() for event in events]
                
        return {
            "security_metrics": security_metrics,
            "recent_threats": recent_security_events,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get security threats: {e}")
        raise HTTPException(status_code=500, detail="Security threat retrieval failed")


@router.get("/events/stream/{stream_name}")
async def get_event_stream(stream_name: str, limit: int = 100, event_type: Optional[str] = None):
    """
    Get events from a specific stream
    """
    try:
        if not service_registry.is_service_available("event_bus"):
            raise HTTPException(status_code=404, detail="Event streaming not available")
            
        stream = event_bus.get_stream(stream_name)
        if not stream:
            raise HTTPException(status_code=404, detail=f"Stream '{stream_name}' not found")
            
        # Convert event_type string to enum if provided
        event_type_enum = None
        if event_type:
            try:
                event_type_enum = EventType(event_type)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid event type: {event_type}")
                
        events = await stream.get_events(
            event_type=event_type_enum,
            limit=limit
        )
        
        return {
            "stream_name": stream_name,
            "event_count": len(events),
            "events": [event.to_dict() for event in events],
            "stream_metrics": stream.get_metrics(),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get event stream: {e}")
        raise HTTPException(status_code=500, detail="Event stream retrieval failed")


@router.post("/events/publish")
async def publish_event(
    stream_name: str,
    event_type: str,
    data: Dict[str, Any],
    source_service: str = "api"
):
    """
    Publish event to stream
    """
    try:
        if not service_registry.is_service_available("event_bus"):
            raise HTTPException(status_code=404, detail="Event streaming not available")
            
        # Convert event_type string to enum
        try:
            event_type_enum = EventType(event_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid event type: {event_type}")
            
        await event_bus.publish(
            stream_name=stream_name,
            event_type=event_type_enum,
            data=data,
            source_service=source_service
        )
        
        return {
            "status": "published",
            "stream_name": stream_name,
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to publish event: {e}")
        raise HTTPException(status_code=500, detail="Event publishing failed")


@router.get("/resilience/validate")
async def validate_system_resilience():
    """
    Validate system resilience
    """
    try:
        if not service_registry.is_service_available("chaos_engineering"):
            return {"status": "unavailable", "message": "Chaos engineering not enabled"}
            
        validation_results = await resilience_validator.validate_resilience()
        
        return validation_results
        
    except Exception as e:
        logger.error(f"Failed to validate resilience: {e}")
        raise HTTPException(status_code=500, detail="Resilience validation failed")


@router.get("/dashboard/executive")
async def get_executive_dashboard():
    """
    Executive dashboard with high-level metrics
    """
    try:
        dashboard = {
            "timestamp": datetime.utcnow().isoformat(),
            "system_status": "unknown",
            "key_metrics": {},
            "alerts": [],
            "performance_summary": {},
            "security_summary": {},
            "business_metrics": {}
        }
        
        # Get comprehensive health
        health = await enterprise_manager.health_check_all_services()
        dashboard["system_status"] = health.get("overall_status", "unknown")
        
        # Key metrics from observability
        if service_registry.is_service_available("observability_stack"):
            obs_dashboard = observability.get_health_dashboard()
            dashboard["key_metrics"] = obs_dashboard.get("metrics_summary", {})
            
        # Real-time analytics
        if service_registry.is_service_available("real_time_analytics"):
            rt_metrics = real_time_analytics.get_real_time_metrics()
            dashboard["performance_summary"] = rt_metrics.get("metrics", {})
            
        # Security summary
        if service_registry.is_service_available("zero_trust_security"):
            security_metrics = zero_trust_engine.get_security_metrics()
            dashboard["security_summary"] = security_metrics
            
        # Business metrics (would be calculated from events)
        dashboard["business_metrics"] = {
            "total_sessions": 0,
            "active_users": 0,
            "messages_per_hour": 0,
            "ai_response_time_avg": 0,
            "error_rate": 0
        }
        
        return dashboard
        
    except Exception as e:
        logger.error(f"Failed to get executive dashboard: {e}")
        raise HTTPException(status_code=500, detail="Dashboard retrieval failed")
