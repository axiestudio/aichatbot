"""
Enterprise Service Manager - Centralized service orchestration and management
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from contextlib import asynccontextmanager

from app.services.unified_chat_service import unified_chat_service
from app.services.cache_service import cache_service
from app.services.performance_service import performance_service
from app.services.rate_limit_service import rate_limit_service
from app.services.ai_autoscaling_service import ai_autoscaling_service
from app.services.security_intelligence_service import security_intelligence_service
from app.services.advanced_analytics_service import advanced_analytics_service
from app.services.conversation_intelligence_service import conversation_intelligence_service
from app.services.realtime_collaboration_service import realtime_collaboration_service
from app.services.content_moderation_service import content_moderation_service
from app.services.knowledge_graph_service import knowledge_graph_service
from app.services.error_tracking_service import get_error_tracker
from app.core.config import settings

logger = logging.getLogger(__name__)


class EnterpriseServiceManager:
    """
    Centralized manager for all enterprise services
    Handles initialization, health monitoring, and graceful shutdown
    """
    
    def __init__(self):
        self.services = {}
        self.service_health = {}
        self.initialization_order = [
            "cache_service",
            "performance_service", 
            "rate_limit_service",
            "unified_chat_service",
            "ai_autoscaling_service",
            "security_intelligence_service",
            "advanced_analytics_service",
            "conversation_intelligence_service",
            "realtime_collaboration_service",
            "content_moderation_service",
            "knowledge_graph_service"
        ]
        self._register_services()
    
    def _register_services(self):
        """Register all enterprise services"""
        self.services = {
            "cache_service": cache_service,
            "performance_service": performance_service,
            "rate_limit_service": rate_limit_service,
            "unified_chat_service": unified_chat_service,
            "ai_autoscaling_service": ai_autoscaling_service,
            "security_intelligence_service": security_intelligence_service,
            "advanced_analytics_service": advanced_analytics_service,
            "conversation_intelligence_service": conversation_intelligence_service,
            "realtime_collaboration_service": realtime_collaboration_service,
            "content_moderation_service": content_moderation_service,
            "knowledge_graph_service": knowledge_graph_service
        }
    
    async def initialize_all_services(self):
        """Initialize all services in the correct order"""
        logger.info("🔧 Initializing enterprise services...")
        
        for service_name in self.initialization_order:
            try:
                service = self.services.get(service_name)
                if not service:
                    logger.warning(f"Service {service_name} not found")
                    continue
                
                logger.info(f"Initializing {service_name}...")
                
                # Initialize service based on its interface
                if hasattr(service, 'initialize'):
                    await service.initialize()
                elif hasattr(service, 'start_monitoring'):
                    await service.start_monitoring()
                elif hasattr(service, 'start_ai_scaling'):
                    await service.start_ai_scaling()
                elif hasattr(service, 'start_security_monitoring'):
                    await service.start_security_monitoring()
                elif hasattr(service, 'start_analytics_engine'):
                    await service.start_analytics_engine()
                elif hasattr(service, 'start_intelligence_processing'):
                    await service.start_intelligence_processing()
                elif hasattr(service, 'start_collaboration_engine'):
                    await service.start_collaboration_engine()
                elif hasattr(service, 'start_moderation_engine'):
                    await service.start_moderation_engine()
                elif hasattr(service, 'start_knowledge_processing'):
                    await service.start_knowledge_processing()
                
                self.service_health[service_name] = {
                    "status": "healthy",
                    "last_check": datetime.utcnow(),
                    "initialized_at": datetime.utcnow()
                }
                
                logger.info(f"✅ {service_name} initialized successfully")
                
            except Exception as e:
                logger.error(f"❌ Failed to initialize {service_name}: {str(e)}")
                self.service_health[service_name] = {
                    "status": "failed",
                    "error": str(e),
                    "last_check": datetime.utcnow()
                }
                
                # Continue with other services even if one fails
                continue
        
        logger.info("✅ Enterprise services initialization completed")
    
    async def shutdown_all_services(self):
        """Gracefully shutdown all services"""
        logger.info("🛑 Shutting down enterprise services...")
        
        # Shutdown in reverse order
        for service_name in reversed(self.initialization_order):
            try:
                service = self.services.get(service_name)
                if not service:
                    continue
                
                logger.info(f"Shutting down {service_name}...")
                
                # Shutdown service based on its interface
                if hasattr(service, 'shutdown'):
                    await service.shutdown()
                elif hasattr(service, 'stop_monitoring'):
                    await service.stop_monitoring()
                elif hasattr(service, 'stop_ai_scaling'):
                    await service.stop_ai_scaling()
                elif hasattr(service, 'stop_security_monitoring'):
                    await service.stop_security_monitoring()
                elif hasattr(service, 'stop_analytics_engine'):
                    await service.stop_analytics_engine()
                elif hasattr(service, 'stop_intelligence_processing'):
                    await service.stop_intelligence_processing()
                elif hasattr(service, 'stop_collaboration_engine'):
                    await service.stop_collaboration_engine()
                elif hasattr(service, 'stop_moderation_engine'):
                    await service.stop_moderation_engine()
                elif hasattr(service, 'stop_knowledge_processing'):
                    await service.stop_knowledge_processing()
                
                logger.info(f"✅ {service_name} shutdown completed")
                
            except Exception as e:
                logger.error(f"❌ Error shutting down {service_name}: {str(e)}")
        
        logger.info("✅ All services shutdown completed")
    
    async def health_check_all_services(self) -> Dict[str, Any]:
        """Perform health check on all services"""
        health_status = {
            "overall_status": "healthy",
            "services": {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        failed_services = 0
        
        for service_name, service in self.services.items():
            try:
                # Perform health check based on service interface
                if hasattr(service, 'health_check'):
                    service_health = await service.health_check()
                elif hasattr(service, 'get_stats'):
                    service_health = service.get_stats()
                elif hasattr(service, 'is_healthy'):
                    service_health = {"healthy": service.is_healthy()}
                else:
                    service_health = {"status": "unknown"}
                
                health_status["services"][service_name] = {
                    "status": "healthy",
                    "details": service_health,
                    "last_check": datetime.utcnow().isoformat()
                }
                
            except Exception as e:
                failed_services += 1
                health_status["services"][service_name] = {
                    "status": "unhealthy",
                    "error": str(e),
                    "last_check": datetime.utcnow().isoformat()
                }
        
        # Determine overall status
        if failed_services > 0:
            if failed_services >= len(self.services) / 2:
                health_status["overall_status"] = "critical"
            else:
                health_status["overall_status"] = "degraded"
        
        return health_status
    
    def get_service_metrics(self) -> Dict[str, Any]:
        """Get comprehensive metrics from all services"""
        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "services": {}
        }
        
        for service_name, service in self.services.items():
            try:
                if hasattr(service, 'get_service_stats'):
                    metrics["services"][service_name] = service.get_service_stats()
                elif hasattr(service, 'get_metrics'):
                    metrics["services"][service_name] = service.get_metrics()
                elif hasattr(service, 'get_stats'):
                    metrics["services"][service_name] = service.get_stats()
                else:
                    metrics["services"][service_name] = {"status": "no_metrics"}
                    
            except Exception as e:
                metrics["services"][service_name] = {"error": str(e)}
        
        return metrics
    
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
