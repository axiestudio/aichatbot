import logging
import traceback
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.core.config import settings

logger = logging.getLogger(__name__)


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Comprehensive error handling middleware"""
    
    def __init__(self, app):
        super().__init__(app)
        self.error_tracker = ErrorTracker()
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Handle all requests and catch errors"""
        error_id = str(uuid.uuid4())
        start_time = datetime.utcnow()
        
        try:
            # Add error ID to request state for tracking
            request.state.error_id = error_id
            
            # Process request
            response = await call_next(request)
            
            # Log successful requests in debug mode
            if settings.DEBUG:
                duration = (datetime.utcnow() - start_time).total_seconds()
                logger.debug(f"Request {error_id}: {request.method} {request.url} - {response.status_code} ({duration:.3f}s)")
            
            return response
            
        except HTTPException as e:
            # Handle FastAPI HTTP exceptions
            await self.error_tracker.log_error(
                error_id=error_id,
                request=request,
                error=e,
                error_type="HTTPException"
            )
            
            return JSONResponse(
                status_code=e.status_code,
                content={
                    "error": {
                        "message": e.detail,
                        "type": "HTTPException",
                        "status_code": e.status_code,
                        "error_id": error_id,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                }
            )
            
        except Exception as e:
            # Handle unexpected errors
            await self.error_tracker.log_error(
                error_id=error_id,
                request=request,
                error=e,
                error_type="UnhandledException"
            )
            
            # Don't expose internal errors in production
            if settings.ENVIRONMENT == "production":
                error_message = "An internal server error occurred"
                error_details = None
            else:
                error_message = str(e)
                error_details = traceback.format_exc()
            
            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "message": error_message,
                        "type": "InternalServerError",
                        "status_code": 500,
                        "error_id": error_id,
                        "timestamp": datetime.utcnow().isoformat(),
                        "details": error_details
                    }
                }
            )


