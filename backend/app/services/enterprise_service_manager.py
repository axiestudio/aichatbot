"""
Enterprise Service Manager - Centralized service orchestration and management
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from contextlib import asynccontextmanager

from app.core.service_registry import service_registry
from app.core.config import settings

logger = logging.getLogger(__name__)


class EnterpriseServiceManager:
    """
    Enterprise-grade service manager with comprehensive orchestration,
    health monitoring, dependency management, and graceful degradation
    """

    def __init__(self):
        self.service_registry = service_registry
        self._register_core_services()

    def _register_core_services(self):
        """Register all core enterprise services"""
        # Register services with proper dependencies and configurations
        self._register_chat_services()
        self._register_infrastructure_services()
        self._register_monitoring_services()
        self._register_security_services()
        self._register_observability_services()

    def _register_chat_services(self):
        """Register chat-related services"""
        try:
            from app.services.unified_chat_service import UnifiedChatService
            self.service_registry.register_service(
                "unified_chat_service",
                UnifiedChatService,
                dependencies=["cache_service", "database_service"],
                required=True
            )
        except ImportError:
            logger.warning("Unified chat service not available")

        try:
            from app.services.rag_service import RAGService
            self.service_registry.register_service(
                "rag_service",
                RAGService,
                dependencies=["database_service", "embedding_service"],
                required=False
            )
        except ImportError:
            logger.warning("RAG service not available")

    def _register_infrastructure_services(self):
        """Register infrastructure services"""
        try:
            from app.services.cache_service import CacheService
            self.service_registry.register_service(
                "cache_service",
                CacheService,
                required=True
            )
        except ImportError:
            logger.warning("Cache service not available")

        try:
            from app.core.database import DatabaseManager
            self.service_registry.register_service(
                "database_service",
                DatabaseManager,
                required=True
            )
        except ImportError:
            logger.warning("Database service not available")

    def _register_monitoring_services(self):
        """Register monitoring and analytics services"""
        try:
            from app.services.health_service import HealthCheckService
            self.service_registry.register_service(
                "health_service",
                HealthCheckService,
                required=False
            )
        except ImportError:
            logger.warning("Health service not available")

        try:
            from app.services.performance_service import PerformanceService
            self.service_registry.register_service(
                "performance_service",
                PerformanceService,
                required=False
            )
        except ImportError:
            logger.warning("Performance service not available")

    def _register_security_services(self):
        """Register security-related services"""
        try:
            from app.services.rate_limit_service import RateLimitService
            self.service_registry.register_service(
                "rate_limit_service",
                RateLimitService,
                required=False
            )
        except ImportError:
            logger.warning("Rate limit service not available")

        # Register enterprise security services
        try:
            from app.core.zero_trust_security import zero_trust_engine
            self.service_registry.register_service(
                "zero_trust_security",
                lambda: zero_trust_engine,
                required=False
            )
        except ImportError:
            logger.warning("Zero trust security not available")

        try:
            from app.core.chaos_engineering import chaos_monkey
            self.service_registry.register_service(
                "chaos_engineering",
                lambda: chaos_monkey,
                required=False
            )
        except ImportError:
            logger.warning("Chaos engineering not available")

    def _register_observability_services(self):
        """Register observability and analytics services"""
        try:
            from app.core.observability import observability
            self.service_registry.register_service(
                "observability_stack",
                lambda: observability,
                required=False
            )
        except ImportError:
            logger.warning("Observability stack not available")

        try:
            from app.core.event_streaming import event_bus, real_time_analytics
            self.service_registry.register_service(
                "event_bus",
                lambda: event_bus,
                required=False
            )
            self.service_registry.register_service(
                "real_time_analytics",
                lambda: real_time_analytics,
                required=False
            )
        except ImportError:
            logger.warning("Event streaming not available")
    
    async def initialize_all_services(self):
        """Initialize all registered services with proper dependency management"""
        logger.info("🔧 Initializing enterprise services...")
        await self.service_registry.initialize_all_services()
        logger.info("✅ Enterprise service initialization complete")

        logger.info("✅ Available services initialization completed")
    
    async def shutdown_all_services(self):
        """Gracefully shutdown all services"""
        logger.info("🛑 Shutting down enterprise services...")
        await self.service_registry.shutdown_all_services()
        logger.info("✅ Enterprise service shutdown complete")
    
    async def health_check_all_services(self) -> Dict[str, Any]:
        """Comprehensive health check of all services"""
        logger.info("🏥 Performing comprehensive health check...")
        return await self.service_registry.health_check_all_services()
    
    def get_service_metrics(self) -> Dict[str, Any]:
        """Get comprehensive metrics from all services"""
        return self.service_registry.get_service_stats()

    def get_service(self, name: str) -> Optional[Any]:
        """Get a specific service instance"""
        return self.service_registry.get_service(name)

    def is_service_available(self, name: str) -> bool:
        """Check if a service is available and healthy"""
        return self.service_registry.is_service_available(name)
    
    @asynccontextmanager
    async def service_context(self):
        """Context manager for enterprise service lifecycle"""
        try:
            await self.initialize_all_services()
            yield self
        finally:
            await self.shutdown_all_services()


# Global enterprise service manager instance
enterprise_service_manager = EnterpriseServiceManager()
