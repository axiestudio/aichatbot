"""
Circuit Breaker Service
Implements circuit breaker pattern for external API calls and database operations
"""

import time
import asyncio
import logging
from typing import Dict, Any, Optional, Callable, Union
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from collections import deque

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Circuit is open, failing fast
    HALF_OPEN = "half_open"  # Testing if service is back


@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 5          # Number of failures to open circuit
    recovery_timeout: int = 60          # Seconds before trying half-open
    success_threshold: int = 3          # Successes needed to close from half-open
    timeout: float = 30.0               # Request timeout in seconds
    expected_exception: tuple = (Exception,)  # Exceptions that count as failures


@dataclass
class CircuitBreakerStats:
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    timeouts: int = 0
    circuit_opens: int = 0
    last_failure_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    recent_failures: deque = field(default_factory=lambda: deque(maxlen=100))
    recent_successes: deque = field(default_factory=lambda: deque(maxlen=100))


class CircuitBreaker:
    """Circuit breaker implementation for resilient service calls"""
    
    def __init__(self, name: str, config: CircuitBreakerConfig):
        self.name = name
        self.config = config
        self.state = CircuitState.CLOSED
        self.stats = CircuitBreakerStats()
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.next_attempt_time = None
        
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        
        # Check if circuit is open and if we should try again
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self._attempt_reset()
            else:
                raise CircuitBreakerOpenException(
                    f"Circuit breaker '{self.name}' is OPEN. "
                    f"Next attempt in {self._time_until_next_attempt():.1f} seconds"
                )
        
        # Record attempt
        self.stats.total_requests += 1
        start_time = time.time()
        
        try:
            # Execute the function with timeout
            if asyncio.iscoroutinefunction(func):
                result = await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=self.config.timeout
                )
            else:
                result = func(*args, **kwargs)
            
            # Record success
            self._on_success()
            return result
            
        except asyncio.TimeoutError:
            self.stats.timeouts += 1
            self._on_failure()
            raise CircuitBreakerTimeoutException(
                f"Circuit breaker '{self.name}' timeout after {self.config.timeout}s"
            )
            
        except self.config.expected_exception as e:
            self._on_failure()
            raise
            
        except Exception as e:
            # Unexpected exceptions don't count as failures
            logger.warning(f"Unexpected exception in circuit breaker '{self.name}': {e}")
            raise
        
        finally:
            duration = time.time() - start_time
            logger.debug(f"Circuit breaker '{self.name}' call took {duration:.3f}s")
    
    def _on_success(self):
        """Handle successful call"""
        self.failure_count = 0
        self.success_count += 1
        self.stats.successful_requests += 1
        self.stats.last_success_time = datetime.utcnow()
        self.stats.recent_successes.append(datetime.utcnow())
        
        # If we're in half-open state, check if we should close
        if self.state == CircuitState.HALF_OPEN:
            if self.success_count >= self.config.success_threshold:
                self._close_circuit()
    
    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.success_count = 0
        self.stats.failed_requests += 1
        self.stats.last_failure_time = datetime.utcnow()
        self.stats.recent_failures.append(datetime.utcnow())
        
        # Check if we should open the circuit
        if (self.state == CircuitState.CLOSED and 
            self.failure_count >= self.config.failure_threshold):
            self._open_circuit()
        elif self.state == CircuitState.HALF_OPEN:
            # If we fail in half-open, go back to open
            self._open_circuit()
    
    def _open_circuit(self):
        """Open the circuit"""
        self.state = CircuitState.OPEN
        self.stats.circuit_opens += 1
        self.last_failure_time = datetime.utcnow()
        self.next_attempt_time = self.last_failure_time + timedelta(
            seconds=self.config.recovery_timeout
        )
        
        logger.warning(
            f"Circuit breaker '{self.name}' OPENED after {self.failure_count} failures. "
            f"Will retry at {self.next_attempt_time}"
        )
    
    def _close_circuit(self):
        """Close the circuit"""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        
        logger.info(f"Circuit breaker '{self.name}' CLOSED - service recovered")
    
    def _attempt_reset(self):
        """Attempt to reset circuit to half-open"""
        self.state = CircuitState.HALF_OPEN
        self.success_count = 0
        
        logger.info(f"Circuit breaker '{self.name}' attempting reset to HALF_OPEN")
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if self.next_attempt_time is None:
            return True
        return datetime.utcnow() >= self.next_attempt_time
    
    def _time_until_next_attempt(self) -> float:
        """Get seconds until next attempt is allowed"""
        if self.next_attempt_time is None:
            return 0
        delta = self.next_attempt_time - datetime.utcnow()
        return max(0, delta.total_seconds())
    
    def get_stats(self) -> Dict[str, Any]:
        """Get circuit breaker statistics"""
        success_rate = 0
        if self.stats.total_requests > 0:
            success_rate = (self.stats.successful_requests / self.stats.total_requests) * 100
        
        # Calculate recent failure rate (last 5 minutes)
        recent_cutoff = datetime.utcnow() - timedelta(minutes=5)
        recent_failures = len([
            f for f in self.stats.recent_failures 
            if f > recent_cutoff
        ])
        recent_successes = len([
            s for s in self.stats.recent_successes 
            if s > recent_cutoff
        ])
        recent_total = recent_failures + recent_successes
        recent_failure_rate = (recent_failures / recent_total * 100) if recent_total > 0 else 0
        
        return {
            'name': self.name,
            'state': self.state.value,
            'total_requests': self.stats.total_requests,
            'successful_requests': self.stats.successful_requests,
            'failed_requests': self.stats.failed_requests,
            'timeouts': self.stats.timeouts,
            'circuit_opens': self.stats.circuit_opens,
            'success_rate': round(success_rate, 2),
            'recent_failure_rate': round(recent_failure_rate, 2),
            'failure_count': self.failure_count,
            'success_count': self.success_count,
            'last_failure_time': self.stats.last_failure_time.isoformat() if self.stats.last_failure_time else None,
            'last_success_time': self.stats.last_success_time.isoformat() if self.stats.last_success_time else None,
            'next_attempt_time': self.next_attempt_time.isoformat() if self.next_attempt_time else None,
            'time_until_next_attempt': self._time_until_next_attempt()
        }
    
    def reset(self):
        """Manually reset circuit breaker"""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.next_attempt_time = None
        
        logger.info(f"Circuit breaker '{self.name}' manually reset")


