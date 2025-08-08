"""
Enterprise Tenant Manager - Advanced multi-tenant management and isolation
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from ..core.database import get_db
from ..models.database import ChatInstance, InstanceAdmin, LiveConfiguration, Message, Conversation
from ..services.cache_service import cache_service
from ..services.performance_service import performance_service

logger = logging.getLogger(__name__)


@dataclass
class TenantQuota:
    """Tenant resource quota configuration"""
    max_monthly_messages: int
    max_concurrent_sessions: int
    max_storage_mb: int
    max_admins: int
    max_configurations: int
    api_rate_limit: int  # requests per minute
    features_enabled: Set[str]


@dataclass
class TenantUsage:
    """Current tenant resource usage"""
    monthly_messages: int
    concurrent_sessions: int
    storage_used_mb: float
    admin_count: int
    configuration_count: int
    last_activity: datetime


class TenantManager:
    """
    Enterprise tenant manager with advanced isolation and resource management
    """
    
    def __init__(self):
        self.tenant_cache = {}
        self.usage_cache = {}
        self.quota_cache = {}
        self.active_sessions = {}  # tenant_id -> session_count
        
    async def initialize(self):
        """Initialize tenant manager"""
        logger.info("🏢 Initializing Enterprise Tenant Manager...")
        await self._load_tenant_configurations()
        await self._start_usage_monitoring()
        logger.info("✅ Tenant Manager initialized")
    
    async def _load_tenant_configurations(self):
        """Load all tenant configurations into cache"""
        try:
            db = next(get_db())
            instances = db.query(ChatInstance).filter(ChatInstance.is_active == True).all()
            
            for instance in instances:
                tenant_info = {
                    "id": instance.id,
                    "subdomain": instance.subdomain,
                    "name": instance.name,
                    "domain": instance.domain,
                    "plan_type": instance.plan_type,
                    "is_active": instance.is_active,
                    "owner_email": instance.owner_email,
                    "created_at": instance.created_at,
                    "settings": instance.settings or {}
                }
                
                self.tenant_cache[instance.id] = tenant_info
                self.tenant_cache[f"subdomain:{instance.subdomain}"] = tenant_info
                
                # Load quota configuration
                quota = await self._get_tenant_quota(instance.plan_type, instance.settings)
                self.quota_cache[instance.id] = quota
                
            logger.info(f"Loaded {len(instances)} tenant configurations")
            
        except Exception as e:
            logger.error(f"Failed to load tenant configurations: {e}")
    
    async def _get_tenant_quota(self, plan_type: str, settings: Dict[str, Any]) -> TenantQuota:
        """Get tenant quota based on plan type and custom settings"""
        
        # Default quotas by plan type
        plan_quotas = {
            "free": TenantQuota(
                max_monthly_messages=1000,
                max_concurrent_sessions=5,
                max_storage_mb=100,
                max_admins=1,
                max_configurations=1,
                api_rate_limit=60,
                features_enabled={"basic_chat", "basic_customization"}
            ),
            "pro": TenantQuota(
                max_monthly_messages=10000,
                max_concurrent_sessions=50,
                max_storage_mb=1000,
                max_admins=5,
                max_configurations=5,
                api_rate_limit=300,
                features_enabled={"basic_chat", "advanced_customization", "analytics", "file_upload"}
            ),
            "enterprise": TenantQuota(
                max_monthly_messages=100000,
                max_concurrent_sessions=500,
                max_storage_mb=10000,
                max_admins=50,
                max_configurations=50,
                api_rate_limit=1000,
                features_enabled={"all_features", "white_labeling", "sso", "api_access", "webhooks"}
            )
        }
        
        base_quota = plan_quotas.get(plan_type, plan_quotas["free"])
        
        # Apply custom overrides from settings
        if "custom_quota" in settings:
            custom = settings["custom_quota"]
            for field in ["max_monthly_messages", "max_concurrent_sessions", "max_storage_mb", 
                         "max_admins", "max_configurations", "api_rate_limit"]:
                if field in custom:
                    setattr(base_quota, field, custom[field])
        
        return base_quota
    
    async def get_tenant_by_subdomain(self, subdomain: str) -> Optional[Dict[str, Any]]:
        """Get tenant information by subdomain with caching"""
        cache_key = f"subdomain:{subdomain}"
        
        if cache_key in self.tenant_cache:
            return self.tenant_cache[cache_key]
        
        # Reload from database if not in cache
        await self._load_tenant_configurations()
        return self.tenant_cache.get(cache_key)
    
    async def get_tenant_by_id(self, tenant_id: str) -> Optional[Dict[str, Any]]:
        """Get tenant information by ID with caching"""
        if tenant_id in self.tenant_cache:
            return self.tenant_cache[tenant_id]
        
        # Reload from database if not in cache
        await self._load_tenant_configurations()
        return self.tenant_cache.get(tenant_id)
    
    async def check_tenant_quota(self, tenant_id: str, resource_type: str, amount: int = 1) -> bool:
        """Check if tenant can use specified amount of resource"""
        try:
            quota = self.quota_cache.get(tenant_id)
            if not quota:
                return False
            
            usage = await self.get_tenant_usage(tenant_id)
            
            # Check specific resource limits
            if resource_type == "messages":
                return usage.monthly_messages + amount <= quota.max_monthly_messages
            elif resource_type == "sessions":
                return usage.concurrent_sessions + amount <= quota.max_concurrent_sessions
            elif resource_type == "storage":
                return usage.storage_used_mb + amount <= quota.max_storage_mb
            elif resource_type == "admins":
                return usage.admin_count + amount <= quota.max_admins
            elif resource_type == "configurations":
                return usage.configuration_count + amount <= quota.max_configurations
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking tenant quota: {e}")
            return False
    
    async def get_tenant_usage(self, tenant_id: str) -> TenantUsage:
        """Get current tenant resource usage"""
        cache_key = f"usage:{tenant_id}"
        
        # Check cache first (5 minute TTL)
        if cache_key in self.usage_cache:
            cached_usage, cached_time = self.usage_cache[cache_key]
            if datetime.utcnow() - cached_time < timedelta(minutes=5):
                return cached_usage
        
        # Calculate usage from database
        try:
            db = next(get_db())
            
            # Get current month's message count
            current_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            monthly_messages = db.query(Message).filter(
                and_(
                    Message.instance_id == tenant_id,
                    Message.created_at >= current_month
                )
            ).count()
            
            # Get concurrent sessions (approximate from recent activity)
            recent_activity = datetime.utcnow() - timedelta(minutes=30)
            concurrent_sessions = db.query(Conversation).filter(
                and_(
                    Conversation.instance_id == tenant_id,
                    Conversation.last_message_at >= recent_activity
                )
            ).count()
            
            # Get admin count
            admin_count = db.query(InstanceAdmin).filter(
                InstanceAdmin.instance_id == tenant_id
            ).count()
            
            # Get configuration count
            config_count = db.query(LiveConfiguration).filter(
                LiveConfiguration.instance_id == tenant_id
            ).count()
            
            # Calculate storage usage (simplified)
            storage_used_mb = 0.0  # TODO: Implement actual storage calculation
            
            # Get last activity
            last_message = db.query(Message).filter(
                Message.instance_id == tenant_id
            ).order_by(Message.created_at.desc()).first()
            
            last_activity = last_message.created_at if last_message else datetime.utcnow()
            
            usage = TenantUsage(
                monthly_messages=monthly_messages,
                concurrent_sessions=concurrent_sessions,
                storage_used_mb=storage_used_mb,
                admin_count=admin_count,
                configuration_count=config_count,
                last_activity=last_activity
            )
            
            # Cache the result
            self.usage_cache[cache_key] = (usage, datetime.utcnow())
            
            return usage
            
        except Exception as e:
            logger.error(f"Error calculating tenant usage: {e}")
            return TenantUsage(0, 0, 0.0, 0, 0, datetime.utcnow())
    
    async def increment_usage(self, tenant_id: str, resource_type: str, amount: int = 1):
        """Increment tenant resource usage"""
        try:
            # Update database counters
            db = next(get_db())
            instance = db.query(ChatInstance).filter(ChatInstance.id == tenant_id).first()
            
            if instance and resource_type == "messages":
                instance.current_monthly_messages = (instance.current_monthly_messages or 0) + amount
                db.commit()
            
            # Invalidate usage cache
            cache_key = f"usage:{tenant_id}"
            if cache_key in self.usage_cache:
                del self.usage_cache[cache_key]
                
        except Exception as e:
            logger.error(f"Error incrementing tenant usage: {e}")
    
    async def _start_usage_monitoring(self):
        """Start background task for usage monitoring"""
        asyncio.create_task(self._usage_monitoring_loop())
    
    async def _usage_monitoring_loop(self):
        """Background loop for monitoring tenant usage"""
        while True:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes
                
                # Check all tenants for quota violations
                for tenant_id in self.tenant_cache.keys():
                    if not tenant_id.startswith("subdomain:"):
                        await self._check_tenant_limits(tenant_id)
                        
            except Exception as e:
                logger.error(f"Error in usage monitoring loop: {e}")
    
    async def _check_tenant_limits(self, tenant_id: str):
        """Check if tenant is approaching or exceeding limits"""
        try:
            quota = self.quota_cache.get(tenant_id)
            usage = await self.get_tenant_usage(tenant_id)
            
            if not quota:
                return
            
            # Check for quota violations
            violations = []
            
            if usage.monthly_messages >= quota.max_monthly_messages:
                violations.append("monthly_messages")
            elif usage.monthly_messages >= quota.max_monthly_messages * 0.9:
                # 90% warning
                await self._send_quota_warning(tenant_id, "monthly_messages", 90)
            
            if usage.concurrent_sessions >= quota.max_concurrent_sessions:
                violations.append("concurrent_sessions")
            
            if violations:
                await self._handle_quota_violation(tenant_id, violations)
                
        except Exception as e:
            logger.error(f"Error checking tenant limits: {e}")
    
    async def _send_quota_warning(self, tenant_id: str, resource: str, percentage: int):
        """Send quota warning to tenant admins"""
        # TODO: Implement notification system
        logger.warning(f"Tenant {tenant_id} at {percentage}% of {resource} quota")
    
    async def _handle_quota_violation(self, tenant_id: str, violations: List[str]):
        """Handle quota violations"""
        # TODO: Implement quota violation handling (throttling, notifications, etc.)
        logger.error(f"Tenant {tenant_id} quota violations: {violations}")


# Global tenant manager instance
tenant_manager = TenantManager()
