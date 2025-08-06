"""
Enterprise Redis Caching Service
High-performance caching layer for production environments
"""

import json
import logging
import asyncio
from typing import Any, Optional, Dict, List, Union
from datetime import datetime, timedelta
import hashlib

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

from ..core.config import settings

logger = logging.getLogger(__name__)


class CacheService:
    """Enterprise-grade Redis caching service"""
    
    def __init__(self):
        self.redis_client = None
        self.fallback_cache = {}  # In-memory fallback
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "errors": 0,
            "fallback_hits": 0
        }
        
        # Cache TTL configurations
        self.ttl_configs = {
            "live_config": 300,      # 5 minutes
            "api_config": 600,       # 10 minutes
            "rag_config": 600,       # 10 minutes
            "user_session": 3600,    # 1 hour
            "chat_history": 1800,    # 30 minutes
            "health_check": 30,      # 30 seconds
            "analytics": 900,        # 15 minutes
            "tenant_info": 1800,     # 30 minutes
            "default": 300           # 5 minutes
        }
    
    async def initialize(self):
        """Initialize Redis connection"""
        if not REDIS_AVAILABLE:
            logger.warning("Redis not available, using in-memory fallback cache")
            return
        
        try:
            redis_url = getattr(settings, 'REDIS_URL', None)
            if redis_url:
                self.redis_client = redis.from_url(redis_url, decode_responses=True)
            else:
                self.redis_client = redis.Redis(
                    host=getattr(settings, 'REDIS_HOST', 'localhost'),
                    port=getattr(settings, 'REDIS_PORT', 6379),
                    db=getattr(settings, 'REDIS_DB', 0),
                    decode_responses=True,
                    socket_timeout=5,
                    socket_connect_timeout=5,
                    retry_on_timeout=True
                )
            
            # Test connection
            await self.redis_client.ping()
            logger.info("✅ Redis cache service initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Redis initialization failed: {e}")
            self.redis_client = None
    
    async def get(self, key: str, cache_type: str = "default") -> Optional[Any]:
        """Get value from cache"""
        try:
            if self.redis_client:
                # Try Redis first
                cached_value = await self.redis_client.get(self._format_key(key, cache_type))
                if cached_value:
                    self.cache_stats["hits"] += 1
                    return json.loads(cached_value)
                else:
                    self.cache_stats["misses"] += 1
                    return None
            else:
                # Fallback to in-memory cache
                cache_key = self._format_key(key, cache_type)
                if cache_key in self.fallback_cache:
                    cache_entry = self.fallback_cache[cache_key]
                    if cache_entry["expires_at"] > datetime.utcnow():
                        self.cache_stats["fallback_hits"] += 1
                        return cache_entry["value"]
                    else:
                        # Expired, remove it
                        del self.fallback_cache[cache_key]
                
                self.cache_stats["misses"] += 1
                return None
                
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            self.cache_stats["errors"] += 1
            return None
    
    async def set(self, key: str, value: Any, cache_type: str = "default", ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        try:
            ttl = ttl or self.ttl_configs.get(cache_type, self.ttl_configs["default"])
            
            if self.redis_client:
                # Store in Redis
                await self.redis_client.setex(
                    self._format_key(key, cache_type),
                    ttl,
                    json.dumps(value, default=str)
                )
                return True
            else:
                # Store in fallback cache
                cache_key = self._format_key(key, cache_type)
                self.fallback_cache[cache_key] = {
                    "value": value,
                    "expires_at": datetime.utcnow() + timedelta(seconds=ttl)
                }
                
                # Clean up expired entries periodically
                await self._cleanup_fallback_cache()
                return True
                
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            self.cache_stats["errors"] += 1
            return False
    
    async def delete(self, key: str, cache_type: str = "default") -> bool:
        """Delete value from cache"""
        try:
            if self.redis_client:
                result = await self.redis_client.delete(self._format_key(key, cache_type))
                return result > 0
            else:
                cache_key = self._format_key(key, cache_type)
                if cache_key in self.fallback_cache:
                    del self.fallback_cache[cache_key]
                    return True
                return False
                
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            self.cache_stats["errors"] += 1
            return False
    
    async def exists(self, key: str, cache_type: str = "default") -> bool:
        """Check if key exists in cache"""
        try:
            if self.redis_client:
                return await self.redis_client.exists(self._format_key(key, cache_type)) > 0
            else:
                cache_key = self._format_key(key, cache_type)
                if cache_key in self.fallback_cache:
                    cache_entry = self.fallback_cache[cache_key]
                    if cache_entry["expires_at"] > datetime.utcnow():
                        return True
                    else:
                        del self.fallback_cache[cache_key]
                return False
                
        except Exception as e:
            logger.error(f"Cache exists error for key {key}: {e}")
            return False
    
    async def increment(self, key: str, cache_type: str = "default", amount: int = 1) -> Optional[int]:
        """Increment a numeric value in cache"""
        try:
            if self.redis_client:
                return await self.redis_client.incrby(self._format_key(key, cache_type), amount)
            else:
                # Fallback implementation
                cache_key = self._format_key(key, cache_type)
                current_value = await self.get(key, cache_type) or 0
                new_value = int(current_value) + amount
                await self.set(key, new_value, cache_type)
                return new_value
                
        except Exception as e:
            logger.error(f"Cache increment error for key {key}: {e}")
            return None
    
    async def get_multiple(self, keys: List[str], cache_type: str = "default") -> Dict[str, Any]:
        """Get multiple values from cache"""
        result = {}
        
        if self.redis_client:
            try:
                formatted_keys = [self._format_key(key, cache_type) for key in keys]
                values = await self.redis_client.mget(formatted_keys)
                
                for i, value in enumerate(values):
                    if value:
                        result[keys[i]] = json.loads(value)
                        self.cache_stats["hits"] += 1
                    else:
                        self.cache_stats["misses"] += 1
                        
            except Exception as e:
                logger.error(f"Cache mget error: {e}")
                self.cache_stats["errors"] += 1
        else:
            # Fallback: get each key individually
            for key in keys:
                value = await self.get(key, cache_type)
                if value is not None:
                    result[key] = value
        
        return result
    
    async def set_multiple(self, data: Dict[str, Any], cache_type: str = "default", ttl: Optional[int] = None) -> bool:
        """Set multiple values in cache"""
        try:
            ttl = ttl or self.ttl_configs.get(cache_type, self.ttl_configs["default"])
            
            if self.redis_client:
                # Use pipeline for efficiency
                pipe = self.redis_client.pipeline()
                for key, value in data.items():
                    pipe.setex(
                        self._format_key(key, cache_type),
                        ttl,
                        json.dumps(value, default=str)
                    )
                await pipe.execute()
                return True
            else:
                # Fallback: set each key individually
                for key, value in data.items():
                    await self.set(key, value, cache_type, ttl)
                return True
                
        except Exception as e:
            logger.error(f"Cache mset error: {e}")
            self.cache_stats["errors"] += 1
            return False
    
    async def clear_pattern(self, pattern: str, cache_type: str = "default") -> int:
        """Clear all keys matching a pattern"""
        try:
            if self.redis_client:
                pattern_key = self._format_key(pattern, cache_type)
                keys = await self.redis_client.keys(pattern_key)
                if keys:
                    return await self.redis_client.delete(*keys)
                return 0
            else:
                # Fallback: clear matching keys from memory cache
                pattern_key = self._format_key(pattern, cache_type)
                keys_to_delete = [k for k in self.fallback_cache.keys() if pattern in k]
                for key in keys_to_delete:
                    del self.fallback_cache[key]
                return len(keys_to_delete)
                
        except Exception as e:
            logger.error(f"Cache clear pattern error: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
        hit_rate = (self.cache_stats["hits"] / max(total_requests, 1)) * 100
        
        return {
            "hits": self.cache_stats["hits"],
            "misses": self.cache_stats["misses"],
            "errors": self.cache_stats["errors"],
            "fallback_hits": self.cache_stats["fallback_hits"],
            "hit_rate_percent": round(hit_rate, 2),
            "total_requests": total_requests,
            "redis_available": self.redis_client is not None,
            "fallback_cache_size": len(self.fallback_cache)
        }
    
    def _format_key(self, key: str, cache_type: str) -> str:
        """Format cache key with namespace"""
        namespace = getattr(settings, 'CACHE_NAMESPACE', 'chatbot')
        return f"{namespace}:{cache_type}:{key}"
    
    async def _cleanup_fallback_cache(self):
        """Clean up expired entries from fallback cache"""
        if len(self.fallback_cache) > 1000:  # Only cleanup if cache is large
            now = datetime.utcnow()
            expired_keys = [
                key for key, entry in self.fallback_cache.items()
                if entry["expires_at"] <= now
            ]
            for key in expired_keys:
                del self.fallback_cache[key]


# Global cache service instance
cache_service = CacheService()
