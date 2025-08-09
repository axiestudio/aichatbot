"""
Distributed Tracing Configuration
OpenTelemetry setup for comprehensive request tracing
"""

import logging
from typing import Dict, Any, Optional
from contextlib import contextmanager

# Try to import OpenTelemetry components with fallback
try:
    from opentelemetry import trace, baggage
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.instrumentation.requests import RequestsInstrumentor
    from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.semconv.resource import ResourceAttributes
    OPENTELEMETRY_AVAILABLE = True
except ImportError:
    OPENTELEMETRY_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("OpenTelemetry not available - using fallback tracing")

from app.core.config import settings

logger = logging.getLogger(__name__)


class TracingService:
    """Distributed tracing service with OpenTelemetry"""
    
    def __init__(self):
        self.tracer_provider: Optional[TracerProvider] = None
        self.tracer = None
        self.is_initialized = False
    
    def initialize(self, app=None):
        """Initialize distributed tracing with OpenTelemetry or fallback"""
        if self.is_initialized:
            return

        if not OPENTELEMETRY_AVAILABLE:
            self._initialize_fallback()
            return

        try:
            # Create resource with service information
            resource = Resource.create({
                ResourceAttributes.SERVICE_NAME: "chatbot-backend",
                ResourceAttributes.SERVICE_VERSION: "1.0.0",
                ResourceAttributes.SERVICE_NAMESPACE: "chatbot",
                ResourceAttributes.DEPLOYMENT_ENVIRONMENT: settings.ENVIRONMENT,
            })
            
            # Create tracer provider
            self.tracer_provider = TracerProvider(resource=resource)
            trace.set_tracer_provider(self.tracer_provider)
            
            # Configure Jaeger exporter if enabled
            if settings.JAEGER_ENDPOINT:
                jaeger_exporter = JaegerExporter(
                    agent_host_name=settings.JAEGER_HOST or "localhost",
                    agent_port=settings.JAEGER_PORT or 6831,
                    collector_endpoint=settings.JAEGER_ENDPOINT,
                )
                
                span_processor = BatchSpanProcessor(jaeger_exporter)
                self.tracer_provider.add_span_processor(span_processor)
                
                logger.info(f"Jaeger tracing enabled: {settings.JAEGER_ENDPOINT}")
            
            # Get tracer
            self.tracer = trace.get_tracer(__name__)
            
            # Auto-instrument FastAPI if app provided
            if app:
                FastAPIInstrumentor.instrument_app(
                    app,
                    tracer_provider=self.tracer_provider,
                    excluded_urls="/health,/metrics"
                )
            
            # Auto-instrument requests
            RequestsInstrumentor().instrument(tracer_provider=self.tracer_provider)
            
            # Auto-instrument SQLAlchemy
            SQLAlchemyInstrumentor().instrument(tracer_provider=self.tracer_provider)
            
            self.is_initialized = True
            logger.info("Distributed tracing initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenTelemetry tracing: {e}")
            self._initialize_fallback()

    def _initialize_fallback(self):
        """Initialize fallback tracing when OpenTelemetry is not available"""
        self.tracer = FallbackTracer()
        self.is_initialized = True
        logger.info("✅ Fallback tracing initialized")
    
    def start_span(
        self,
        name: str,
        attributes: Optional[Dict[str, Any]] = None,
        parent_context=None
    ):
        """Start a new span with optional attributes"""
        
        if not self.is_initialized or not self.tracer:
            return trace.NoOpSpan()
        
        span = self.tracer.start_span(
            name,
            context=parent_context,
            attributes=attributes or {}
        )
        
        return span
    
    def add_span_attributes(self, span, attributes: Dict[str, Any]):
        """Add attributes to an existing span"""
        
        if span and hasattr(span, 'set_attributes'):
            span.set_attributes(attributes)
    
    def add_span_event(self, span, name: str, attributes: Optional[Dict[str, Any]] = None):
        """Add an event to an existing span"""
        
        if span and hasattr(span, 'add_event'):
            span.add_event(name, attributes or {})
    
    def set_span_status(self, span, status_code, description: Optional[str] = None):
        """Set span status"""
        
        if span and hasattr(span, 'set_status'):
            span.set_status(status_code, description)
    
    def get_current_span(self):
        """Get the current active span"""
        
        return trace.get_current_span()
    
    def get_trace_id(self) -> Optional[str]:
        """Get current trace ID"""
        
        span = self.get_current_span()
        if span and span.get_span_context().is_valid:
            return format(span.get_span_context().trace_id, '032x')
        return None
    
    def get_span_id(self) -> Optional[str]:
        """Get current span ID"""
        
        span = self.get_current_span()
        if span and span.get_span_context().is_valid:
            return format(span.get_span_context().span_id, '016x')
        return None
    
    def set_baggage(self, key: str, value: str):
        """Set baggage for cross-service context propagation"""
        
        baggage.set_baggage(key, value)
    
    def get_baggage(self, key: str) -> Optional[str]:
        """Get baggage value"""
        
        return baggage.get_baggage(key)
    
    def create_child_span(self, name: str, parent_span=None):
        """Create a child span"""
        
        if not self.is_initialized or not self.tracer:
            return trace.NoOpSpan()
        
        if parent_span:
            context = trace.set_span_in_context(parent_span)
            return self.tracer.start_span(name, context=context)
        else:
            return self.tracer.start_span(name)


