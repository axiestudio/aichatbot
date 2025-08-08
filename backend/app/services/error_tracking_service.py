"""
Advanced Error Tracking and Monitoring Service
Provides comprehensive error tracking, alerting, and analytics
"""

import logging
import json
import time
import traceback
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from collections import defaultdict, deque
import asyncio
import hashlib

from app.core.config import settings

logger = logging.getLogger(__name__)

# Lazy import to avoid circular dependencies
def get_cache_service():
    try:
        from .cache_service import cache_service
        return cache_service
    except ImportError:
        logger.warning("Cache service not available")
        return None


class ErrorTrackingService:
    """Advanced error tracking with analytics and alerting"""
    
    def __init__(self):
        self.error_cache = defaultdict(lambda: {
            'count': 0,
            'first_seen': None,
            'last_seen': None,
            'samples': deque(maxlen=10)
        })
        self.error_rates = defaultdict(lambda: deque(maxlen=60))  # 1 minute window
        self.alert_thresholds = {
            'error_rate_per_minute': 10,
            'critical_error_rate': 5,
            'unique_errors_threshold': 20
        }

        # Recovery mechanisms
        self.recovery_strategies = {
            'database_error': self._recover_database_connection,
            'redis_error': self._recover_redis_connection,
            'api_error': self._recover_api_connection,
            'websocket_error': self._recover_websocket_connection,
            'memory_error': self._recover_memory_pressure,
            'timeout_error': self._recover_timeout_issues
        }

        # Circuit breaker states
        self.circuit_breakers = defaultdict(lambda: {
            'state': 'closed',  # closed, open, half_open
            'failure_count': 0,
            'last_failure_time': None,
            'success_count': 0
        })
        
    def track_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        severity: str = "error",
        user_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> str:
        """Track an error with full context and analytics"""
        
        error_id = self._generate_error_id(error, context)
        timestamp = datetime.utcnow()
        
        # Create error record
        error_record = {
            'error_id': error_id,
            'timestamp': timestamp.isoformat(),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'traceback': traceback.format_exc(),
            'severity': severity,
            'context': context or {},
            'user_id': user_id,
            'session_id': session_id,
            'environment': settings.ENVIRONMENT
        }
        
        # Update error cache
        error_info = self.error_cache[error_id]
        error_info['count'] += 1
        if error_info['first_seen'] is None:
            error_info['first_seen'] = timestamp
        error_info['last_seen'] = timestamp
        error_info['samples'].append(error_record)
        
        # Update error rates
        current_minute = int(timestamp.timestamp() // 60)
        self.error_rates[current_minute].append({
            'error_id': error_id,
            'severity': severity,
            'timestamp': timestamp
        })
        
        # Check for alerts
        self._check_alert_conditions(error_id, severity)
        
        # Log the error
        self._log_error(error_record)
        
        return error_id
    
    def _generate_error_id(self, error: Exception, context: Optional[Dict] = None) -> str:
        """Generate unique error ID based on error type, message, and context"""
        error_signature = f"{type(error).__name__}:{str(error)}"
        if context:
            # Include relevant context in signature
            context_str = json.dumps(context, sort_keys=True, default=str)
            error_signature += f":{context_str}"
        
        return hashlib.md5(error_signature.encode()).hexdigest()[:12]
    
    def _check_alert_conditions(self, error_id: str, severity: str):
        """Check if error conditions warrant alerts"""
        current_time = datetime.utcnow()
        current_minute = int(current_time.timestamp() // 60)
        
        # Check error rate in last minute
        recent_errors = []
        for minute in range(current_minute - 1, current_minute + 1):
            recent_errors.extend(self.error_rates.get(minute, []))
        
        error_rate = len(recent_errors)
        critical_errors = len([e for e in recent_errors if e['severity'] == 'critical'])
        
        # Alert conditions
        if error_rate > self.alert_thresholds['error_rate_per_minute']:
            self._send_alert('high_error_rate', {
                'error_rate': error_rate,
                'threshold': self.alert_thresholds['error_rate_per_minute'],
                'time_window': '1 minute'
            })
        
        if critical_errors > self.alert_thresholds['critical_error_rate']:
            self._send_alert('critical_errors', {
                'critical_error_count': critical_errors,
                'threshold': self.alert_thresholds['critical_error_rate']
            })
        
        if len(self.error_cache) > self.alert_thresholds['unique_errors_threshold']:
            self._send_alert('too_many_unique_errors', {
                'unique_error_count': len(self.error_cache),
                'threshold': self.alert_thresholds['unique_errors_threshold']
            })
    
    def _send_alert(self, alert_type: str, data: Dict[str, Any]):
        """Send alert (implement webhook/email/slack integration)"""
        alert = {
            'alert_type': alert_type,
            'timestamp': datetime.utcnow().isoformat(),
            'environment': settings.ENVIRONMENT,
            'data': data
        }
        
        logger.critical(f"ALERT: {alert_type} - {json.dumps(alert)}")
        
        # TODO: Implement actual alerting (Slack, email, PagerDuty, etc.)
        # await self._send_to_webhook(alert)
        # await self._send_email_alert(alert)
    
    def _log_error(self, error_record: Dict[str, Any]):
        """Log error with structured format"""
        logger.error(
            f"Error tracked: {error_record['error_type']} - {error_record['error_message']}",
            extra={
                'error_id': error_record['error_id'],
                'severity': error_record['severity'],
                'context': error_record['context'],
                'user_id': error_record.get('user_id'),
                'session_id': error_record.get('session_id')
            }
        )
    
    def get_error_analytics(self, time_range_hours: int = 24) -> Dict[str, Any]:
        """Get comprehensive error analytics"""
        cutoff_time = datetime.utcnow() - timedelta(hours=time_range_hours)
        
        # Filter recent errors
        recent_errors = {}
        total_errors = 0
        
        for error_id, error_info in self.error_cache.items():
            if error_info['last_seen'] and error_info['last_seen'] > cutoff_time:
                recent_errors[error_id] = error_info
                total_errors += error_info['count']
        
        # Calculate error rates by hour
        hourly_rates = defaultdict(int)
        for error_info in recent_errors.values():
            for sample in error_info['samples']:
                hour = datetime.fromisoformat(sample['timestamp']).hour
                hourly_rates[hour] += 1
        
        # Top errors by frequency
        top_errors = sorted(
            recent_errors.items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )[:10]
        
        return {
            'time_range_hours': time_range_hours,
            'total_errors': total_errors,
            'unique_errors': len(recent_errors),
            'hourly_error_rates': dict(hourly_rates),
            'top_errors': [
                {
                    'error_id': error_id,
                    'count': info['count'],
                    'first_seen': info['first_seen'].isoformat() if info['first_seen'] else None,
                    'last_seen': info['last_seen'].isoformat() if info['last_seen'] else None,
                    'latest_sample': list(info['samples'])[-1] if info['samples'] else None
                }
                for error_id, info in top_errors
            ]
        }
    
    def clear_old_errors(self, max_age_hours: int = 168):  # 1 week default
        """Clean up old error data"""
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
        
        errors_to_remove = []
        for error_id, error_info in self.error_cache.items():
            if error_info['last_seen'] and error_info['last_seen'] < cutoff_time:
                errors_to_remove.append(error_id)
        
        for error_id in errors_to_remove:
            del self.error_cache[error_id]
        
        logger.info(f"Cleaned up {len(errors_to_remove)} old error records")

    async def attempt_recovery(self, error_type: str, context: Dict[str, Any] = None) -> bool:
        """Attempt automatic recovery for known error types"""
        try:
            if error_type in self.recovery_strategies:
                recovery_func = self.recovery_strategies[error_type]
                success = await recovery_func(context or {})

                if success:
                    logger.info(f"✅ Successfully recovered from {error_type}")
                    await self._reset_circuit_breaker(error_type)
                    return True
                else:
                    logger.warning(f"❌ Failed to recover from {error_type}")
                    await self._trip_circuit_breaker(error_type)
                    return False
            else:
                logger.warning(f"No recovery strategy for error type: {error_type}")
                return False

        except Exception as e:
            logger.error(f"Recovery attempt failed for {error_type}: {e}")
            return False

    async def _recover_database_connection(self, context: Dict[str, Any]) -> bool:
        """Recover database connection issues"""
        try:
            from app.core.database import get_db
            from sqlalchemy import text

            # Test database connection
            db = next(get_db())
            db.execute(text("SELECT 1")).scalar()

            logger.info("Database connection recovered")
            return True

        except Exception as e:
            logger.error(f"Database recovery failed: {e}")
            return False

    async def _recover_redis_connection(self, context: Dict[str, Any]) -> bool:
        """Recover Redis connection issues"""
        try:
            # Get cache service with lazy import
            cache_service = get_cache_service()
            if not cache_service:
                return False

            # Test cache connection
            test_key = "recovery_test"
            await cache_service.set(test_key, "test", "default", 10)
            result = await cache_service.get(test_key, "default")

            if result == "test":
                await cache_service.delete(test_key, "default")
                logger.info("Cache connection recovered")
                return True
            else:
                return False

        except Exception as e:
            logger.error(f"Redis recovery failed: {e}")
            return False

    async def _trip_circuit_breaker(self, service: str):
        """Trip circuit breaker for a service"""
        self.circuit_breakers[service]['state'] = 'open'
        self.circuit_breakers[service]['failure_count'] += 1
        self.circuit_breakers[service]['last_failure_time'] = datetime.utcnow()

        logger.warning(f"🔴 Circuit breaker OPEN for {service}")

    async def _reset_circuit_breaker(self, service: str):
        """Reset circuit breaker for a service"""
        self.circuit_breakers[service]['state'] = 'closed'
        self.circuit_breakers[service]['failure_count'] = 0
        self.circuit_breakers[service]['success_count'] += 1

        logger.info(f"🟢 Circuit breaker CLOSED for {service}")


# Global error tracking instance
error_tracker = ErrorTrackingService()
