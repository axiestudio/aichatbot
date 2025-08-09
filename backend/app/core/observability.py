"""
Enterprise Observability Stack
Netflix/Google-style comprehensive observability with metrics, logs, and traces
"""

import logging
import time
import asyncio
import json
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from contextlib import asynccontextmanager
from collections import defaultdict, deque
import threading

# Try to import Prometheus client
try:
    from prometheus_client import Counter, Histogram, Gauge, Summary, CollectorRegistry, generate_latest
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class MetricPoint:
    """Single metric data point"""
    name: str
    value: float
    labels: Dict[str, str]
    timestamp: datetime
    metric_type: str  # counter, gauge, histogram, summary


@dataclass
class LogEntry:
    """Structured log entry"""
    timestamp: datetime
    level: str
    message: str
    service: str
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class MetricsCollector:
    """
    Enterprise-grade metrics collection similar to Netflix's Atlas
    """
    
    def __init__(self):
        self.metrics_store = defaultdict(deque)
        self.counters = {}
        self.gauges = {}
        self.histograms = {}
        self.summaries = {}
        self.custom_metrics = defaultdict(list)
        self.retention_hours = 24
        self._lock = threading.Lock()
        
        # Initialize Prometheus if available
        if PROMETHEUS_AVAILABLE:
            self.registry = CollectorRegistry()
            self._init_prometheus_metrics()
        
    def _init_prometheus_metrics(self):
        """Initialize Prometheus metrics"""
        self.prom_request_count = Counter(
            'http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status'],
            registry=self.registry
        )
        
        self.prom_request_duration = Histogram(
            'http_request_duration_seconds',
            'HTTP request duration',
            ['method', 'endpoint'],
            registry=self.registry
        )
        
        self.prom_active_connections = Gauge(
            'websocket_connections_active',
            'Active WebSocket connections',
            registry=self.registry
        )
        
        self.prom_chat_messages = Counter(
            'chat_messages_total',
            'Total chat messages',
            ['type', 'provider'],
            registry=self.registry
        )
        
        self.prom_ai_response_time = Histogram(
            'ai_response_duration_seconds',
            'AI response time',
            ['provider', 'model'],
            registry=self.registry
        )
        
        self.prom_error_rate = Counter(
            'errors_total',
            'Total errors',
            ['service', 'error_type'],
            registry=self.registry
        )
        
        self.prom_cache_hits = Counter(
            'cache_operations_total',
            'Cache operations',
            ['operation', 'result'],
            registry=self.registry
        )
        
        self.prom_database_connections = Gauge(
            'database_connections_active',
            'Active database connections',
            registry=self.registry
        )
        
        self.prom_memory_usage = Gauge(
            'memory_usage_bytes',
            'Memory usage in bytes',
            ['type'],
            registry=self.registry
        )
        
        self.prom_cpu_usage = Gauge(
            'cpu_usage_percent',
            'CPU usage percentage',
            registry=self.registry
        )
        
    def record_metric(self, name: str, value: float, labels: Dict[str, str] = None, metric_type: str = "gauge"):
        """Record a custom metric"""
        with self._lock:
            metric = MetricPoint(
                name=name,
                value=value,
                labels=labels or {},
                timestamp=datetime.utcnow(),
                metric_type=metric_type
            )
            
            # Store in time series
            self.metrics_store[name].append(metric)
            
            # Cleanup old metrics
            cutoff_time = datetime.utcnow() - timedelta(hours=self.retention_hours)
            while (self.metrics_store[name] and 
                   self.metrics_store[name][0].timestamp < cutoff_time):
                self.metrics_store[name].popleft()
                
    def record_http_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Record HTTP request metrics"""
        if PROMETHEUS_AVAILABLE:
            self.prom_request_count.labels(
                method=method,
                endpoint=endpoint,
                status=str(status_code)
            ).inc()
            
            self.prom_request_duration.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)
            
        # Custom storage
        self.record_metric("http_requests_total", 1, {
            "method": method,
            "endpoint": endpoint,
            "status": str(status_code)
        }, "counter")
        
        self.record_metric("http_request_duration", duration, {
            "method": method,
            "endpoint": endpoint
        }, "histogram")
        
    def record_ai_response(self, provider: str, model: str, duration: float, tokens: int):
        """Record AI response metrics"""
        if PROMETHEUS_AVAILABLE:
            self.prom_ai_response_time.labels(
                provider=provider,
                model=model
            ).observe(duration)
            
            self.prom_chat_messages.labels(
                type="ai_response",
                provider=provider
            ).inc()
            
        self.record_metric("ai_response_duration", duration, {
            "provider": provider,
            "model": model
        }, "histogram")
        
        self.record_metric("ai_tokens_used", tokens, {
            "provider": provider,
            "model": model
        }, "counter")
        
    def record_error(self, service: str, error_type: str, error_message: str):
        """Record error metrics"""
        if PROMETHEUS_AVAILABLE:
            self.prom_error_rate.labels(
                service=service,
                error_type=error_type
            ).inc()
            
        self.record_metric("errors_total", 1, {
            "service": service,
            "error_type": error_type
        }, "counter")
        
    def record_cache_operation(self, operation: str, result: str):
        """Record cache operation metrics"""
        if PROMETHEUS_AVAILABLE:
            self.prom_cache_hits.labels(
                operation=operation,
                result=result
            ).inc()
            
        self.record_metric("cache_operations", 1, {
            "operation": operation,
            "result": result
        }, "counter")
        
    def update_system_metrics(self, cpu_percent: float, memory_bytes: int, db_connections: int):
        """Update system metrics"""
        if PROMETHEUS_AVAILABLE:
            self.prom_cpu_usage.set(cpu_percent)
            self.prom_memory_usage.labels(type="used").set(memory_bytes)
            self.prom_database_connections.set(db_connections)
            
        self.record_metric("cpu_usage_percent", cpu_percent)
        self.record_metric("memory_usage_bytes", memory_bytes)
        self.record_metric("database_connections", db_connections)
        
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get comprehensive metrics summary"""
        with self._lock:
            summary = {
                "timestamp": datetime.utcnow().isoformat(),
                "metrics_count": sum(len(deque_) for deque_ in self.metrics_store.values()),
                "metric_types": list(self.metrics_store.keys()),
                "retention_hours": self.retention_hours,
                "prometheus_enabled": PROMETHEUS_AVAILABLE
            }
            
            # Calculate aggregations for key metrics
            for metric_name, metric_deque in self.metrics_store.items():
                if metric_deque:
                    values = [m.value for m in metric_deque]
                    summary[f"{metric_name}_stats"] = {
                        "count": len(values),
                        "sum": sum(values),
                        "avg": sum(values) / len(values),
                        "min": min(values),
                        "max": max(values),
                        "latest": values[-1]
                    }
                    
            return summary
            
    def export_prometheus_metrics(self) -> str:
        """Export metrics in Prometheus format"""
        if PROMETHEUS_AVAILABLE:
            return generate_latest(self.registry).decode('utf-8')
        return "# Prometheus not available\n"


