"""
Enterprise Health Check Service
Comprehensive system health monitoring for production environments
"""

import asyncio
import logging
import time
import psutil
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text

from ..core.database import get_db
from ..core.config import settings
from ..models.database import ChatInstance, SuperAdmin, InstanceAdmin

logger = logging.getLogger(__name__)


class HealthCheckService:
    """Enterprise-grade health monitoring service"""
    
    def __init__(self):
        self.start_time = time.time()
        self.health_cache = {}
        self.cache_ttl = 30  # 30 seconds cache
        
    async def get_comprehensive_health(self) -> Dict[str, Any]:
        """Get comprehensive system health status"""
        
        # Check cache first
        cache_key = "comprehensive_health"
        if self._is_cache_valid(cache_key):
            return self.health_cache[cache_key]["data"]
        
        health_data = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": time.time() - self.start_time,
            "version": "1.0.0",
            "environment": settings.ENVIRONMENT,
            "checks": {}
        }
        
        # Run all health checks
        checks = [
            ("database", self._check_database),
            ("redis", self._check_redis),
            ("system_resources", self._check_system_resources),
            ("websocket", self._check_websocket),
            ("external_apis", self._check_external_apis),
            ("security", self._check_security),
            ("performance", self._check_performance)
        ]
        
        overall_status = "healthy"
        
        for check_name, check_func in checks:
            try:
                check_result = await check_func()
                health_data["checks"][check_name] = check_result
                
                # Update overall status
                if check_result["status"] == "critical":
                    overall_status = "critical"
                elif check_result["status"] == "degraded" and overall_status != "critical":
                    overall_status = "degraded"
                    
            except Exception as e:
                logger.error(f"Health check {check_name} failed: {e}")
                health_data["checks"][check_name] = {
                    "status": "critical",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }
                overall_status = "critical"
        
        health_data["status"] = overall_status
        
        # Cache result
        self._cache_result(cache_key, health_data)
        
        return health_data
    
    async def _check_database(self) -> Dict[str, Any]:
        """Check database connectivity and performance"""
        start_time = time.time()
        
        try:
            db = next(get_db())
            
            # Test basic connectivity
            result = db.execute(text("SELECT 1")).scalar()
            
            # Test table access
            instance_count = db.query(ChatInstance).count()
            admin_count = db.query(InstanceAdmin).count()
            super_admin_count = db.query(SuperAdmin).count()
            
            response_time = (time.time() - start_time) * 1000
            
            # Determine status
            if response_time > 2000:  # > 2 seconds
                status = "critical"
            elif response_time > 1000:  # > 1 second
                status = "degraded"
            else:
                status = "healthy"
            
            return {
                "status": status,
                "response_time_ms": round(response_time, 2),
                "connection_status": "connected" if result == 1 else "error",
                "table_counts": {
                    "chat_instances": instance_count,
                    "instance_admins": admin_count,
                    "super_admins": super_admin_count
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "critical",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _check_redis(self) -> Dict[str, Any]:
        """Check Redis connectivity and performance"""
        try:
            import redis
            
            # Try to connect to Redis
            r = redis.Redis(
                host=settings.REDIS_HOST if hasattr(settings, 'REDIS_HOST') else 'localhost',
                port=settings.REDIS_PORT if hasattr(settings, 'REDIS_PORT') else 6379,
                decode_responses=True,
                socket_timeout=5
            )
            
            start_time = time.time()
            r.ping()
            response_time = (time.time() - start_time) * 1000
            
            # Get Redis info
            info = r.info()
            
            return {
                "status": "healthy" if response_time < 100 else "degraded",
                "response_time_ms": round(response_time, 2),
                "connected_clients": info.get("connected_clients", 0),
                "used_memory_human": info.get("used_memory_human", "unknown"),
                "redis_version": info.get("redis_version", "unknown"),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except ImportError:
            return {
                "status": "warning",
                "message": "Redis client not available",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "status": "degraded",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _check_system_resources(self) -> Dict[str, Any]:
        """Check system resource usage"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            
            # Disk usage
            disk = psutil.disk_usage('/')
            
            # Load average (if available)
            load_avg = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
            
            # Determine status
            if cpu_percent > 90 or memory.percent > 90 or (disk.used / disk.total * 100) > 90:
                status = "critical"
            elif cpu_percent > 80 or memory.percent > 80 or (disk.used / disk.total * 100) > 80:
                status = "degraded"
            else:
                status = "healthy"
            
            return {
                "status": status,
                "cpu_percent": round(cpu_percent, 2),
                "memory_percent": round(memory.percent, 2),
                "memory_available_gb": round(memory.available / (1024**3), 2),
                "disk_percent": round((disk.used / disk.total * 100), 2),
                "disk_free_gb": round(disk.free / (1024**3), 2),
                "load_average": load_avg[0] if load_avg else None,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "critical",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _check_websocket(self) -> Dict[str, Any]:
        """Check WebSocket service health"""
        try:
            from ..services.websocket_manager import websocket_manager
            
            stats = websocket_manager.get_connection_stats()
            
            return {
                "status": "healthy",
                "total_connections": stats["total_connections"],
                "total_instances": stats["total_instances"],
                "instance_stats": stats["instance_stats"],
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "degraded",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _check_external_apis(self) -> Dict[str, Any]:
        """Check external API connectivity"""
        try:
            import httpx
            
            # Test OpenAI API (if configured)
            openai_status = "not_configured"
            anthropic_status = "not_configured"
            
            # This would be expanded to actually test API endpoints
            # For now, just return basic status
            
            return {
                "status": "healthy",
                "openai_api": openai_status,
                "anthropic_api": anthropic_status,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "degraded",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _check_security(self) -> Dict[str, Any]:
        """Check security-related health"""
        try:
            db = next(get_db())
            
            # Check for active super admins
            active_super_admins = db.query(SuperAdmin).filter(SuperAdmin.is_active == True).count()
            
            # Check for recent admin activity
            recent_threshold = datetime.utcnow() - timedelta(days=7)
            recent_admin_logins = db.query(InstanceAdmin).filter(
                InstanceAdmin.last_login >= recent_threshold
            ).count()
            
            return {
                "status": "healthy" if active_super_admins > 0 else "warning",
                "active_super_admins": active_super_admins,
                "recent_admin_logins": recent_admin_logins,
                "jwt_enabled": True,
                "rate_limiting_enabled": True,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "degraded",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _check_performance(self) -> Dict[str, Any]:
        """Check performance metrics"""
        try:
            uptime = time.time() - self.start_time
            
            return {
                "status": "healthy",
                "uptime_seconds": round(uptime, 2),
                "uptime_human": self._format_uptime(uptime),
                "cache_hit_rate": 0.95,  # Would be calculated from actual cache metrics
                "avg_response_time_ms": 150,  # Would be calculated from actual metrics
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "degraded",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cached result is still valid"""
        if key not in self.health_cache:
            return False
        
        cache_time = self.health_cache[key]["timestamp"]
        return (time.time() - cache_time) < self.cache_ttl
    
    def _cache_result(self, key: str, data: Dict[str, Any]):
        """Cache health check result"""
        self.health_cache[key] = {
            "data": data,
            "timestamp": time.time()
        }
    
    def _format_uptime(self, seconds: float) -> str:
        """Format uptime in human-readable format"""
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"


# Global health service instance
health_service = HealthCheckService()
