"""
Enterprise Middleware Stack
Comprehensive middleware integrating observability, security, and event streaming
"""

import time
import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.service_registry import service_registry
from app.core.observability import observability
from app.core.event_streaming import event_bus, EventType
from app.core.zero_trust_security import zero_trust_engine, SecurityAction
from app.core.tracing import tracing_service

logger = logging.getLogger(__name__)


class EnterpriseMiddleware(BaseHTTPMiddleware):
    """
    Enterprise-grade middleware that provides:
    - Comprehensive request/response observability
    - Zero trust security evaluation
    - Real-time event streaming
    - Distributed tracing
    - Performance monitoring
    """
    
    def __init__(self, app, enable_security: bool = True, enable_observability: bool = True):
        super().__init__(app)
        self.enable_security = enable_security
        self.enable_observability = enable_observability
        self.excluded_paths = {"/health", "/metrics", "/docs", "/openapi.json"}
        
    async def dispatch(self, request: Request, call_next) -> Response:
        """Main middleware dispatch"""
        start_time = time.time()
        
        # Skip middleware for excluded paths
        if request.url.path in self.excluded_paths:
            return await call_next(request)
            
        # Extract request context
        context = await self._extract_request_context(request)
        
        # Security evaluation
        security_action = SecurityAction.ALLOW
        if self.enable_security and service_registry.is_service_available("zero_trust_security"):
            security_action = await self._evaluate_security(request, context)
            
            # Block request if security policy requires it
            if security_action == SecurityAction.BLOCK:
                return await self._create_security_response(request, "Request blocked by security policy", 403)
                
        # Start distributed tracing
        trace_context = None
        if service_registry.is_service_available("observability_stack"):
            trace_context = await self._start_tracing(request, context)
            
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate metrics
            duration = time.time() - start_time
            
            # Record observability data
            if self.enable_observability:
                await self._record_observability(request, response, context, duration)
                
            # Publish events
            await self._publish_events(request, response, context, duration, security_action)
            
            # Add enterprise headers
            self._add_enterprise_headers(response, context, duration)
            
            return response
            
        except Exception as e:
            # Handle errors
            duration = time.time() - start_time
            
            # Record error observability
            if self.enable_observability:
                await self._record_error_observability(request, e, context, duration)
                
            # Publish error events
            await self._publish_error_events(request, e, context, duration)
            
            # Re-raise the exception
            raise
            
        finally:
            # End tracing
            if trace_context:
                await self._end_tracing(trace_context, request)
                
    async def _extract_request_context(self, request: Request) -> Dict[str, Any]:
        """Extract comprehensive request context"""
        # Get client IP (handle proxies)
        client_ip = request.client.host
        if "x-forwarded-for" in request.headers:
            client_ip = request.headers["x-forwarded-for"].split(",")[0].strip()
        elif "x-real-ip" in request.headers:
            client_ip = request.headers["x-real-ip"]
            
        # Extract user context
        user_id = None
        session_id = None
        
        # Try to extract from headers or JWT
        if "authorization" in request.headers:
            # Would decode JWT to get user_id
            pass
            
        if "x-session-id" in request.headers:
            session_id = request.headers["x-session-id"]
            
        return {
            "ip_address": client_ip,
            "user_agent": request.headers.get("user-agent", ""),
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "headers": dict(request.headers),
            "user_id": user_id,
            "session_id": session_id,
            "timestamp": datetime.utcnow()
        }
        
    async def _evaluate_security(self, request: Request, context: Dict[str, Any]) -> SecurityAction:
        """Evaluate request security using zero trust engine"""
        try:
            # Read request body for payload analysis
            payload = None
            if request.method in ["POST", "PUT", "PATCH"]:
                try:
                    body = await request.body()
                    if body:
                        payload = body.decode('utf-8')
                except Exception:
                    payload = None
                    
            # Evaluate security context
            security_context = await zero_trust_engine.evaluate_request(
                user_id=context.get("user_id"),
                session_id=context.get("session_id"),
                ip_address=context["ip_address"],
                headers=context["headers"],
                payload=payload,
                action=f"{request.method} {request.url.path}"
            )
            
            # Detect threats
            threats = await zero_trust_engine.detect_threats(security_context)
            
            # Enforce policy
            action = await zero_trust_engine.enforce_policy(threats)
            
            # Log security evaluation
            if threats:
                logger.warning(f"Security threats detected: {len(threats)} threats for {context['ip_address']}")
                
                # Publish security event
                if service_registry.is_service_available("event_bus"):
                    await event_bus.publish(
                        stream_name="security",
                        event_type=EventType.SECURITY_ALERT,
                        data={
                            "threats": [
                                {
                                    "threat_id": t.threat_id,
                                    "threat_type": t.threat_type,
                                    "threat_level": t.threat_level.value,
                                    "confidence": t.confidence,
                                    "description": t.description,
                                    "indicators": t.indicators
                                }
                                for t in threats
                            ],
                            "security_context": {
                                "trust_score": security_context.trust_score,
                                "risk_factors": security_context.risk_factors,
                                "ip_address": security_context.ip_address,
                                "user_agent": security_context.user_agent
                            },
                            "recommended_action": action.value
                        },
                        source_service="enterprise_middleware",
                        user_id=context.get("user_id"),
                        session_id=context.get("session_id")
                    )
                    
            return action
            
        except Exception as e:
            logger.error(f"Security evaluation failed: {e}")
            return SecurityAction.ALLOW  # Fail open for availability
            
    async def _start_tracing(self, request: Request, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Start distributed tracing"""
        try:
            span_name = f"{request.method} {request.url.path}"
            
            # Start span with tracing service
            span = tracing_service.start_span(
                span_name,
                attributes={
                    "http.method": request.method,
                    "http.url": str(request.url),
                    "http.user_agent": context.get("user_agent", ""),
                    "client.ip": context["ip_address"],
                    "user.id": context.get("user_id"),
                    "session.id": context.get("session_id")
                }
            )
            
            return {
                "span": span,
                "span_name": span_name,
                "start_time": time.time()
            }
            
        except Exception as e:
            logger.error(f"Failed to start tracing: {e}")
            return None
            
    async def _record_observability(
        self, 
        request: Request, 
        response: Response, 
        context: Dict[str, Any], 
        duration: float
    ):
        """Record comprehensive observability data"""
        try:
            if not service_registry.is_service_available("observability_stack"):
                return
                
            # Record HTTP metrics
            observability.metrics.record_http_request(
                method=request.method,
                endpoint=request.url.path,
                status_code=response.status_code,
                duration=duration
            )
            
            # Log structured request
            observability.logger.info(
                f"{request.method} {request.url.path} - {response.status_code}",
                user_id=context.get("user_id"),
                session_id=context.get("session_id"),
                metadata={
                    "duration_ms": duration * 1000,
                    "status_code": response.status_code,
                    "ip_address": context["ip_address"],
                    "user_agent": context.get("user_agent", "")
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to record observability: {e}")
            
    async def _publish_events(
        self, 
        request: Request, 
        response: Response, 
        context: Dict[str, Any], 
        duration: float,
        security_action: SecurityAction
    ):
        """Publish request/response events"""
        try:
            if not service_registry.is_service_available("event_bus"):
                return
                
            # Publish performance metric event
            await event_bus.publish(
                stream_name="performance",
                event_type=EventType.PERFORMANCE_METRIC,
                data={
                    "metric_name": "http_request_duration",
                    "metric_value": duration,
                    "method": request.method,
                    "endpoint": request.url.path,
                    "status_code": response.status_code,
                    "security_action": security_action.value
                },
                source_service="enterprise_middleware",
                user_id=context.get("user_id"),
                session_id=context.get("session_id")
            )
            
        except Exception as e:
            logger.error(f"Failed to publish events: {e}")
            
    async def _record_error_observability(
        self, 
        request: Request, 
        error: Exception, 
        context: Dict[str, Any], 
        duration: float
    ):
        """Record error observability data"""
        try:
            if not service_registry.is_service_available("observability_stack"):
                return
                
            # Record error metrics
            observability.metrics.record_error(
                service="api",
                error_type=type(error).__name__,
                error_message=str(error)
            )
            
            # Log structured error
            observability.logger.error(
                f"Request failed: {request.method} {request.url.path}",
                user_id=context.get("user_id"),
                session_id=context.get("session_id"),
                metadata={
                    "error_type": type(error).__name__,
                    "error_message": str(error),
                    "duration_ms": duration * 1000,
                    "ip_address": context["ip_address"],
                    "user_agent": context.get("user_agent", "")
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to record error observability: {e}")
            
    async def _publish_error_events(
        self, 
        request: Request, 
        error: Exception, 
        context: Dict[str, Any], 
        duration: float
    ):
        """Publish error events"""
        try:
            if not service_registry.is_service_available("event_bus"):
                return
                
            await event_bus.publish(
                stream_name="errors",
                event_type=EventType.ERROR_OCCURRED,
                data={
                    "error_type": type(error).__name__,
                    "error_message": str(error),
                    "method": request.method,
                    "endpoint": request.url.path,
                    "duration_ms": duration * 1000
                },
                source_service="enterprise_middleware",
                user_id=context.get("user_id"),
                session_id=context.get("session_id")
            )
            
        except Exception as e:
            logger.error(f"Failed to publish error events: {e}")
            
    async def _end_tracing(self, trace_context: Dict[str, Any], request: Request):
        """End distributed tracing"""
        try:
            if trace_context and "span" in trace_context:
                span = trace_context["span"]
                if hasattr(span, "end"):
                    span.end()
                    
        except Exception as e:
            logger.error(f"Failed to end tracing: {e}")
            
    async def _create_security_response(self, request: Request, message: str, status_code: int) -> Response:
        """Create security response"""
        from fastapi.responses import JSONResponse
        
        return JSONResponse(
            status_code=status_code,
            content={
                "error": "Security Policy Violation",
                "message": message,
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": getattr(request.state, "request_id", "unknown")
            }
        )
        
    def _add_enterprise_headers(self, response: Response, context: Dict[str, Any], duration: float):
        """Add enterprise headers to response"""
        response.headers["X-Response-Time"] = f"{duration:.3f}s"
        response.headers["X-Request-ID"] = str(context.get("request_id", "unknown"))
        response.headers["X-Service-Version"] = "1.0.0"
        response.headers["X-Enterprise-Security"] = "enabled" if self.enable_security else "disabled"