class StructuredLogger:
    """
    Enterprise structured logging similar to Google's Cloud Logging
    """
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.log_buffer = deque(maxlen=10000)  # Keep last 10k logs in memory
        self.logger = logging.getLogger(service_name)
        
    def log(self, level: str, message: str, **kwargs):
        """Log structured message"""
        entry = LogEntry(
            timestamp=datetime.utcnow(),
            level=level.upper(),
            message=message,
            service=self.service_name,
            trace_id=kwargs.get('trace_id'),
            span_id=kwargs.get('span_id'),
            user_id=kwargs.get('user_id'),
            session_id=kwargs.get('session_id'),
            metadata=kwargs.get('metadata', {})
        )
        
        # Add to buffer
        self.log_buffer.append(entry)
        
        # Log to standard logger with structured format
        log_dict = asdict(entry)
        log_dict['timestamp'] = entry.timestamp.isoformat()
        
        getattr(self.logger, level.lower())(json.dumps(log_dict))
        
    def info(self, message: str, **kwargs):
        self.log("INFO", message, **kwargs)
        
    def error(self, message: str, **kwargs):
        self.log("ERROR", message, **kwargs)
        
    def warning(self, message: str, **kwargs):
        self.log("WARNING", message, **kwargs)
        
    def debug(self, message: str, **kwargs):
        self.log("DEBUG", message, **kwargs)
        
    def get_recent_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent logs"""
        logs = list(self.log_buffer)[-limit:]
        return [asdict(log) for log in logs]


class ObservabilityStack:
    """
    Complete observability stack combining metrics, logs, and traces
    Similar to Netflix's observability platform
    """
    
    def __init__(self, service_name: str = "ai-chatbot"):
        self.service_name = service_name
        self.metrics = MetricsCollector()
        self.logger = StructuredLogger(service_name)
        self.alerts = []
        self.dashboards = {}
        
    async def initialize(self):
        """Initialize observability stack"""
        self.logger.info("Initializing enterprise observability stack")
        
        # Start background tasks
        asyncio.create_task(self._metrics_collection_loop())
        asyncio.create_task(self._alert_evaluation_loop())
        
        self.logger.info("Observability stack initialized", metadata={
            "prometheus_enabled": PROMETHEUS_AVAILABLE,
            "service_name": self.service_name
        })
        
    async def _metrics_collection_loop(self):
        """Background metrics collection"""
        while True:
            try:
                # Collect system metrics
                import psutil
                cpu_percent = psutil.cpu_percent()
                memory = psutil.virtual_memory()
                
                self.metrics.update_system_metrics(
                    cpu_percent=cpu_percent,
                    memory_bytes=memory.used,
                    db_connections=0  # Would get from DB pool
                )
                
                await asyncio.sleep(30)  # Collect every 30 seconds
                
            except Exception as e:
                self.logger.error("Metrics collection failed", metadata={"error": str(e)})
                await asyncio.sleep(60)
                
    async def _alert_evaluation_loop(self):
        """Background alert evaluation"""
        while True:
            try:
                # Evaluate alert conditions
                await self._evaluate_alerts()
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error("Alert evaluation failed", metadata={"error": str(e)})
                await asyncio.sleep(120)
                
    async def _evaluate_alerts(self):
        """Evaluate alert conditions"""
        # This would implement alert rules similar to Prometheus AlertManager
        pass
        
    @asynccontextmanager
    async def trace_operation(self, operation_name: str, **attributes):
        """Context manager for tracing operations"""
        start_time = time.time()
        
        self.logger.info(f"Starting operation: {operation_name}", metadata=attributes)
        
        try:
            yield
            duration = time.time() - start_time
            
            self.metrics.record_metric(
                f"operation_duration_{operation_name}",
                duration,
                attributes,
                "histogram"
            )
            
            self.logger.info(f"Completed operation: {operation_name}", metadata={
                **attributes,
                "duration_seconds": duration
            })
            
        except Exception as e:
            duration = time.time() - start_time
            
            self.metrics.record_error(
                service=self.service_name,
                error_type=type(e).__name__,
                error_message=str(e)
            )
            
            self.logger.error(f"Failed operation: {operation_name}", metadata={
                **attributes,
                "duration_seconds": duration,
                "error": str(e),
                "error_type": type(e).__name__
            })
            
            raise
            
    def get_health_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive health dashboard"""
        return {
            "service": self.service_name,
            "timestamp": datetime.utcnow().isoformat(),
            "metrics_summary": self.metrics.get_metrics_summary(),
            "recent_logs": self.logger.get_recent_logs(50),
            "active_alerts": len(self.alerts),
            "prometheus_endpoint": "/metrics" if PROMETHEUS_AVAILABLE else None
        }


# Global observability instance
observability = ObservabilityStack()
