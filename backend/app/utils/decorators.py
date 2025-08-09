"""
Utility decorators for caching, performance monitoring, and circuit breaker patterns
"""

import time
import asyncio
import functools
import logging
from typing import Any, Callable, Optional, Dict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def cached(key_prefix: str = "default", ttl: int = 300, config: Optional[Any] = None):
    """
    Caching decorator with fallback to in-memory cache
    """
    # Simple in-memory cache as fallback
    _cache: Dict[str, Dict[str, Any]] = {}
    
    def decorator(func: Callable):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Check cache
            if cache_key in _cache:
                cache_entry = _cache[cache_key]
                if datetime.utcnow() < cache_entry["expires"]:
                    logger.debug(f"Cache hit for {cache_key}")
                    return cache_entry["value"]
                else:
                    # Expired, remove from cache
                    del _cache[cache_key]
            
            # Execute function
            try:
                result = await func(*args, **kwargs)
                
                # Store in cache
                _cache[cache_key] = {
                    "value": result,
                    "expires": datetime.utcnow() + timedelta(seconds=ttl)
                }
                
                logger.debug(f"Cached result for {cache_key}")
                return result
                
            except Exception as e:
                logger.error(f"Error in cached function {func.__name__}: {e}")
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Check cache
            if cache_key in _cache:
                cache_entry = _cache[cache_key]
                if datetime.utcnow() < cache_entry["expires"]:
                    logger.debug(f"Cache hit for {cache_key}")
                    return cache_entry["value"]
                else:
                    # Expired, remove from cache
                    del _cache[cache_key]
            
            # Execute function
            try:
                result = func(*args, **kwargs)
                
                # Store in cache
                _cache[cache_key] = {
                    "value": result,
                    "expires": datetime.utcnow() + timedelta(seconds=ttl)
                }
                
                logger.debug(f"Cached result for {cache_key}")
                return result
                
            except Exception as e:
                logger.error(f"Error in cached function {func.__name__}: {e}")
                raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator


def performance_monitor(metric_name: str = None):
    """
    Performance monitoring decorator
    """
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
                
                logger.info(
                    f"Performance: {name} took {duration:.2f}ms"
                    + (f" (error: {error})" if error else "")
                )
        
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
                
                logger.info(
                    f"Performance: {name} took {duration:.2f}ms"
                    + (f" (error: {error})" if error else "")
                )
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator


def circuit_breaker(service_name: str, failure_threshold: int = 5, recovery_timeout: int = 60):
    """
    Circuit breaker decorator with simple state management
    """
    # Simple circuit breaker state
    _circuit_state: Dict[str, Dict[str, Any]] = {}
    
    def decorator(func: Callable):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Initialize circuit state if not exists
            if service_name not in _circuit_state:
                _circuit_state[service_name] = {
                    "state": "closed",  # closed, open, half-open
                    "failure_count": 0,
                    "last_failure_time": None,
                    "success_count": 0
                }
            
            circuit = _circuit_state[service_name]
            
            # Check if circuit is open
            if circuit["state"] == "open":
                if circuit["last_failure_time"]:
                    time_since_failure = (datetime.utcnow() - circuit["last_failure_time"]).total_seconds()
                    if time_since_failure < recovery_timeout:
                        logger.warning(f"Circuit breaker OPEN for {service_name}")
                        raise Exception(f"Circuit breaker is open for {service_name}")
                    else:
                        # Try to recover
                        circuit["state"] = "half-open"
                        logger.info(f"Circuit breaker HALF-OPEN for {service_name}")
            
            try:
                result = await func(*args, **kwargs)
                
                # Success - reset or close circuit
                if circuit["state"] in ["half-open", "open"]:
                    circuit["state"] = "closed"
                    circuit["failure_count"] = 0
                    logger.info(f"Circuit breaker CLOSED for {service_name}")
                
                circuit["success_count"] += 1
                return result
                
            except Exception as e:
                # Failure - increment counter
                circuit["failure_count"] += 1
                circuit["last_failure_time"] = datetime.utcnow()
                
                # Open circuit if threshold reached
                if circuit["failure_count"] >= failure_threshold:
                    circuit["state"] = "open"
                    logger.warning(f"Circuit breaker OPENED for {service_name}")
                
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Initialize circuit state if not exists
            if service_name not in _circuit_state:
                _circuit_state[service_name] = {
                    "state": "closed",
                    "failure_count": 0,
                    "last_failure_time": None,
                    "success_count": 0
                }
            
            circuit = _circuit_state[service_name]
            
            # Check if circuit is open
            if circuit["state"] == "open":
                if circuit["last_failure_time"]:
                    time_since_failure = (datetime.utcnow() - circuit["last_failure_time"]).total_seconds()
                    if time_since_failure < recovery_timeout:
                        logger.warning(f"Circuit breaker OPEN for {service_name}")
                        raise Exception(f"Circuit breaker is open for {service_name}")
                    else:
                        # Try to recover
                        circuit["state"] = "half-open"
                        logger.info(f"Circuit breaker HALF-OPEN for {service_name}")
            
            try:
                result = func(*args, **kwargs)
                
                # Success - reset or close circuit
                if circuit["state"] in ["half-open", "open"]:
                    circuit["state"] = "closed"
                    circuit["failure_count"] = 0
                    logger.info(f"Circuit breaker CLOSED for {service_name}")
                
                circuit["success_count"] += 1
                return result
                
            except Exception as e:
                # Failure - increment counter
                circuit["failure_count"] += 1
                circuit["last_failure_time"] = datetime.utcnow()
                
                # Open circuit if threshold reached
                if circuit["failure_count"] >= failure_threshold:
                    circuit["state"] = "open"
                    logger.warning(f"Circuit breaker OPENED for {service_name}")
                
                raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator
