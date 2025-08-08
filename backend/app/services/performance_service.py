"""
Enterprise Performance Monitoring Service
Advanced performance tracking, optimization, and alerting
"""

import time
import asyncio
import logging
import psutil
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass
import functools

from .cache_service import cache_service
from ..core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetric:
    """Performance metric data structure"""
    name: str
    value: float
    timestamp: datetime
    tags: Dict[str, str] = None
    unit: str = "ms"


class PerformanceService:
    """Enterprise-grade performance monitoring service"""
    
    def __init__(self):
        self.metrics = defaultdict(deque)
        self.metric_retention = 1000  # Keep last 1000 metrics per type
        
        # Performance thresholds
        self.thresholds = {
            "api_response_time": {"warning": 1000, "critical": 3000},  # ms
            "database_query_time": {"warning": 500, "critical": 2000},  # ms
            "memory_usage": {"warning": 80, "critical": 90},  # percentage
            "cpu_usage": {"warning": 80, "critical": 95},  # percentage
            "disk_usage": {"warning": 85, "critical": 95},  # percentage
            "websocket_connections": {"warning": 1000, "critical": 2000},  # count
            "cache_hit_rate": {"warning": 70, "critical": 50},  # percentage (lower is worse)
        }
        
        # Performance counters
        self.counters = defaultdict(int)
        
        # Request tracking
        self.active_requests = {}
        self.request_history = deque(maxlen=10000)
        
        # Background monitoring task
        self.monitoring_task = None
        
    async def start_monitoring(self):
        """Start background performance monitoring"""
        if self.monitoring_task is None:
            self.monitoring_task = asyncio.create_task(self._background_monitoring())
            logger.info("🔍 Performance monitoring started")
    
    async def stop_monitoring(self):
        """Stop background performance monitoring"""
        if self.monitoring_task:
            self.monitoring_task.cancel()
            self.monitoring_task = None
            logger.info("⏹️ Performance monitoring stopped")
    
    def track_request_start(self, request_id: str, endpoint: str, method: str) -> str:
        """Track the start of a request"""
        self.active_requests[request_id] = {
            "endpoint": endpoint,
            "method": method,
            "start_time": time.time(),
            "memory_start": psutil.Process().memory_info().rss
        }
        return request_id
    
    def track_request_end(self, request_id: str, status_code: int = 200, error: str = None):
        """Track the end of a request"""
        if request_id not in self.active_requests:
            return
        
        request_data = self.active_requests.pop(request_id)
        end_time = time.time()
        duration = (end_time - request_data["start_time"]) * 1000  # Convert to ms
        
        # Record performance metric
        metric = PerformanceMetric(
            name="api_response_time",
            value=duration,
            timestamp=datetime.utcnow(),
            tags={
                "endpoint": request_data["endpoint"],
                "method": request_data["method"],
                "status_code": str(status_code),
                "error": error or "none"
            }
        )
        
        self._record_metric(metric)
        
        # Add to request history
        self.request_history.append({
            "request_id": request_id,
            "endpoint": request_data["endpoint"],
            "method": request_data["method"],
            "duration_ms": duration,
            "status_code": status_code,
            "error": error,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Update counters
        self.counters["total_requests"] += 1
        if error:
            self.counters["error_requests"] += 1
        
        # Check for performance alerts
        self._check_performance_alert("api_response_time", duration, request_data["endpoint"])
    
    def track_database_query(self, query_type: str, duration_ms: float, table: str = None):
        """Track database query performance"""
        metric = PerformanceMetric(
            name="database_query_time",
            value=duration_ms,
            timestamp=datetime.utcnow(),
            tags={
                "query_type": query_type,
                "table": table or "unknown"
            }
        )
        
        self._record_metric(metric)
        self.counters["database_queries"] += 1
        
        # Check for performance alerts
        self._check_performance_alert("database_query_time", duration_ms, f"{query_type}:{table}")
    
    def track_cache_operation(self, operation: str, hit: bool, duration_ms: float = None):
        """Track cache operation performance"""
        self.counters[f"cache_{operation}"] += 1
        self.counters["cache_hits" if hit else "cache_misses"] += 1
        
        if duration_ms:
            metric = PerformanceMetric(
                name="cache_operation_time",
                value=duration_ms,
                timestamp=datetime.utcnow(),
                tags={"operation": operation, "hit": str(hit)}
            )
            self._record_metric(metric)
    
    def track_websocket_event(self, event_type: str, connection_count: int):
        """Track WebSocket events"""
        metric = PerformanceMetric(
            name="websocket_connections",
            value=connection_count,
            timestamp=datetime.utcnow(),
            tags={"event_type": event_type},
            unit="count"
        )
        
        self._record_metric(metric)
        self.counters[f"websocket_{event_type}"] += 1
        
        # Check for performance alerts
        self._check_performance_alert("websocket_connections", connection_count, event_type)
    
    async def get_performance_summary(self, time_window_minutes: int = 60) -> Dict[str, Any]:
        """Get performance summary for the specified time window"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=time_window_minutes)
        
        summary = {
            "time_window_minutes": time_window_minutes,
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": {},
            "counters": dict(self.counters),
            "alerts": [],
            "system_resources": await self._get_system_resources(),
            "top_slow_endpoints": self._get_slow_endpoints(cutoff_time),
            "error_rate": self._calculate_error_rate()
        }
        
        # Calculate metrics for each type
        for metric_name, metric_deque in self.metrics.items():
            recent_metrics = [m for m in metric_deque if m.timestamp >= cutoff_time]
            
            if recent_metrics:
                values = [m.value for m in recent_metrics]
                summary["metrics"][metric_name] = {
                    "count": len(values),
                    "avg": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values),
                    "p95": self._percentile(values, 95),
                    "p99": self._percentile(values, 99),
                    "unit": recent_metrics[0].unit
                }
        
        # Calculate cache hit rate
        cache_hits = self.counters.get("cache_hits", 0)
        cache_misses = self.counters.get("cache_misses", 0)
        total_cache_ops = cache_hits + cache_misses
        
        if total_cache_ops > 0:
            hit_rate = (cache_hits / total_cache_ops) * 100
            summary["cache_hit_rate"] = hit_rate
            self._check_performance_alert("cache_hit_rate", hit_rate, "cache")
        
        return summary
    
    async def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get real-time performance metrics"""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "active_requests": len(self.active_requests),
            "system_resources": await self._get_system_resources(),
            "counters": dict(self.counters),
            "recent_requests": list(self.request_history)[-10:],  # Last 10 requests
            "cache_stats": cache_service.get_stats() if cache_service else {}
        }
    
    def _record_metric(self, metric: PerformanceMetric):
        """Record a performance metric"""
        metric_deque = self.metrics[metric.name]
        metric_deque.append(metric)
        
        # Maintain retention limit
        while len(metric_deque) > self.metric_retention:
            metric_deque.popleft()
    
    def _check_performance_alert(self, metric_name: str, value: float, context: str):
        """Check if metric value triggers an alert"""
        if metric_name not in self.thresholds:
            return
        
        thresholds = self.thresholds[metric_name]
        
        if value >= thresholds["critical"]:
            logger.error(f"🚨 CRITICAL: {metric_name} = {value} (threshold: {thresholds['critical']}) - {context}")
        elif value >= thresholds["warning"]:
            logger.warning(f"⚠️ WARNING: {metric_name} = {value} (threshold: {thresholds['warning']}) - {context}")
    
    async def _get_system_resources(self) -> Dict[str, Any]:
        """Get current system resource usage"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            
            # Disk usage
            disk = psutil.disk_usage('/')
            
            # Process-specific metrics
            process = psutil.Process()
            process_memory = process.memory_info()
            
            resources = {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_gb": memory.available / (1024**3),
                "disk_percent": (disk.used / disk.total) * 100,
                "disk_free_gb": disk.free / (1024**3),
                "process_memory_mb": process_memory.rss / (1024**2),
                "process_cpu_percent": process.cpu_percent()
            }
            
            # Check for resource alerts
            self._check_performance_alert("cpu_usage", cpu_percent, "system")
            self._check_performance_alert("memory_usage", memory.percent, "system")
            self._check_performance_alert("disk_usage", (disk.used / disk.total) * 100, "system")
            
            return resources
            
        except Exception as e:
            logger.error(f"Error getting system resources: {e}")
            return {}
    
    def _get_slow_endpoints(self, cutoff_time: datetime, limit: int = 10) -> List[Dict[str, Any]]:
        """Get slowest endpoints in the time window"""
        endpoint_metrics = defaultdict(list)
        
        # Collect API response time metrics
        for metric in self.metrics.get("api_response_time", []):
            if metric.timestamp >= cutoff_time and metric.tags:
                endpoint = metric.tags.get("endpoint", "unknown")
                endpoint_metrics[endpoint].append(metric.value)
        
        # Calculate average response times
        slow_endpoints = []
        for endpoint, times in endpoint_metrics.items():
            if times:
                avg_time = sum(times) / len(times)
                slow_endpoints.append({
                    "endpoint": endpoint,
                    "avg_response_time_ms": avg_time,
                    "request_count": len(times),
                    "max_response_time_ms": max(times),
                    "p95_response_time_ms": self._percentile(times, 95)
                })
        
        # Sort by average response time
        slow_endpoints.sort(key=lambda x: x["avg_response_time_ms"], reverse=True)
        return slow_endpoints[:limit]
    
    def _calculate_error_rate(self) -> float:
        """Calculate current error rate"""
        total_requests = self.counters.get("total_requests", 0)
        error_requests = self.counters.get("error_requests", 0)
        
        if total_requests == 0:
            return 0.0
        
        return (error_requests / total_requests) * 100
    
    def _percentile(self, values: List[float], percentile: int) -> float:
        """Calculate percentile of values"""
        if not values:
            return 0.0
        
        sorted_values = sorted(values)
        index = int((percentile / 100) * len(sorted_values))
        index = min(index, len(sorted_values) - 1)
        return sorted_values[index]
    
    async def _background_monitoring(self):
        """Background task for continuous monitoring"""
        while True:
            try:
                # Record system metrics
                resources = await self._get_system_resources()
                
                for metric_name, value in resources.items():
                    if metric_name.endswith("_percent"):
                        metric = PerformanceMetric(
                            name=metric_name,
                            value=value,
                            timestamp=datetime.utcnow(),
                            unit="percent"
                        )
                        self._record_metric(metric)
                
                # Clean up old metrics
                self._cleanup_old_metrics()
                
                # Wait before next monitoring cycle
                await asyncio.sleep(30)  # Monitor every 30 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Background monitoring error: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    def _cleanup_old_metrics(self):
        """Clean up old metrics to prevent memory leaks"""
        cutoff_time = datetime.utcnow() - timedelta(hours=24)  # Keep 24 hours of data
        
        for metric_name, metric_deque in self.metrics.items():
            # Remove old metrics
            while metric_deque and metric_deque[0].timestamp < cutoff_time:
                metric_deque.popleft()


# Performance monitoring decorator
def monitor_performance(metric_name: str = None):
    """Decorator to monitor function performance"""
    def decorator(func: Callable):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            error = None
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                error = str(e)
                raise
            finally:
                duration = (time.time() - start_time) * 1000
                name = metric_name or f"{func.__module__}.{func.__name__}"
                
                metric = PerformanceMetric(
                    name=name,
                    value=duration,
                    timestamp=datetime.utcnow(),
                    tags={"function": func.__name__, "error": error or "none"}
                )
                
                get_performance_service()._record_metric(metric)
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            error = None
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                error = str(e)
                raise
            finally:
                duration = (time.time() - start_time) * 1000
                name = metric_name or f"{func.__module__}.{func.__name__}"
                
                metric = PerformanceMetric(
                    name=name,
                    value=duration,
                    timestamp=datetime.utcnow(),
                    tags={"function": func.__name__, "error": error or "none"}
                )
                
                get_performance_service()._record_metric(metric)
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator


# Global performance service instance - lazy initialization
_performance_service_instance = None

def get_performance_service() -> PerformanceService:
    """Get performance service instance with lazy initialization"""
    global _performance_service_instance
    if _performance_service_instance is None:
        _performance_service_instance = PerformanceService()
    return _performance_service_instance