class FallbackTracer:
    """Fallback tracer when OpenTelemetry is not available"""

    def start_span(self, name: str, **kwargs):
        return FallbackSpan(name, **kwargs)


class FallbackSpan:
    """Fallback span implementation"""

    def __init__(self, name: str, **kwargs):
        self.name = name
        self.attributes = kwargs

    def set_attribute(self, key: str, value):
        self.attributes[key] = value

    def add_event(self, name: str, attributes=None):
        pass

    def set_status(self, status):
        pass

    def end(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end()


# Global tracing service instance
tracing_service = TracingService()


def trace_function(operation_name: str = None, attributes: Dict[str, Any] = None):
    """Decorator to trace function execution"""
    
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not tracing_service.is_initialized:
                return func(*args, **kwargs)
            
            span_name = operation_name or f"{func.__module__}.{func.__name__}"
            span_attributes = {
                "function.name": func.__name__,
                "function.module": func.__module__,
                **(attributes or {})
            }
            
            with tracing_service.start_span(span_name, span_attributes) as span:
                try:
                    # Add function arguments as attributes (be careful with sensitive data)
                    if args:
                        span_attributes["function.args_count"] = len(args)
                    if kwargs:
                        span_attributes["function.kwargs_count"] = len(kwargs)
                    
                    tracing_service.add_span_attributes(span, span_attributes)
                    
                    result = func(*args, **kwargs)
                    
                    # Mark span as successful
                    tracing_service.set_span_status(span, trace.Status(trace.StatusCode.OK))
                    
                    return result
                    
                except Exception as e:
                    # Mark span as error
                    tracing_service.set_span_status(
                        span,
                        trace.Status(trace.StatusCode.ERROR, str(e))
                    )
                    tracing_service.add_span_event(
                        span,
                        "exception",
                        {
                            "exception.type": type(e).__name__,
                            "exception.message": str(e)
                        }
                    )
                    raise
        
        return wrapper
    return decorator


def trace_async_function(operation_name: str = None, attributes: Dict[str, Any] = None):
    """Decorator to trace async function execution"""
    
    def decorator(func):
        async def wrapper(*args, **kwargs):
            if not tracing_service.is_initialized:
                return await func(*args, **kwargs)
            
            span_name = operation_name or f"{func.__module__}.{func.__name__}"
            span_attributes = {
                "function.name": func.__name__,
                "function.module": func.__module__,
                "function.async": True,
                **(attributes or {})
            }
            
            with tracing_service.start_span(span_name, span_attributes) as span:
                try:
                    # Add function arguments as attributes
                    if args:
                        span_attributes["function.args_count"] = len(args)
                    if kwargs:
                        span_attributes["function.kwargs_count"] = len(kwargs)
                    
                    tracing_service.add_span_attributes(span, span_attributes)
                    
                    result = await func(*args, **kwargs)
                    
                    # Mark span as successful
                    tracing_service.set_span_status(span, trace.Status(trace.StatusCode.OK))
                    
                    return result
                    
                except Exception as e:
                    # Mark span as error
                    tracing_service.set_span_status(
                        span,
                        trace.Status(trace.StatusCode.ERROR, str(e))
                    )
                    tracing_service.add_span_event(
                        span,
                        "exception",
                        {
                            "exception.type": type(e).__name__,
                            "exception.message": str(e)
                        }
                    )
                    raise
        
        return wrapper
    return decorator


# Context manager for manual span creation
class TracingContext:
    """Context manager for manual span creation"""
    
    def __init__(self, name: str, attributes: Optional[Dict[str, Any]] = None):
        self.name = name
        self.attributes = attributes or {}
        self.span = None
    
    def __enter__(self):
        self.span = tracing_service.start_span(self.name, self.attributes)
        return self.span
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.span:
            if exc_type:
                tracing_service.set_span_status(
                    self.span,
                    trace.Status(trace.StatusCode.ERROR, str(exc_val))
                )
                tracing_service.add_span_event(
                    self.span,
                    "exception",
                    {
                        "exception.type": exc_type.__name__,
                        "exception.message": str(exc_val)
                    }
                )
            else:
                tracing_service.set_span_status(
                    self.span,
                    trace.Status(trace.StatusCode.OK)
                )
            
            self.span.end()


def get_trace_context() -> Dict[str, str]:
    """Get current trace context for logging"""
    
    return {
        "trace_id": tracing_service.get_trace_id() or "",
        "span_id": tracing_service.get_span_id() or ""
    }
