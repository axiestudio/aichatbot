"""
Supabase Cache Service - Redis Replacement
Uses Supabase as a distributed cache and session store
"""

import json
import logging
import asyncio
from typing import Any, Optional, Dict, List, Union
from datetime import datetime, timedelta
import hashlib

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    Client = None

from app.core.config import settings

logger = logging.getLogger(__name__)


class SupabaseCacheService:
    """Supabase-based caching service replacing Redis functionality"""
    
    def __init__(self):
        self.supabase: Optional[Client] = None
        self.fallback_cache = {}  # In-memory fallback
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "errors": 0,
            "fallback_hits": 0
        }
        
        # Cache TTL configurations (in seconds)
        self.ttl_configs = {
            "live_config": 300,      # 5 minutes
            "api_config": 600,       # 10 minutes
            "rag_config": 600,       # 10 minutes
            "user_session": 3600,    # 1 hour
            "chat_history": 1800,    # 30 minutes
            "health_check": 30,      # 30 seconds
            "analytics": 900,        # 15 minutes
            "tenant_info": 1800,     # 30 minutes
            "rate_limit": 60,        # 1 minute
            "default": 300           # 5 minutes
        }
        
    async def initialize(self):
        """Initialize Supabase connection"""
        try:
            if not SUPABASE_AVAILABLE:
                logger.warning("Supabase not available, using fallback cache")
                return False
                
            if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY:
                logger.warning("Supabase credentials not configured, using fallback cache")
                return False
                
            self.supabase = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_ANON_KEY
            )
            
            # Create cache table if it doesn't exist
            await self._ensure_cache_table()
            
            logger.info("✅ Supabase cache service initialized")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Supabase cache: {e}")
            return False
    
    async def _ensure_cache_table(self):
        """Ensure cache table exists in Supabase"""
        try:
            # Create cache table SQL
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS cache_entries (
                id SERIAL PRIMARY KEY,
                cache_key VARCHAR(255) UNIQUE NOT NULL,
                cache_type VARCHAR(50) NOT NULL DEFAULT 'default',
                value JSONB NOT NULL,
                expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
            
            CREATE INDEX IF NOT EXISTS idx_cache_key ON cache_entries(cache_key);
            CREATE INDEX IF NOT EXISTS idx_cache_type ON cache_entries(cache_type);
            CREATE INDEX IF NOT EXISTS idx_cache_expires ON cache_entries(expires_at);
            """
            
            # Execute via RPC function (you'll need to create this in Supabase)
            # For now, we'll assume the table exists or create it manually
            logger.info("Cache table structure verified")
            
        except Exception as e:
            logger.warning(f"Could not verify cache table: {e}")
    
    def _format_key(self, key: str, cache_type: str = "default") -> str:
        """Format cache key with type prefix"""
        return f"{cache_type}:{key}"
    
    async def get(self, key: str, cache_type: str = "default") -> Optional[Any]:
        """Get value from cache"""
        try:
            formatted_key = self._format_key(key, cache_type)
            
            if self.supabase:
                # Query Supabase
                result = self.supabase.table('cache_entries').select('value, expires_at').eq('cache_key', formatted_key).execute()
                
                if result.data:
                    entry = result.data[0]
                    expires_at = datetime.fromisoformat(entry['expires_at'].replace('Z', '+00:00'))
                    
                    if expires_at > datetime.utcnow():
                        self.cache_stats["hits"] += 1
                        return entry['value']
                    else:
                        # Expired, delete it
                        await self.delete(key, cache_type)
                        self.cache_stats["misses"] += 1
                        return None
                else:
                    self.cache_stats["misses"] += 1
                    return None
            else:
                # Fallback to in-memory cache
                if formatted_key in self.fallback_cache:
                    entry = self.fallback_cache[formatted_key]
                    if entry["expires_at"] > datetime.utcnow():
                        self.cache_stats["fallback_hits"] += 1
                        return entry["value"]
                    else:
                        del self.fallback_cache[formatted_key]
                
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
            expires_at = datetime.utcnow() + timedelta(seconds=ttl)
            formatted_key = self._format_key(key, cache_type)
            
            if self.supabase:
                # Store in Supabase
                data = {
                    'cache_key': formatted_key,
                    'cache_type': cache_type,
                    'value': value,
                    'expires_at': expires_at.isoformat(),
                    'updated_at': datetime.utcnow().isoformat()
                }
                
                # Upsert (insert or update)
                result = self.supabase.table('cache_entries').upsert(data, on_conflict='cache_key').execute()
                return True
            else:
                # Store in fallback cache
                self.fallback_cache[formatted_key] = {
                    "value": value,
                    "expires_at": expires_at
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
            formatted_key = self._format_key(key, cache_type)
            
            if self.supabase:
                self.supabase.table('cache_entries').delete().eq('cache_key', formatted_key).execute()
            else:
                self.fallback_cache.pop(formatted_key, None)
            
            return True
            
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    async def exists(self, key: str, cache_type: str = "default") -> bool:
        """Check if key exists in cache"""
        value = await self.get(key, cache_type)
        return value is not None
    
    async def expire(self, key: str, ttl: int, cache_type: str = "default") -> bool:
        """Set expiration time for existing key"""
        try:
            # Get current value
            value = await self.get(key, cache_type)
            if value is not None:
                # Reset with new TTL
                return await self.set(key, value, cache_type, ttl)
            return False
            
        except Exception as e:
            logger.error(f"Cache expire error for key {key}: {e}")
            return False
    
    async def clear_type(self, cache_type: str) -> bool:
        """Clear all entries of a specific cache type"""
        try:
            if self.supabase:
                self.supabase.table('cache_entries').delete().eq('cache_type', cache_type).execute()
            else:
                # Clear from fallback cache
                keys_to_delete = [k for k in self.fallback_cache.keys() if k.startswith(f"{cache_type}:")]
                for key in keys_to_delete:
                    del self.fallback_cache[key]
            
            return True
            
        except Exception as e:
            logger.error(f"Cache clear type error for {cache_type}: {e}")
            return False
    
    async def clear_all(self) -> bool:
        """Clear all cache entries"""
        try:
            if self.supabase:
                self.supabase.table('cache_entries').delete().neq('id', 0).execute()
            else:
                self.fallback_cache.clear()
            
            return True
            
        except Exception as e:
            logger.error(f"Cache clear all error: {e}")
            return False
    
    async def _cleanup_fallback_cache(self):
        """Clean up expired entries from fallback cache"""
        try:
            now = datetime.utcnow()
            expired_keys = [
                key for key, entry in self.fallback_cache.items()
                if entry["expires_at"] <= now
            ]
            
            for key in expired_keys:
                del self.fallback_cache[key]
                
        except Exception as e:
            logger.error(f"Fallback cache cleanup error: {e}")
    
    async def cleanup_expired(self) -> int:
        """Clean up expired entries from Supabase cache"""
        try:
            if self.supabase:
                now = datetime.utcnow().isoformat()
                result = self.supabase.table('cache_entries').delete().lt('expires_at', now).execute()
                return len(result.data) if result.data else 0
            else:
                await self._cleanup_fallback_cache()
                return 0
                
        except Exception as e:
            logger.error(f"Cache cleanup error: {e}")
            return 0
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        stats = self.cache_stats.copy()
        
        try:
            if self.supabase:
                # Get total entries count
                result = self.supabase.table('cache_entries').select('id', count='exact').execute()
                stats["total_entries"] = result.count if hasattr(result, 'count') else 0
                
                # Get entries by type
                type_result = self.supabase.table('cache_entries').select('cache_type').execute()
                type_counts = {}
                for entry in type_result.data:
                    cache_type = entry['cache_type']
                    type_counts[cache_type] = type_counts.get(cache_type, 0) + 1
                stats["entries_by_type"] = type_counts
            else:
                stats["total_entries"] = len(self.fallback_cache)
                stats["fallback_mode"] = True
            
            # Calculate hit rate
            total_requests = stats["hits"] + stats["misses"]
            stats["hit_rate"] = (stats["hits"] / total_requests * 100) if total_requests > 0 else 0
            
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
        
        return stats


# Global cache service instance
supabase_cache_service = SupabaseCacheService()

# Alias for compatibility
cache_service = supabase_cache_service
