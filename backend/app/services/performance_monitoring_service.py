"""
Performance Monitoring Service
Tracks API performance, database queries, and system metrics
"""

import time
import asyncio
import logging
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
from collections import defaultdict, deque
from functools import wraps
import statistics

from app.core.config import settings

logger = logging.getLogger(__name__)


class PerformanceMonitoringService:
    """Comprehensive performance monitoring and analytics"""
    
    def __init__(self):
        self.request_metrics = defaultdict(lambda: deque(maxlen=1000))
        self.database_metrics = defaultdict(lambda: deque(maxlen=1000))
        self.custom_metrics = defaultdict(lambda: deque(maxlen=1000))
        self.slow_query_threshold = 1.0  # seconds
        self.slow_request_threshold = 2.0  # seconds
        
    def track_request(
        self,
        endpoint: str,
        method: str,
        duration: float,
        status_code: int,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None
    ):
        """Track API request performance"""
        
        metric = {
            'timestamp': datetime.utcnow(),
            'endpoint': endpoint,
            'method': method,
            'duration': duration,
            'status_code': status_code,
            'user_id': user_id,
            'session_id': session_id,
            'is_slow': duration > self.slow_request_threshold
        }
        
        key = f"{method}:{endpoint}"
        self.request_metrics[key].append(metric)
        
        # Log slow requests
        if metric['is_slow']:
            logger.warning(
                f"Slow request detected: {method} {endpoint} took {duration:.2f}s",
                extra={
                    'duration': duration,
                    'endpoint': endpoint,
                    'method': method,
                    'status_code': status_code
                }
            )
    
    def track_database_query(
        self,
        query_type: str,
        table: str,
        duration: float,
        rows_affected: Optional[int] = None,
        query_hash: Optional[str] = None
    ):
        """Track database query performance"""
        
        metric = {
            'timestamp': datetime.utcnow(),
            'query_type': query_type,
            'table': table,
            'duration': duration,
            'rows_affected': rows_affected,
            'query_hash': query_hash,
            'is_slow': duration > self.slow_query_threshold
        }
        
        key = f"{query_type}:{table}"
        self.database_metrics[key].append(metric)
        
        # Log slow queries
        if metric['is_slow']:
            logger.warning(
                f"Slow query detected: {query_type} on {table} took {duration:.2f}s",
                extra={
                    'duration': duration,
                    'query_type': query_type,
                    'table': table,
                    'rows_affected': rows_affected
                }
            )
    
    def track_custom_metric(
        self,
        metric_name: str,
        value: float,
        tags: Optional[Dict[str, str]] = None
    ):
        """Track custom application metrics"""
        
        metric = {
            'timestamp': datetime.utcnow(),
            'value': value,
            'tags': tags or {}
        }
        
        self.custom_metrics[metric_name].append(metric)
    
    def get_request_analytics(self, time_range_hours: int = 24) -> Dict[str, Any]:
        """Get comprehensive request analytics"""
        cutoff_time = datetime.utcnow() - timedelta(hours=time_range_hours)
        
        analytics = {
            'time_range_hours': time_range_hours,
            'endpoints': {},
            'summary': {
                'total_requests': 0,
                'slow_requests': 0,
                'error_requests': 0,
                'avg_response_time': 0,
                'p95_response_time': 0,
                'p99_response_time': 0
            }
        }
        
        all_durations = []
        
        for endpoint, metrics in self.request_metrics.items():
            recent_metrics = [m for m in metrics if m['timestamp'] > cutoff_time]
            
            if not recent_metrics:
                continue
            
            durations = [m['duration'] for m in recent_metrics]
            slow_count = len([m for m in recent_metrics if m['is_slow']])
            error_count = len([m for m in recent_metrics if m['status_code'] >= 400])
            
            analytics['endpoints'][endpoint] = {
                'total_requests': len(recent_metrics),
                'slow_requests': slow_count,
                'error_requests': error_count,
                'avg_response_time': statistics.mean(durations),
                'min_response_time': min(durations),
                'max_response_time': max(durations),
                'p95_response_time': statistics.quantiles(durations, n=20)[18] if len(durations) > 1 else durations[0],
                'p99_response_time': statistics.quantiles(durations, n=100)[98] if len(durations) > 1 else durations[0]
            }
            
            all_durations.extend(durations)
            analytics['summary']['total_requests'] += len(recent_metrics)
            analytics['summary']['slow_requests'] += slow_count
            analytics['summary']['error_requests'] += error_count
        
        if all_durations:
            analytics['summary']['avg_response_time'] = statistics.mean(all_durations)
            analytics['summary']['p95_response_time'] = statistics.quantiles(all_durations, n=20)[18] if len(all_durations) > 1 else all_durations[0]
            analytics['summary']['p99_response_time'] = statistics.quantiles(all_durations, n=100)[98] if len(all_durations) > 1 else all_durations[0]
        
        return analytics
    
    def get_database_analytics(self, time_range_hours: int = 24) -> Dict[str, Any]:
        """Get database performance analytics"""
        cutoff_time = datetime.utcnow() - timedelta(hours=time_range_hours)
        
        analytics = {
            'time_range_hours': time_range_hours,
            'queries': {},
            'summary': {
                'total_queries': 0,
                'slow_queries': 0,
                'avg_query_time': 0,
                'p95_query_time': 0,
                'p99_query_time': 0
            }
        }
        
        all_durations = []
        
        for query_key, metrics in self.database_metrics.items():
            recent_metrics = [m for m in metrics if m['timestamp'] > cutoff_time]
            
            if not recent_metrics:
                continue
            
            durations = [m['duration'] for m in recent_metrics]
            slow_count = len([m for m in recent_metrics if m['is_slow']])
            
            analytics['queries'][query_key] = {
                'total_queries': len(recent_metrics),
                'slow_queries': slow_count,
                'avg_query_time': statistics.mean(durations),
                'min_query_time': min(durations),
                'max_query_time': max(durations),
                'p95_query_time': statistics.quantiles(durations, n=20)[18] if len(durations) > 1 else durations[0],
                'p99_query_time': statistics.quantiles(durations, n=100)[98] if len(durations) > 1 else durations[0]
            }
            
            all_durations.extend(durations)
            analytics['summary']['total_queries'] += len(recent_metrics)
            analytics['summary']['slow_queries'] += slow_count
        
        if all_durations:
            analytics['summary']['avg_query_time'] = statistics.mean(all_durations)
            analytics['summary']['p95_query_time'] = statistics.quantiles(all_durations, n=20)[18] if len(all_durations) > 1 else all_durations[0]
            analytics['summary']['p99_query_time'] = statistics.quantiles(all_durations, n=100)[98] if len(all_durations) > 1 else all_durations[0]
        
        return analytics
    
    def get_performance_alerts(self) -> List[Dict[str, Any]]:
        """Get current performance alerts"""
        alerts = []
        current_time = datetime.utcnow()
        
        # Check for recent slow requests
        recent_cutoff = current_time - timedelta(minutes=5)
        
        for endpoint, metrics in self.request_metrics.items():
            recent_slow = [
                m for m in metrics 
                if m['timestamp'] > recent_cutoff and m['is_slow']
            ]
            
            if len(recent_slow) > 5:  # More than 5 slow requests in 5 minutes
                alerts.append({
                    'type': 'high_slow_request_rate',
                    'endpoint': endpoint,
                    'slow_request_count': len(recent_slow),
                    'time_window': '5 minutes',
                    'severity': 'warning'
                })
        
        # Check for recent slow queries
        for query_key, metrics in self.database_metrics.items():
            recent_slow = [
                m for m in metrics 
                if m['timestamp'] > recent_cutoff and m['is_slow']
            ]
            
            if len(recent_slow) > 3:  # More than 3 slow queries in 5 minutes
                alerts.append({
                    'type': 'high_slow_query_rate',
                    'query': query_key,
                    'slow_query_count': len(recent_slow),
                    'time_window': '5 minutes',
                    'severity': 'warning'
                })
        
        return alerts


def performance_monitor(metric_name: str = None):
    """Decorator to monitor function performance"""
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                performance_service.track_custom_metric(
                    metric_name or f"function:{func.__name__}",
                    duration,
                    {'function': func.__name__, 'status': 'success'}
                )
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                performance_service.track_custom_metric(
                    metric_name or f"function:{func.__name__}",
                    duration,
                    {'function': func.__name__, 'status': 'error', 'error': str(e)}
                )
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                performance_service.track_custom_metric(
                    metric_name or f"function:{func.__name__}",
                    duration,
                    {'function': func.__name__, 'status': 'success'}
                )
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                performance_service.track_custom_metric(
                    metric_name or f"function:{func.__name__}",
                    duration,
                    {'function': func.__name__, 'status': 'error', 'error': str(e)}
                )
                raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator


# Global performance monitoring instance
performance_service = PerformanceMonitoringService()
