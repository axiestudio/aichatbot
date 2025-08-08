"""
Supabase Caching Service
High-performance caching layer using Supabase as backend
"""

import json
import logging
import asyncio
from typing import Any, Optional, Dict, List, Union
from datetime import datetime, timedelta
import hashlib

# Import Supabase cache service
from .supabase_cache_service import supabase_cache_service

from ..core.config import settings

logger = logging.getLogger(__name__)


class CacheService:
    """Supabase-based caching service - Redis replacement"""

    def __init__(self):
        self.supabase_cache = supabase_cache_service
        self._initialized = False

    async def initialize(self):
        """Initialize Supabase cache connection"""
        try:
            success = await self.supabase_cache.initialize()
            self._initialized = success

            if success:
                logger.info("✅ Supabase cache service initialized")
            else:
                logger.warning("⚠️ Supabase cache initialization failed, using fallback")

        except Exception as e:
            logger.warning(f"Supabase cache connection failed: {str(e)}, using fallback cache")
            self._initialized = False

    async def get(self, key: str, cache_type: str = "default") -> Optional[Any]:
        """Get value from cache"""
        return await self.supabase_cache.get(key, cache_type)

    async def set(self, key: str, value: Any, cache_type: str = "default", ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        return await self.supabase_cache.set(key, value, cache_type, ttl)

    async def delete(self, key: str, cache_type: str = "default") -> bool:
        """Delete value from cache"""
        return await self.supabase_cache.delete(key, cache_type)

    async def exists(self, key: str, cache_type: str = "default") -> bool:
        """Check if key exists in cache"""
        return await self.supabase_cache.exists(key, cache_type)

    async def expire(self, key: str, ttl: int, cache_type: str = "default") -> bool:
        """Set expiration time for existing key"""
        return await self.supabase_cache.expire(key, ttl, cache_type)

    async def clear_type(self, cache_type: str) -> bool:
        """Clear all entries of a specific cache type"""
        return await self.supabase_cache.clear_type(cache_type)

    async def clear_all(self) -> bool:
        """Clear all cache entries"""
        return await self.supabase_cache.clear_all()

    async def cleanup_expired(self) -> int:
        """Clean up expired entries"""
        return await self.supabase_cache.cleanup_expired()

    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return await self.supabase_cache.get_stats()

    # Redis compatibility methods
    async def ping(self) -> bool:
        """Ping cache service (Redis compatibility)"""
        try:
            # Test by setting and getting a test key
            test_key = "ping_test"
            await self.set(test_key, "pong", "test", 10)
            result = await self.get(test_key, "test")
            await self.delete(test_key, "test")
            return result == "pong"
        except Exception:
            return False

    async def flushall(self) -> bool:
        """Flush all cache (Redis compatibility)"""
        return await self.clear_all()

    async def keys(self, pattern: str = "*") -> List[str]:
        """Get keys matching pattern (limited Redis compatibility)"""
        # Note: This is a simplified implementation
        # In a real Redis replacement, you'd need more sophisticated pattern matching
        try:
            stats = await self.get_stats()
            return list(stats.get("entries_by_type", {}).keys())
        except Exception:
            return []


# Global cache service instance
cache_service = CacheService()