class ErrorTracker:
    """Track and analyze application errors"""
    
    def __init__(self):
        self.error_log = []
        self.error_stats = {
            "total_errors": 0,
            "errors_by_type": {},
            "errors_by_endpoint": {},
            "recent_errors": []
        }
        self.max_recent_errors = 100
    
    async def log_error(
        self, 
        error_id: str, 
        request: Request, 
        error: Exception, 
        error_type: str
    ):
        """Log error with detailed information"""
        try:
            # Extract request information
            request_info = {
                "method": request.method,
                "url": str(request.url),
                "path": request.url.path,
                "query_params": dict(request.query_params),
                "headers": dict(request.headers),
                "client_ip": self._get_client_ip(request),
                "user_agent": request.headers.get("user-agent", "Unknown")
            }
            
            # Create error record
            error_record = {
                "error_id": error_id,
                "timestamp": datetime.utcnow().isoformat(),
                "error_type": error_type,
                "error_message": str(error),
                "error_class": error.__class__.__name__,
                "traceback": traceback.format_exc(),
                "request": request_info,
                "severity": self._determine_severity(error, error_type)
            }
            
            # Log to file/console
            logger.error(f"Error {error_id}: {error_type} - {str(error)}", extra=error_record)
            
            # Store in memory for analytics
            self.error_log.append(error_record)
            
            # Update statistics
            self._update_error_stats(error_record)
            
            # Send to external monitoring if configured
            await self._send_to_monitoring(error_record)
            
        except Exception as logging_error:
            # Don't let error logging break the application
            logger.critical(f"Failed to log error {error_id}: {str(logging_error)}")
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics"""
        return {
            **self.error_stats,
            "last_updated": datetime.utcnow().isoformat()
        }
    
    def get_recent_errors(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent errors"""
        return self.error_stats["recent_errors"][-limit:]
    
    def get_error_by_id(self, error_id: str) -> Optional[Dict[str, Any]]:
        """Get specific error by ID"""
        for error in self.error_log:
            if error["error_id"] == error_id:
                return error
        return None
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address"""
        # Check for forwarded headers first
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # Fallback to direct client IP
        if hasattr(request, "client") and request.client:
            return request.client.host
        
        return "unknown"
    
    def _determine_severity(self, error: Exception, error_type: str) -> str:
        """Determine error severity level"""
        if isinstance(error, HTTPException):
            if error.status_code >= 500:
                return "high"
            elif error.status_code >= 400:
                return "medium"
            else:
                return "low"
        
        # Critical errors
        critical_errors = [
            "DatabaseError",
            "ConnectionError",
            "AuthenticationError",
            "SecurityError"
        ]
        
        if any(critical in error.__class__.__name__ for critical in critical_errors):
            return "critical"
        
        # High severity errors
        high_errors = [
            "ValueError",
            "TypeError",
            "AttributeError",
            "KeyError"
        ]
        
        if any(high in error.__class__.__name__ for high in high_errors):
            return "high"
        
        return "medium"
    
    def _update_error_stats(self, error_record: Dict[str, Any]):
        """Update error statistics"""
        self.error_stats["total_errors"] += 1
        
        # Count by type
        error_type = error_record["error_type"]
        self.error_stats["errors_by_type"][error_type] = \
            self.error_stats["errors_by_type"].get(error_type, 0) + 1
        
        # Count by endpoint
        endpoint = error_record["request"]["path"]
        self.error_stats["errors_by_endpoint"][endpoint] = \
            self.error_stats["errors_by_endpoint"].get(endpoint, 0) + 1
        
        # Add to recent errors
        self.error_stats["recent_errors"].append({
            "error_id": error_record["error_id"],
            "timestamp": error_record["timestamp"],
            "error_type": error_record["error_type"],
            "error_message": error_record["error_message"],
            "endpoint": endpoint,
            "severity": error_record["severity"]
        })
        
        # Keep only recent errors
        if len(self.error_stats["recent_errors"]) > self.max_recent_errors:
            self.error_stats["recent_errors"] = \
                self.error_stats["recent_errors"][-self.max_recent_errors:]
    
    async def _send_to_monitoring(self, error_record: Dict[str, Any]):
        """Send error to external monitoring service"""
        try:
            # Send to Sentry if configured
            if hasattr(settings, 'SENTRY_DSN') and settings.SENTRY_DSN:
                # This would integrate with Sentry SDK
                pass
            
            # Send to custom monitoring endpoint
            if hasattr(settings, 'MONITORING_WEBHOOK') and settings.MONITORING_WEBHOOK:
                # This would send to a webhook
                pass
                
        except Exception as e:
            logger.warning(f"Failed to send error to monitoring: {str(e)}")


class ValidationError(Exception):
    """Custom validation error"""
    def __init__(self, message: str, field: str = None, code: str = None):
        self.message = message
        self.field = field
        self.code = code
        super().__init__(message)


class BusinessLogicError(Exception):
    """Custom business logic error"""
    def __init__(self, message: str, code: str = None, details: Dict[str, Any] = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(message)


class SecurityError(Exception):
    """Custom security error"""
    def __init__(self, message: str, threat_type: str = None, details: Dict[str, Any] = None):
        self.message = message
        self.threat_type = threat_type
        self.details = details or {}
        super().__init__(message)


class RateLimitError(Exception):
    """Custom rate limit error"""
    def __init__(self, message: str, retry_after: int = None):
        self.message = message
        self.retry_after = retry_after
        super().__init__(message)


def create_error_response(
    message: str,
    status_code: int = 400,
    error_type: str = "ValidationError",
    details: Optional[Dict[str, Any]] = None,
    error_id: Optional[str] = None
) -> JSONResponse:
    """Create standardized error response"""
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "message": message,
                "type": error_type,
                "status_code": status_code,
                "error_id": error_id or str(uuid.uuid4()),
                "timestamp": datetime.utcnow().isoformat(),
                "details": details
            }
        }
    )


def handle_validation_error(error: ValidationError) -> JSONResponse:
    """Handle validation errors"""
    return create_error_response(
        message=error.message,
        status_code=422,
        error_type="ValidationError",
        details={
            "field": error.field,
            "code": error.code
        }
    )


def handle_business_logic_error(error: BusinessLogicError) -> JSONResponse:
    """Handle business logic errors"""
    return create_error_response(
        message=error.message,
        status_code=400,
        error_type="BusinessLogicError",
        details={
            "code": error.code,
            **error.details
        }
    )


def handle_security_error(error: SecurityError) -> JSONResponse:
    """Handle security errors"""
    return create_error_response(
        message="Security violation detected",
        status_code=403,
        error_type="SecurityError",
        details={
            "threat_type": error.threat_type
        }
    )


def handle_rate_limit_error(error: RateLimitError) -> JSONResponse:
    """Handle rate limit errors"""
    headers = {}
    if error.retry_after:
        headers["Retry-After"] = str(error.retry_after)
    
    response = create_error_response(
        message=error.message,
        status_code=429,
        error_type="RateLimitError",
        details={
            "retry_after": error.retry_after
        }
    )
    
    # Add headers to response
    for key, value in headers.items():
        response.headers[key] = value
    
    return response


# Global error tracker instance
error_tracker = ErrorTracker()
