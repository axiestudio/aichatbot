"""
Advanced Caching Service
Multi-layer caching with Redis, memory cache, and intelligent cache strategies
"""

import json
import time
import hashlib
import logging
import asyncio
from typing import Any, Optional, Dict, List, Union, Callable
from datetime import datetime, timedelta
from functools import wraps
from dataclasses import dataclass
import redis.asyncio as redis

from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class CacheConfig:
    ttl: int = 3600                    # Time to live in seconds
    max_size: int = 1000               # Max items in memory cache
    compression: bool = False          # Enable compression for large values
    serialize_json: bool = True        # Auto JSON serialization
    cache_null: bool = False           # Cache null/None values
    refresh_ahead: bool = True         # Refresh cache before expiry
    refresh_threshold: float = 0.8     # Refresh when 80% of TTL elapsed


class AdvancedCacheService:
    """Multi-layer caching service with Redis and memory cache"""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.memory_cache: Dict[str, Dict[str, Any]] = {}
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'memory_hits': 0,
            'redis_hits': 0,
            'errors': 0
        }
        self.default_config = CacheConfig()
        
    async def initialize(self):
        """Initialize Redis connection"""
        try:
            if settings.REDIS_URL:
                self.redis_client = redis.from_url(
                    settings.REDIS_URL,
                    encoding="utf-8",
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True,
                    health_check_interval=30
                )
                
                # Test connection
                await self.redis_client.ping()
                logger.info("Redis cache initialized successfully")
            else:
                logger.warning("Redis URL not configured, using memory cache only")
                
        except Exception as e:
            logger.error(f"Failed to initialize Redis cache: {e}")
            self.redis_client = None
    
    async def get(
        self, 
        key: str, 
        default: Any = None,
        config: Optional[CacheConfig] = None
    ) -> Any:
        """Get value from cache with multi-layer fallback"""
        cache_config = config or self.default_config
        
        try:
            # Try memory cache first
            if key in self.memory_cache:
                cache_item = self.memory_cache[key]
                if self._is_valid(cache_item):
                    self.cache_stats['hits'] += 1
                    self.cache_stats['memory_hits'] += 1
                    
                    # Check if we should refresh ahead
                    if (cache_config.refresh_ahead and 
                        self._should_refresh_ahead(cache_item, cache_config)):
                        asyncio.create_task(self._refresh_ahead(key, cache_config))
                    
                    return self._deserialize(cache_item['value'], cache_config)
                else:
                    # Remove expired item
                    del self.memory_cache[key]
            
            # Try Redis cache
            if self.redis_client:
                try:
                    redis_value = await self.redis_client.get(key)
                    if redis_value is not None:
                        self.cache_stats['hits'] += 1
                        self.cache_stats['redis_hits'] += 1
                        
                        # Store in memory cache for faster access
                        cache_item = {
                            'value': redis_value,
                            'timestamp': time.time(),
                            'ttl': cache_config.ttl
                        }
                        self._store_in_memory(key, cache_item, cache_config)
                        
                        return self._deserialize(redis_value, cache_config)
                        
                except Exception as e:
                    logger.warning(f"Redis get error for key '{key}': {e}")
                    self.cache_stats['errors'] += 1
            
            # Cache miss
            self.cache_stats['misses'] += 1
            return default
            
        except Exception as e:
            logger.error(f"Cache get error for key '{key}': {e}")
            self.cache_stats['errors'] += 1
            return default
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        config: Optional[CacheConfig] = None
    ) -> bool:
        """Set value in cache with multi-layer storage"""
        cache_config = config or self.default_config
        cache_ttl = ttl or cache_config.ttl
        
        try:
            # Don't cache None values unless configured to do so
            if value is None and not cache_config.cache_null:
                return False
            
            serialized_value = self._serialize(value, cache_config)
            timestamp = time.time()
            
            # Store in memory cache
            cache_item = {
                'value': serialized_value,
                'timestamp': timestamp,
                'ttl': cache_ttl
            }
            self._store_in_memory(key, cache_item, cache_config)
            
            # Store in Redis cache
            if self.redis_client:
                try:
                    await self.redis_client.setex(key, cache_ttl, serialized_value)
                except Exception as e:
                    logger.warning(f"Redis set error for key '{key}': {e}")
                    self.cache_stats['errors'] += 1
            
            self.cache_stats['sets'] += 1
            return True
            
        except Exception as e:
            logger.error(f"Cache set error for key '{key}': {e}")
            self.cache_stats['errors'] += 1
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            # Remove from memory cache
            if key in self.memory_cache:
                del self.memory_cache[key]
            
            # Remove from Redis cache
            if self.redis_client:
                try:
                    await self.redis_client.delete(key)
                except Exception as e:
                    logger.warning(f"Redis delete error for key '{key}': {e}")
                    self.cache_stats['errors'] += 1
            
            self.cache_stats['deletes'] += 1
            return True
            
        except Exception as e:
            logger.error(f"Cache delete error for key '{key}': {e}")
            self.cache_stats['errors'] += 1
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            # Check memory cache
            if key in self.memory_cache:
                if self._is_valid(self.memory_cache[key]):
                    return True
                else:
                    del self.memory_cache[key]
            
            # Check Redis cache
            if self.redis_client:
                try:
                    return await self.redis_client.exists(key) > 0
                except Exception as e:
                    logger.warning(f"Redis exists error for key '{key}': {e}")
                    self.cache_stats['errors'] += 1
            
            return False
            
        except Exception as e:
            logger.error(f"Cache exists error for key '{key}': {e}")
            self.cache_stats['errors'] += 1
            return False
    
    async def clear(self, pattern: Optional[str] = None) -> int:
        """Clear cache entries, optionally by pattern"""
        cleared_count = 0
        
        try:
            if pattern:
                # Clear by pattern
                if self.redis_client:
                    try:
                        keys = await self.redis_client.keys(pattern)
                        if keys:
                            cleared_count += await self.redis_client.delete(*keys)
                    except Exception as e:
                        logger.warning(f"Redis clear pattern error: {e}")
                
                # Clear from memory cache
                keys_to_remove = [k for k in self.memory_cache.keys() if self._match_pattern(k, pattern)]
                for key in keys_to_remove:
                    del self.memory_cache[key]
                    cleared_count += 1
            else:
                # Clear all
                if self.redis_client:
                    try:
                        await self.redis_client.flushdb()
                    except Exception as e:
                        logger.warning(f"Redis flush error: {e}")
                
                cleared_count = len(self.memory_cache)
                self.memory_cache.clear()
            
            logger.info(f"Cleared {cleared_count} cache entries")
            return cleared_count
            
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            self.cache_stats['errors'] += 1
            return 0
    
    def _store_in_memory(self, key: str, cache_item: Dict[str, Any], config: CacheConfig):
        """Store item in memory cache with size management"""
        # Remove expired items if cache is full
        if len(self.memory_cache) >= config.max_size:
            self._cleanup_memory_cache()
        
        # If still full, remove oldest items
        if len(self.memory_cache) >= config.max_size:
            oldest_keys = sorted(
                self.memory_cache.keys(),
                key=lambda k: self.memory_cache[k]['timestamp']
            )[:len(self.memory_cache) - config.max_size + 1]
            
            for old_key in oldest_keys:
                del self.memory_cache[old_key]
        
        self.memory_cache[key] = cache_item
    
    def _cleanup_memory_cache(self):
        """Remove expired items from memory cache"""
        current_time = time.time()
        expired_keys = []
        
        for key, cache_item in self.memory_cache.items():
            if current_time - cache_item['timestamp'] > cache_item['ttl']:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.memory_cache[key]
    
    def _is_valid(self, cache_item: Dict[str, Any]) -> bool:
        """Check if cache item is still valid"""
        current_time = time.time()
        return current_time - cache_item['timestamp'] < cache_item['ttl']
    
    def _should_refresh_ahead(self, cache_item: Dict[str, Any], config: CacheConfig) -> bool:
        """Check if cache should be refreshed ahead of expiry"""
        current_time = time.time()
        elapsed_time = current_time - cache_item['timestamp']
        return elapsed_time > (cache_item['ttl'] * config.refresh_threshold)
    
    async def _refresh_ahead(self, key: str, config: CacheConfig):
        """Refresh cache ahead of expiry (placeholder for implementation)"""
        # This would typically call the original function to refresh the cache
        # Implementation depends on how the cache decorator is used
        logger.debug(f"Refresh ahead triggered for key: {key}")
    
    def _serialize(self, value: Any, config: CacheConfig) -> str:
        """Serialize value for storage"""
        if config.serialize_json:
            return json.dumps(value, default=str)
        return str(value)
    
    def _deserialize(self, value: str, config: CacheConfig) -> Any:
        """Deserialize value from storage"""
        if config.serialize_json:
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        return value
    
    def _match_pattern(self, key: str, pattern: str) -> bool:
        """Simple pattern matching for cache keys"""
        if '*' in pattern:
            pattern_parts = pattern.split('*')
            if len(pattern_parts) == 2:
                prefix, suffix = pattern_parts
                return key.startswith(prefix) and key.endswith(suffix)
        return key == pattern
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
        hit_rate = (self.cache_stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'total_requests': total_requests,
            'hits': self.cache_stats['hits'],
            'misses': self.cache_stats['misses'],
            'hit_rate': round(hit_rate, 2),
            'memory_hits': self.cache_stats['memory_hits'],
            'redis_hits': self.cache_stats['redis_hits'],
            'sets': self.cache_stats['sets'],
            'deletes': self.cache_stats['deletes'],
            'errors': self.cache_stats['errors'],
            'memory_cache_size': len(self.memory_cache),
            'redis_connected': self.redis_client is not None
        }


