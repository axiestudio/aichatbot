"""
Enterprise Rate Limiting Service
Advanced rate limiting with Redis backend and intelligent throttling
"""

import time
import logging
import hashlib
from typing import Dict, Optional, Tuple, List
from datetime import datetime, timedelta
from fastapi import Request, HTTPException, status

from .cache_service import cache_service
from ..core.config import settings

logger = logging.getLogger(__name__)


class RateLimitService:
    """Enterprise-grade rate limiting service"""
    
    def __init__(self):
        self.rate_limits = {
            # API endpoints
            "api_general": {"requests": 100, "window": 60},      # 100 req/min
            "api_chat": {"requests": 30, "window": 60},          # 30 chat req/min
            "api_admin": {"requests": 200, "window": 60},        # 200 admin req/min
            "api_super_admin": {"requests": 500, "window": 60},  # 500 super admin req/min
            
            # Authentication
            "auth_login": {"requests": 5, "window": 300},        # 5 login attempts per 5 min
            "auth_failed": {"requests": 3, "window": 900},       # 3 failed attempts per 15 min
            
            # WebSocket connections
            "websocket_connect": {"requests": 10, "window": 60}, # 10 connections per min
            
            # File uploads
            "file_upload": {"requests": 10, "window": 300},      # 10 uploads per 5 min
            
            # Configuration changes
            "config_update": {"requests": 20, "window": 60},     # 20 config updates per min
            
            # Instance-specific limits
            "instance_messages": {"requests": 100, "window": 3600}, # 100 messages per hour per instance
        }
        
        # Whitelist for IPs that bypass rate limiting
        self.whitelist = set(getattr(settings, 'RATE_LIMIT_WHITELIST', []))
        
        # Blacklist for IPs that are completely blocked
        self.blacklist = set()
        
        # Adaptive rate limiting
        self.adaptive_limits = {}
    
    async def check_rate_limit(
        self, 
        request: Request, 
        limit_type: str = "api_general",
        identifier: Optional[str] = None,
        custom_limit: Optional[Dict] = None
    ) -> Tuple[bool, Dict[str, any]]:
        """
        Check if request is within rate limits
        Returns: (is_allowed, rate_limit_info)
        """
        
        # Get client identifier
        client_id = identifier or self._get_client_identifier(request)
        
        # Check whitelist
        if self._is_whitelisted(client_id, request):
            return True, {"status": "whitelisted"}
        
        # Check blacklist
        if self._is_blacklisted(client_id):
            return False, {
                "status": "blacklisted",
                "error": "IP address is blacklisted"
            }
        
        # Get rate limit configuration
        limit_config = custom_limit or self.rate_limits.get(limit_type, self.rate_limits["api_general"])
        
        # Apply adaptive rate limiting
        limit_config = self._apply_adaptive_limits(client_id, limit_config)
        
        # Check rate limit
        cache_key = f"rate_limit:{limit_type}:{client_id}"
        
        try:
            # Get current count
            current_count = await cache_service.get(cache_key, "rate_limit") or 0
            
            # Check if limit exceeded
            if current_count >= limit_config["requests"]:
                # Log rate limit violation
                logger.warning(f"Rate limit exceeded for {client_id} on {limit_type}: {current_count}/{limit_config['requests']}")
                
                # Update adaptive limits for repeat offenders
                await self._update_adaptive_limits(client_id, limit_type)
                
                return False, {
                    "status": "rate_limited",
                    "limit": limit_config["requests"],
                    "window": limit_config["window"],
                    "current": current_count,
                    "reset_time": time.time() + limit_config["window"]
                }
            
            # Increment counter
            if current_count == 0:
                # First request in window
                await cache_service.set(cache_key, 1, "rate_limit", limit_config["window"])
            else:
                # Increment existing counter
                await cache_service.increment(cache_key, "rate_limit")
            
            return True, {
                "status": "allowed",
                "limit": limit_config["requests"],
                "window": limit_config["window"],
                "current": current_count + 1,
                "remaining": limit_config["requests"] - current_count - 1
            }
            
        except Exception as e:
            logger.error(f"Rate limit check error: {e}")
            # On error, allow request but log it
            return True, {"status": "error", "error": str(e)}
    
    async def record_failed_attempt(self, request: Request, attempt_type: str = "auth_failed"):
        """Record a failed attempt (login, etc.)"""
        client_id = self._get_client_identifier(request)
        cache_key = f"failed_attempts:{attempt_type}:{client_id}"
        
        try:
            current_count = await cache_service.get(cache_key, "rate_limit") or 0
            new_count = current_count + 1
            
            # Store with 15-minute TTL
            await cache_service.set(cache_key, new_count, "rate_limit", 900)
            
            # Auto-blacklist after too many failed attempts
            if new_count >= 10:  # 10 failed attempts
                await self.add_to_blacklist(client_id, duration=3600)  # 1 hour blacklist
                logger.warning(f"Auto-blacklisted {client_id} for {new_count} failed attempts")
            
        except Exception as e:
            logger.error(f"Failed to record failed attempt: {e}")
    
    async def add_to_blacklist(self, identifier: str, duration: int = 3600):
        """Add identifier to blacklist for specified duration"""
        cache_key = f"blacklist:{identifier}"
        await cache_service.set(cache_key, True, "rate_limit", duration)
        self.blacklist.add(identifier)
        logger.info(f"Added {identifier} to blacklist for {duration} seconds")
    
    async def remove_from_blacklist(self, identifier: str):
        """Remove identifier from blacklist"""
        cache_key = f"blacklist:{identifier}"
        await cache_service.delete(cache_key, "rate_limit")
        self.blacklist.discard(identifier)
        logger.info(f"Removed {identifier} from blacklist")
    
    async def get_rate_limit_status(self, request: Request, limit_type: str = "api_general") -> Dict:
        """Get current rate limit status for client"""
        client_id = self._get_client_identifier(request)
        cache_key = f"rate_limit:{limit_type}:{client_id}"
        
        limit_config = self.rate_limits.get(limit_type, self.rate_limits["api_general"])
        current_count = await cache_service.get(cache_key, "rate_limit") or 0
        
        return {
            "client_id": client_id,
            "limit_type": limit_type,
            "limit": limit_config["requests"],
            "window": limit_config["window"],
            "current": current_count,
            "remaining": max(0, limit_config["requests"] - current_count),
            "is_whitelisted": self._is_whitelisted(client_id, request),
            "is_blacklisted": self._is_blacklisted(client_id)
        }
    
    async def clear_rate_limit(self, identifier: str, limit_type: str = None):
        """Clear rate limit for specific identifier"""
        if limit_type:
            cache_key = f"rate_limit:{limit_type}:{identifier}"
            await cache_service.delete(cache_key, "rate_limit")
        else:
            # Clear all rate limits for this identifier
            pattern = f"rate_limit:*:{identifier}"
            await cache_service.clear_pattern(pattern, "rate_limit")
    
    def _get_client_identifier(self, request: Request) -> str:
        """Get unique client identifier"""
        # Try to get real IP from headers (for reverse proxy setups)
        real_ip = (
            request.headers.get("X-Forwarded-For", "").split(",")[0].strip() or
            request.headers.get("X-Real-IP") or
            request.headers.get("CF-Connecting-IP") or  # Cloudflare
            getattr(request.client, "host", "unknown")
        )
        
        # For authenticated requests, also consider user ID
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            return f"{real_ip}:{user_id}"
        
        return real_ip
    
    def _is_whitelisted(self, client_id: str, request: Request) -> bool:
        """Check if client is whitelisted"""
        # Check IP whitelist
        ip = client_id.split(":")[0]
        if ip in self.whitelist:
            return True
        
        # Check for localhost/development
        if ip in ["127.0.0.1", "localhost", "::1"]:
            return getattr(settings, 'ENVIRONMENT', 'production') != 'production'
        
        # Check for internal service calls
        user_agent = request.headers.get("User-Agent", "")
        if "internal-service" in user_agent.lower():
            return True
        
        return False
    
    def _is_blacklisted(self, client_id: str) -> bool:
        """Check if client is blacklisted"""
        ip = client_id.split(":")[0]
        return ip in self.blacklist
    
    def _apply_adaptive_limits(self, client_id: str, base_limit: Dict) -> Dict:
        """Apply adaptive rate limiting based on client behavior"""
        if client_id in self.adaptive_limits:
            adaptive_factor = self.adaptive_limits[client_id].get("factor", 1.0)
            
            # Reduce limits for problematic clients
            if adaptive_factor < 1.0:
                return {
                    "requests": int(base_limit["requests"] * adaptive_factor),
                    "window": base_limit["window"]
                }
        
        return base_limit
    
    async def _update_adaptive_limits(self, client_id: str, limit_type: str):
        """Update adaptive limits for repeat offenders"""
        if client_id not in self.adaptive_limits:
            self.adaptive_limits[client_id] = {"violations": 0, "factor": 1.0}
        
        self.adaptive_limits[client_id]["violations"] += 1
        violations = self.adaptive_limits[client_id]["violations"]
        
        # Reduce rate limits for repeat offenders
        if violations >= 5:
            self.adaptive_limits[client_id]["factor"] = 0.5  # 50% of normal limits
        elif violations >= 3:
            self.adaptive_limits[client_id]["factor"] = 0.75  # 75% of normal limits
        
        # Store in cache for persistence
        cache_key = f"adaptive_limits:{client_id}"
        await cache_service.set(cache_key, self.adaptive_limits[client_id], "rate_limit", 3600)
    
    async def get_statistics(self) -> Dict:
        """Get rate limiting statistics"""
        stats = cache_service.get_stats()
        
        return {
            "cache_stats": stats,
            "rate_limits_configured": len(self.rate_limits),
            "whitelisted_ips": len(self.whitelist),
            "blacklisted_ips": len(self.blacklist),
            "adaptive_limits_active": len(self.adaptive_limits),
            "rate_limit_types": list(self.rate_limits.keys())
        }


# Global rate limit service instance
rate_limit_service = RateLimitService()
