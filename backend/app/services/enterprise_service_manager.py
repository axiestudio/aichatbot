"""
Enterprise Service Manager - Centralized service orchestration and management
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from contextlib import asynccontextmanager

# Import services with fallbacks
try:
    from app.services.unified_chat_service import unified_chat_service
    CHAT_SERVICE_AVAILABLE = True
except ImportError:
    CHAT_SERVICE_AVAILABLE = False
    unified_chat_service = None

try:
    from app.services.cache_service import cache_service
    CACHE_SERVICE_AVAILABLE = True
except ImportError:
    CACHE_SERVICE_AVAILABLE = False
    cache_service = None

try:
    from app.services.health_service import health_service
    HEALTH_SERVICE_AVAILABLE = True
except ImportError:
    HEALTH_SERVICE_AVAILABLE = False
    health_service = None

from app.core.config import settings

logger = logging.getLogger(__name__)


class EnterpriseServiceManager:
    """
    Simplified service manager for production deployment
    Only manages available services with fallbacks
    """

    def __init__(self):
        self.services = {}
        self.service_health = {}
        self._register_available_services()

    def _register_available_services(self):
        """Register only available services"""
        if CHAT_SERVICE_AVAILABLE:
            self.services["unified_chat_service"] = unified_chat_service
        if CACHE_SERVICE_AVAILABLE:
            self.services["cache_service"] = cache_service
        if HEALTH_SERVICE_AVAILABLE:
            self.services["health_service"] = health_service
    
    async def initialize_all_services(self):
        """Initialize available services"""
        logger.info("🔧 Initializing available services...")

        for service_name, service in self.services.items():
            try:
                logger.info(f"Initializing {service_name}...")

                # Simple initialization - just check if service has initialize method
                if hasattr(service, 'initialize'):
                    await service.initialize()

                self.service_health[service_name] = {
                    "status": "healthy",
                    "last_check": datetime.utcnow(),
                    "initialized_at": datetime.utcnow()
                }

                logger.info(f"✅ {service_name} initialized successfully")

            except Exception as e:
                logger.error(f"❌ Failed to initialize {service_name}: {str(e)}")
                self.service_health[service_name] = {
                    "status": "error",
                    "last_check": datetime.utcnow(),
                    "error": str(e)
                }

        logger.info("✅ Available services initialization completed")
    
    async def shutdown_all_services(self):
        """Gracefully shutdown all services"""
        logger.info("🛑 Shutting down services...")

        for service_name, service in self.services.items():
            try:
                if hasattr(service, 'shutdown'):
                    await service.shutdown()
                logger.info(f"✅ {service_name} shutdown completed")
            except Exception as e:
                logger.error(f"❌ Error shutting down {service_name}: {str(e)}")

        logger.info("✅ All services shutdown completed")
    
    async def health_check_all_services(self) -> Dict[str, Any]:
        """Perform simple health check on all services"""
        health_status = {
            "overall_status": "healthy",
            "services": {},
            "timestamp": datetime.utcnow().isoformat()
        }

        for service_name, service in self.services.items():
            try:
                # Simple health check
                if hasattr(service, 'health_check'):
                    await service.health_check()

                health_status["services"][service_name] = {
                    "status": "healthy",
                    "last_check": datetime.utcnow().isoformat()
                }

            except Exception as e:
                health_status["services"][service_name] = {
                    "status": "unhealthy",
                    "error": str(e),
                    "last_check": datetime.utcnow().isoformat()
                }

        return health_status
    
    def get_service_metrics(self) -> Dict[str, Any]:
        """Get basic metrics from all services"""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "services": list(self.services.keys()),
            "service_count": len(self.services)
        }
    
    @asynccontextmanager
    async def service_context(self):
        """Context manager for service lifecycle"""
        try:
            await self.initialize_all_services()
            yield self
        finally:
            await self.shutdown_all_services()


# Global enterprise service manager instance
enterprise_service_manager = EnterpriseServiceManager()
