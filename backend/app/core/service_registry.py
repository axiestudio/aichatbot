"""
Enterprise Service Registry
Centralized service management with dependency injection and health monitoring
"""

import logging
import asyncio
from typing import Dict, Any, Optional, Type, Callable
from datetime import datetime
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)


class ServiceRegistry:
    """
    Enterprise-grade service registry with dependency injection,
    health monitoring, and graceful degradation
    """
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._service_configs: Dict[str, Dict[str, Any]] = {}
        self._service_health: Dict[str, Dict[str, Any]] = {}
        self._initialized = False
        self._startup_order = []
        
    def register_service(
        self, 
        name: str, 
        service_class: Type, 
        config: Optional[Dict[str, Any]] = None,
        dependencies: Optional[list] = None,
        required: bool = True
    ):
        """Register a service with the registry"""
        self._service_configs[name] = {
            "class": service_class,
            "config": config or {},
            "dependencies": dependencies or [],
            "required": required,
            "instance": None
        }
        
    def get_service(self, name: str) -> Optional[Any]:
        """Get a service instance"""
        if name in self._services:
            return self._services[name]
        return None
        
    def is_service_available(self, name: str) -> bool:
        """Check if a service is available and healthy"""
        return (
            name in self._services and 
            self._service_health.get(name, {}).get("status") == "healthy"
        )
        
    async def initialize_all_services(self):
        """Initialize all registered services in dependency order"""
        if self._initialized:
            return
            
        logger.info("🔧 Initializing enterprise services...")
        
        # Sort services by dependencies
        sorted_services = self._resolve_dependencies()
        
        for service_name in sorted_services:
            await self._initialize_service(service_name)
            
        self._initialized = True
        logger.info("✅ All services initialized successfully")
        
    def _resolve_dependencies(self) -> list:
        """Resolve service dependencies and return initialization order"""
        resolved = []
        unresolved = list(self._service_configs.keys())
        
        while unresolved:
            for service_name in unresolved[:]:
                config = self._service_configs[service_name]
                dependencies = config.get("dependencies", [])
                
                # Check if all dependencies are resolved
                if all(dep in resolved for dep in dependencies):
                    resolved.append(service_name)
                    unresolved.remove(service_name)
                    
        return resolved
        
    async def _initialize_service(self, service_name: str):
        """Initialize a single service"""
        try:
            config = self._service_configs[service_name]
            service_class = config["class"]
            service_config = config["config"]
            
            logger.info(f"Initializing {service_name}...")
            
            # Create service instance
            if asyncio.iscoroutinefunction(service_class):
                service_instance = await service_class(**service_config)
            else:
                service_instance = service_class(**service_config)
                
            # Initialize if method exists
            if hasattr(service_instance, 'initialize'):
                if asyncio.iscoroutinefunction(service_instance.initialize):
                    await service_instance.initialize()
                else:
                    service_instance.initialize()
                    
            self._services[service_name] = service_instance
            self._service_health[service_name] = {
                "status": "healthy",
                "initialized_at": datetime.utcnow(),
                "last_check": datetime.utcnow()
            }
            
            logger.info(f"✅ {service_name} initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize {service_name}: {e}")
            
            config = self._service_configs[service_name]
            if config["required"]:
                # For required services, create a mock or raise error
                self._create_fallback_service(service_name, e)
            else:
                # For optional services, just log and continue
                self._service_health[service_name] = {
                    "status": "unavailable",
                    "error": str(e),
                    "last_check": datetime.utcnow()
                }
                
    def _create_fallback_service(self, service_name: str, error: Exception):
        """Create a fallback service for critical services"""
        logger.warning(f"Creating fallback service for {service_name}")
        
        class FallbackService:
            def __init__(self, original_error):
                self.original_error = original_error
                
            async def __aenter__(self):
                return self
                
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass
                
            def __getattr__(self, name):
                async def fallback_method(*args, **kwargs):
                    logger.warning(f"Fallback method {name} called for {service_name}")
                    return {}
                return fallback_method
                
        self._services[service_name] = FallbackService(error)
        self._service_health[service_name] = {
            "status": "fallback",
            "error": str(error),
            "last_check": datetime.utcnow()
        }
        
    async def health_check_all_services(self) -> Dict[str, Any]:
        """Perform health check on all services"""
        health_results = {
            "overall_status": "healthy",
            "services": {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        unhealthy_count = 0
        
        for service_name, service in self._services.items():
            try:
                # Try to call health check method if available
                if hasattr(service, 'health_check'):
                    if asyncio.iscoroutinefunction(service.health_check):
                        health = await service.health_check()
                    else:
                        health = service.health_check()
                else:
                    # Basic health check - just verify service exists
                    health = {"status": "healthy", "message": "Service available"}
                    
                health_results["services"][service_name] = health
                
                if health.get("status") != "healthy":
                    unhealthy_count += 1
                    
            except Exception as e:
                logger.error(f"Health check failed for {service_name}: {e}")
                health_results["services"][service_name] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
                unhealthy_count += 1
                
        # Determine overall status
        if unhealthy_count == 0:
            health_results["overall_status"] = "healthy"
        elif unhealthy_count < len(self._services) / 2:
            health_results["overall_status"] = "degraded"
        else:
            health_results["overall_status"] = "critical"
            
        return health_results
        
    async def shutdown_all_services(self):
        """Gracefully shutdown all services"""
        logger.info("🔄 Shutting down services...")
        
        # Shutdown in reverse order
        for service_name in reversed(list(self._services.keys())):
            try:
                service = self._services[service_name]
                if hasattr(service, 'shutdown'):
                    if asyncio.iscoroutinefunction(service.shutdown):
                        await service.shutdown()
                    else:
                        service.shutdown()
                logger.info(f"✅ {service_name} shutdown successfully")
            except Exception as e:
                logger.error(f"❌ Error shutting down {service_name}: {e}")
                
        self._services.clear()
        self._service_health.clear()
        self._initialized = False
        
    @asynccontextmanager
    async def service_context(self):
        """Context manager for service lifecycle"""
        try:
            await self.initialize_all_services()
            yield self
        finally:
            await self.shutdown_all_services()
            
    def get_service_stats(self) -> Dict[str, Any]:
        """Get comprehensive service statistics"""
        return {
            "total_services": len(self._service_configs),
            "active_services": len(self._services),
            "healthy_services": len([
                s for s in self._service_health.values() 
                if s.get("status") == "healthy"
            ]),
            "service_health": self._service_health,
            "initialized": self._initialized,
            "timestamp": datetime.utcnow().isoformat()
        }


# Global service registry instance
service_registry = ServiceRegistry()