class CircuitBreakerManager:
    """Manages multiple circuit breakers"""
    
    def __init__(self):
        self.breakers: Dict[str, CircuitBreaker] = {}
        self.default_config = CircuitBreakerConfig()
    
    def get_breaker(self, name: str, config: Optional[CircuitBreakerConfig] = None) -> CircuitBreaker:
        """Get or create a circuit breaker"""
        if name not in self.breakers:
            breaker_config = config or self.default_config
            self.breakers[name] = CircuitBreaker(name, breaker_config)
        
        return self.breakers[name]
    
    def get_all_stats(self) -> Dict[str, Any]:
        """Get statistics for all circuit breakers"""
        return {
            name: breaker.get_stats()
            for name, breaker in self.breakers.items()
        }
    
    def reset_all(self):
        """Reset all circuit breakers"""
        for breaker in self.breakers.values():
            breaker.reset()
        
        logger.info("All circuit breakers reset")
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get overall health summary"""
        total_breakers = len(self.breakers)
        open_breakers = len([b for b in self.breakers.values() if b.state == CircuitState.OPEN])
        half_open_breakers = len([b for b in self.breakers.values() if b.state == CircuitState.HALF_OPEN])
        
        health_status = "healthy"
        if open_breakers > 0:
            health_status = "degraded" if open_breakers < total_breakers else "critical"
        elif half_open_breakers > 0:
            health_status = "warning"
        
        return {
            'health_status': health_status,
            'total_breakers': total_breakers,
            'closed_breakers': total_breakers - open_breakers - half_open_breakers,
            'half_open_breakers': half_open_breakers,
            'open_breakers': open_breakers,
            'breaker_details': {
                name: {
                    'state': breaker.state.value,
                    'failure_count': breaker.failure_count,
                    'success_rate': round(
                        (breaker.stats.successful_requests / max(breaker.stats.total_requests, 1)) * 100, 2
                    )
                }
                for name, breaker in self.breakers.items()
            }
        }


class CircuitBreakerOpenException(Exception):
    """Raised when circuit breaker is open"""
    pass


class CircuitBreakerTimeoutException(Exception):
    """Raised when circuit breaker times out"""
    pass


# Global circuit breaker manager
circuit_manager = CircuitBreakerManager()


# Decorator for easy circuit breaker usage
def circuit_breaker(name: str, config: Optional[CircuitBreakerConfig] = None):
    """Decorator to add circuit breaker protection to functions"""
    def decorator(func):
        breaker = circuit_manager.get_breaker(name, config)
        
        async def async_wrapper(*args, **kwargs):
            return await breaker.call(func, *args, **kwargs)
        
        def sync_wrapper(*args, **kwargs):
            return asyncio.run(breaker.call(func, *args, **kwargs))
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator
