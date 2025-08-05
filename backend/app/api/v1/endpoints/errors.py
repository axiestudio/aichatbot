"""
Error Reporting API Endpoints
Production-ready error tracking and reporting
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from app.services.error_tracking_service import error_tracker
from app.services.unified_monitoring_service import unified_monitoring
from app.core.tracing import trace_async_function

router = APIRouter()
logger = logging.getLogger(__name__)


class ErrorReport(BaseModel):
    """Error report model"""
    error: Dict[str, Any]
    errorInfo: Optional[Dict[str, Any]] = None
    timestamp: str
    userAgent: str
    url: str
    userId: Optional[str] = None
    sessionId: Optional[str] = None
    additionalContext: Optional[Dict[str, Any]] = None


class ClientErrorReport(BaseModel):
    """Client-side error report"""
    message: str
    stack: Optional[str] = None
    filename: Optional[str] = None
    lineno: Optional[int] = None
    colno: Optional[int] = None
    timestamp: str
    userAgent: str
    url: str
    userId: Optional[str] = None


@router.post("/report")
@trace_async_function("errors.report_frontend_error")
async def report_frontend_error(
    error_report: ErrorReport,
    request: Request
):
    """Report a frontend error for tracking and analysis"""
    
    try:
        # Extract client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Create comprehensive error context
        error_context = {
            "source": "frontend",
            "error_type": "react_error_boundary",
            "client_ip": client_ip,
            "user_agent": error_report.userAgent,
            "url": error_report.url,
            "timestamp": error_report.timestamp,
            "user_id": error_report.userId,
            "session_id": error_report.sessionId,
            "error_details": error_report.error,
            "component_stack": error_report.errorInfo.get("componentStack") if error_report.errorInfo else None,
            "additional_context": error_report.additionalContext or {}
        }
        
        # Create error instance
        error_message = error_report.error.get("message", "Unknown frontend error")
        error_stack = error_report.error.get("stack", "No stack trace available")
        
        # Track the error
        error_tracker.track_error(
            Exception(error_message),
            context=error_context,
            severity="error",
            user_id=error_report.userId
        )
        
        # Log the error
        logger.error(
            f"Frontend error reported: {error_message}",
            extra={
                "error_context": error_context,
                "stack_trace": error_stack
            }
        )
        
        # Track business metric
        unified_monitoring.track_business_metric(
            "frontend_errors",
            1,
            {
                "error_type": error_report.error.get("name", "unknown"),
                "url": error_report.url,
                "user_id": error_report.userId or "anonymous"
            }
        )
        
        return {
            "status": "success",
            "message": "Error reported successfully",
            "error_id": f"fe_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{hash(error_message) % 10000:04d}"
        }
        
    except Exception as e:
        logger.error(f"Failed to process error report: {e}")
        raise HTTPException(status_code=500, detail="Failed to process error report")


@router.post("/client-error")
@trace_async_function("errors.report_client_error")
async def report_client_error(
    error_report: ClientErrorReport,
    request: Request
):
    """Report a client-side JavaScript error"""
    
    try:
        # Extract client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Create error context
        error_context = {
            "source": "frontend",
            "error_type": "javascript_error",
            "client_ip": client_ip,
            "user_agent": error_report.userAgent,
            "url": error_report.url,
            "timestamp": error_report.timestamp,
            "user_id": error_report.userId,
            "filename": error_report.filename,
            "line_number": error_report.lineno,
            "column_number": error_report.colno
        }
        
        # Track the error
        error_tracker.track_error(
            Exception(error_report.message),
            context=error_context,
            severity="warning",
            user_id=error_report.userId
        )
        
        # Log the error
        logger.warning(
            f"Client JavaScript error: {error_report.message}",
            extra={
                "error_context": error_context,
                "stack_trace": error_report.stack
            }
        )
        
        return {
            "status": "success",
            "message": "Client error reported successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to process client error report: {e}")
        raise HTTPException(status_code=500, detail="Failed to process client error report")


@router.get("/stats")
@trace_async_function("errors.get_error_stats")
async def get_error_statistics(
    time_range_hours: int = 24
):
    """Get error statistics for monitoring dashboard"""
    
    try:
        # Get error analytics
        error_analytics = error_tracker.get_error_analytics(time_range_hours)
        
        # Get frontend-specific error stats
        frontend_errors = [
            error for error in error_analytics.get("recent_errors", [])
            if error.get("context", {}).get("source") == "frontend"
        ]
        
        # Calculate frontend error rate
        total_frontend_errors = len(frontend_errors)
        
        # Group by error type
        error_types = {}
        for error in frontend_errors:
            error_type = error.get("context", {}).get("error_type", "unknown")
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        # Group by URL
        error_urls = {}
        for error in frontend_errors:
            url = error.get("context", {}).get("url", "unknown")
            error_urls[url] = error_urls.get(url, 0) + 1
        
        return {
            "time_range_hours": time_range_hours,
            "total_errors": error_analytics.get("total_errors", 0),
            "frontend_errors": total_frontend_errors,
            "error_rate": error_analytics.get("error_rate", 0),
            "error_types": error_types,
            "error_urls": error_urls,
            "recent_errors": frontend_errors[:10],  # Last 10 errors
            "error_trends": error_analytics.get("error_trends", [])
        }
        
    except Exception as e:
        logger.error(f"Failed to get error statistics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get error statistics")


@router.get("/health-impact")
@trace_async_function("errors.get_health_impact")
async def get_error_health_impact():
    """Get error impact on system health"""
    
    try:
        # Get recent error analytics
        error_analytics = error_tracker.get_error_analytics(1)  # Last hour
        
        # Calculate health impact
        total_errors = error_analytics.get("total_errors", 0)
        critical_errors = len([
            error for error in error_analytics.get("recent_errors", [])
            if error.get("severity") == "critical"
        ])
        
        # Determine health status based on errors
        if critical_errors > 5:
            health_status = "critical"
        elif total_errors > 20:
            health_status = "degraded"
        elif total_errors > 5:
            health_status = "warning"
        else:
            health_status = "healthy"
        
        return {
            "health_status": health_status,
            "total_errors_last_hour": total_errors,
            "critical_errors_last_hour": critical_errors,
            "error_rate_per_minute": total_errors / 60,
            "recommendations": get_error_recommendations(health_status, total_errors, critical_errors)
        }
        
    except Exception as e:
        logger.error(f"Failed to get error health impact: {e}")
        raise HTTPException(status_code=500, detail="Failed to get error health impact")


def get_error_recommendations(health_status: str, total_errors: int, critical_errors: int) -> list:
    """Get recommendations based on error patterns"""
    
    recommendations = []
    
    if health_status == "critical":
        recommendations.extend([
            "Immediate investigation required - critical errors detected",
            "Consider rolling back recent deployments",
            "Alert development team immediately"
        ])
    elif health_status == "degraded":
        recommendations.extend([
            "Monitor error patterns closely",
            "Review recent code changes",
            "Consider scaling resources if needed"
        ])
    elif health_status == "warning":
        recommendations.extend([
            "Review error logs for patterns",
            "Monitor user experience metrics",
            "Schedule error review in next sprint"
        ])
    else:
        recommendations.append("System error levels are within normal parameters")
    
    return recommendations