# Global cache service instance
cache_service = AdvancedCacheService()


def cached(
    key_prefix: str = "",
    ttl: int = 3600,
    config: Optional[CacheConfig] = None
):
    """Decorator for caching function results"""
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = _generate_cache_key(key_prefix, func.__name__, args, kwargs)
            
            # Try to get from cache
            cached_result = await cache_service.get(cache_key, config=config)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache_service.set(cache_key, result, ttl=ttl, config=config)
            
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            return asyncio.run(async_wrapper(*args, **kwargs))
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator


def _generate_cache_key(prefix: str, func_name: str, args: tuple, kwargs: dict) -> str:
    """Generate cache key from function name and arguments"""
    key_parts = [prefix, func_name] if prefix else [func_name]
    
    # Add args to key
    if args:
        args_str = "_".join(str(arg) for arg in args)
        key_parts.append(args_str)
    
    # Add kwargs to key
    if kwargs:
        kwargs_str = "_".join(f"{k}={v}" for k, v in sorted(kwargs.items()))
        key_parts.append(kwargs_str)
    
    cache_key = ":".join(key_parts)
    
    # Hash long keys to prevent Redis key length issues
    if len(cache_key) > 200:
        cache_key = hashlib.md5(cache_key.encode()).hexdigest()
    
    return cache_key
