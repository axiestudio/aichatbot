"""
Unified Monitoring Service
Consolidates all monitoring functionality into a single, comprehensive service
"""

import time
import psutil
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict, deque

from app.services.performance_monitoring_service import performance_service
from app.services.error_tracking_service import error_tracker
from app.services.circuit_breaker_service import circuit_manager
from app.services.advanced_cache_service import cache_service
from app.core.config import settings

logger = logging.getLogger(__name__)


class UnifiedMonitoringService:
    """
    Unified monitoring service that consolidates:
    - System metrics (CPU, memory, disk)
    - Application performance metrics
    - Error tracking and analytics
    - Circuit breaker health
    - Cache performance
    - Business metrics
    """
    
    def __init__(self):
        self.start_time = time.time()
        self.business_metrics = defaultdict(lambda: deque(maxlen=1000))
        self.alert_thresholds = {
            'cpu_usage': 80.0,
            'memory_usage': 85.0,
            'disk_usage': 90.0,
            'error_rate': 5.0,
            'response_time_p95': 2000.0,  # 2 seconds
            'cache_hit_rate': 80.0
        }
        
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get comprehensive system metrics"""
        
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            load_avg = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0, 0, 0]
            
            # Memory metrics
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            
            # Network metrics
            network = psutil.net_io_counters()
            
            # Process metrics
            process = psutil.Process()
            process_memory = process.memory_info()
            
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'uptime_seconds': time.time() - self.start_time,
                'cpu': {
                    'usage_percent': cpu_percent,
                    'count': cpu_count,
                    'load_average': list(load_avg)
                },
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'used': memory.used,
                    'percentage': memory.percent,
                    'swap_total': swap.total,
                    'swap_used': swap.used,
                    'swap_percentage': swap.percent
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percentage': (disk.used / disk.total) * 100
                },
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv
                },
                'process': {
                    'memory_rss': process_memory.rss,
                    'memory_vms': process_memory.vms,
                    'cpu_percent': process.cpu_percent(),
                    'num_threads': process.num_threads(),
                    'num_fds': process.num_fds() if hasattr(process, 'num_fds') else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
            return {'error': str(e), 'timestamp': datetime.utcnow().isoformat()}
    
    def get_application_metrics(self) -> Dict[str, Any]:
        """Get application-specific metrics"""
        
        try:
            # Performance metrics
            perf_analytics = performance_service.get_request_analytics(24)
            db_analytics = performance_service.get_database_analytics(24)
            
            # Error metrics
            error_analytics = error_tracker.get_error_analytics(24)
            
            # Circuit breaker health
            circuit_health = circuit_manager.get_health_summary()
            
            # Cache metrics
            cache_stats = cache_service.get_stats()
            
            # Business metrics
            business_summary = self._get_business_metrics_summary()
            
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'performance': {
                    'requests': perf_analytics,
                    'database': db_analytics,
                    'alerts': performance_service.get_performance_alerts()
                },
                'errors': error_analytics,
                'circuit_breakers': circuit_health,
                'cache': cache_stats,
                'business': business_summary
            }
            
        except Exception as e:
            logger.error(f"Failed to collect application metrics: {e}")
            return {'error': str(e), 'timestamp': datetime.utcnow().isoformat()}
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get overall system health status"""
        
        try:
            system_metrics = self.get_system_metrics()
            app_metrics = self.get_application_metrics()
            
            # Determine overall health
            health_issues = []
            health_status = "healthy"
            
            # Check system thresholds
            if 'cpu' in system_metrics:
                cpu_usage = system_metrics['cpu']['usage_percent']
                if cpu_usage > self.alert_thresholds['cpu_usage']:
                    health_issues.append(f"High CPU usage: {cpu_usage:.1f}%")
                    health_status = "warning" if health_status == "healthy" else "critical"
            
            if 'memory' in system_metrics:
                memory_usage = system_metrics['memory']['percentage']
                if memory_usage > self.alert_thresholds['memory_usage']:
                    health_issues.append(f"High memory usage: {memory_usage:.1f}%")
                    health_status = "warning" if health_status == "healthy" else "critical"
            
            if 'disk' in system_metrics:
                disk_usage = system_metrics['disk']['percentage']
                if disk_usage > self.alert_thresholds['disk_usage']:
                    health_issues.append(f"High disk usage: {disk_usage:.1f}%")
                    health_status = "critical"
            
            # Check application health
            if 'errors' in app_metrics and app_metrics['errors'].get('total_errors', 0) > 0:
                error_count = app_metrics['errors']['total_errors']
                if error_count > 10:  # More than 10 errors in 24h
                    health_issues.append(f"High error count: {error_count}")
                    health_status = "warning" if health_status == "healthy" else "critical"
            
            # Check circuit breakers
            if 'circuit_breakers' in app_metrics:
                cb_health = app_metrics['circuit_breakers']['health_status']
                if cb_health != "healthy":
                    health_issues.append(f"Circuit breaker issues: {cb_health}")
                    health_status = "warning" if health_status == "healthy" else "critical"
            
            # Check cache performance
            if 'cache' in app_metrics:
                cache_hit_rate = app_metrics['cache'].get('hit_rate', 0)
                if cache_hit_rate < self.alert_thresholds['cache_hit_rate']:
                    health_issues.append(f"Low cache hit rate: {cache_hit_rate:.1f}%")
                    health_status = "warning" if health_status == "healthy" else health_status
            
            # Service status
            services = {
                'api': 'up',
                'database': 'up',  # This would check actual DB connection
                'cache': 'up' if app_metrics.get('cache', {}).get('redis_connected') else 'degraded',
                'storage': 'up'  # This would check storage service
            }
            
            return {
                'overall': health_status,
                'timestamp': datetime.utcnow().isoformat(),
                'services': services,
                'issues': health_issues,
                'metrics_summary': {
                    'cpu_usage': system_metrics.get('cpu', {}).get('usage_percent', 0),
                    'memory_usage': system_metrics.get('memory', {}).get('percentage', 0),
                    'disk_usage': system_metrics.get('disk', {}).get('percentage', 0),
                    'error_count': app_metrics.get('errors', {}).get('total_errors', 0),
                    'cache_hit_rate': app_metrics.get('cache', {}).get('hit_rate', 0)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get health status: {e}")
            return {
                'overall': 'critical',
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e)
            }
    
    def track_business_metric(self, metric_name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Track business-specific metrics"""
        
        metric_data = {
            'value': value,
            'timestamp': datetime.utcnow(),
            'tags': tags or {}
        }
        
        self.business_metrics[metric_name].append(metric_data)
    
    def _get_business_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of business metrics"""
        
        summary = {}
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        
        for metric_name, metrics in self.business_metrics.items():
            recent_metrics = [m for m in metrics if m['timestamp'] > cutoff_time]
            
            if recent_metrics:
                values = [m['value'] for m in recent_metrics]
                summary[metric_name] = {
                    'count': len(recent_metrics),
                    'sum': sum(values),
                    'avg': sum(values) / len(values),
                    'min': min(values),
                    'max': max(values),
                    'latest': recent_metrics[-1]['value']
                }
        
        return summary
    
    def get_alerts(self) -> List[Dict[str, Any]]:
        """Get current system alerts"""
        
        alerts = []
        
        try:
            # System alerts
            system_metrics = self.get_system_metrics()
            
            if 'cpu' in system_metrics:
                cpu_usage = system_metrics['cpu']['usage_percent']
                if cpu_usage > self.alert_thresholds['cpu_usage']:
                    alerts.append({
                        'type': 'system',
                        'severity': 'warning' if cpu_usage < 90 else 'critical',
                        'message': f"High CPU usage: {cpu_usage:.1f}%",
                        'metric': 'cpu_usage',
                        'value': cpu_usage,
                        'threshold': self.alert_thresholds['cpu_usage'],
                        'timestamp': datetime.utcnow().isoformat()
                    })
            
            # Application alerts
            app_metrics = self.get_application_metrics()
            
            # Performance alerts
            if 'performance' in app_metrics:
                perf_alerts = app_metrics['performance'].get('alerts', [])
                for alert in perf_alerts:
                    alerts.append({
                        'type': 'performance',
                        'severity': alert.get('severity', 'warning'),
                        'message': alert.get('message', 'Performance issue detected'),
                        'timestamp': datetime.utcnow().isoformat()
                    })
            
            # Error alerts
            if 'errors' in app_metrics:
                error_count = app_metrics['errors'].get('total_errors', 0)
                if error_count > 5:  # More than 5 errors in 24h
                    alerts.append({
                        'type': 'errors',
                        'severity': 'warning' if error_count < 20 else 'critical',
                        'message': f"High error count: {error_count} errors in 24h",
                        'metric': 'error_count',
                        'value': error_count,
                        'timestamp': datetime.utcnow().isoformat()
                    })
            
        except Exception as e:
            logger.error(f"Failed to get alerts: {e}")
            alerts.append({
                'type': 'system',
                'severity': 'critical',
                'message': f"Monitoring system error: {str(e)}",
                'timestamp': datetime.utcnow().isoformat()
            })
        
        return alerts
    
    def get_comprehensive_dashboard_data(self) -> Dict[str, Any]:
        """Get all data needed for monitoring dashboard"""
        
        return {
            'system_metrics': self.get_system_metrics(),
            'application_metrics': self.get_application_metrics(),
            'health_status': self.get_health_status(),
            'alerts': self.get_alerts(),
            'timestamp': datetime.utcnow().isoformat()
        }


# Global unified monitoring service instance
unified_monitoring = UnifiedMonitoringService()
