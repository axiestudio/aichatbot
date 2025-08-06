"""
Railway Startup Setup Script
Automatically creates super admin and default instance on Railway deployment
"""

import asyncio
import logging
import uuid
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.auth import auth_service
from ..models.database import SuperAdmin, ChatInstance, InstanceAdmin, LiveConfiguration
from ..core.config import settings

logger = logging.getLogger(__name__)


async def setup_railway_super_admin():
    """Setup Railway super admin with predefined credentials"""
    try:
        db = next(get_db())
        
        # Check if Railway admin already exists
        existing_admin = db.query(SuperAdmin).filter(
            SuperAdmin.email == "stefan@axiestudio.se"
        ).first()
        
        if existing_admin:
            logger.info("Railway super admin already exists")
            return existing_admin
        
        # Create Railway super admin
        railway_admin = SuperAdmin(
            id=str(uuid.uuid4()),
            email="stefan@axiestudio.se",
            name="Stefan - Railway Super Admin",
            password_hash=auth_service.hash_password("STEfanjohn!12"),
            can_create_instances=True,
            can_delete_instances=True,
            can_manage_billing=True,
            can_view_all_analytics=True
        )
        
        db.add(railway_admin)
        db.commit()
        db.refresh(railway_admin)
        
        logger.info(f"Created Railway super admin: {railway_admin.email}")
        return railway_admin
        
    except Exception as e:
        logger.error(f"Error setting up Railway super admin: {e}")
        return None


async def setup_default_instance():
    """Setup default chat instance for Railway deployment"""
    try:
        db = next(get_db())
        
        # Check if default instance already exists
        existing_instance = db.query(ChatInstance).filter(
            ChatInstance.subdomain == "default"
        ).first()
        
        if existing_instance:
            logger.info("Default instance already exists")
            return existing_instance
        
        # Create default instance
        default_instance = ChatInstance(
            id=str(uuid.uuid4()),
            name="Default Chat Instance",
            subdomain="default",
            description="Default chat instance for Railway deployment",
            owner_email="stefan@axiestudio.se",
            owner_name="Stefan",
            max_monthly_messages=10000,
            plan_type="pro",
            primary_color="#3b82f6",
            secondary_color="#e5e7eb"
        )
        
        db.add(default_instance)
        db.commit()
        db.refresh(default_instance)
        
        # Create instance admin
        instance_admin = InstanceAdmin(
            id=str(uuid.uuid4()),
            instance_id=default_instance.id,
            email="stefan@axiestudio.se",
            name="Stefan",
            password_hash=auth_service.hash_password("STEfanjohn!12"),
            role="admin"
        )
        
        db.add(instance_admin)
        db.commit()
        
        # Create default live configuration
        live_config = LiveConfiguration(
            id=str(uuid.uuid4()),
            instance_id=default_instance.id,
            chat_title="AI Assistant",
            chat_subtitle="Powered by Railway",
            welcome_message="Hello! I'm your AI assistant. How can I help you today?",
            placeholder_text="Type your message here...",
            primary_color="#3b82f6",
            secondary_color="#e5e7eb",
            accent_color="#10b981",
            background_color="#ffffff",
            text_color="#1f2937",
            company_name="Railway Demo",
            show_branding=True,
            typing_indicator=True,
            sound_enabled=False,
            auto_scroll=True,
            message_timestamps=True,
            file_upload_enabled=True,
            max_file_size_mb=10,
            allowed_file_types=["pdf", "txt", "docx", "jpg", "png"],
            messages_per_minute=10,
            messages_per_hour=100,
            conversation_starters=[
                "What can you help me with?",
                "Tell me about your capabilities",
                "How does this chat work?"
            ],
            quick_replies=[
                "Thank you!",
                "That's helpful",
                "Can you explain more?"
            ],
            last_updated_by=instance_admin.id
        )
        
        db.add(live_config)
        db.commit()
        
        logger.info(f"Created default instance: {default_instance.name}")
        logger.info(f"Created instance admin: {instance_admin.email}")
        logger.info(f"Created live configuration for instance")
        
        return default_instance
        
    except Exception as e:
        logger.error(f"Error setting up default instance: {e}")
        return None


async def setup_railway_environment():
    """Complete Railway environment setup"""
    logger.info("Starting Railway environment setup...")
    
    try:
        # Setup super admin
        super_admin = await setup_railway_super_admin()
        if not super_admin:
            logger.error("Failed to setup super admin")
            return False
        
        # Setup default instance
        instance = await setup_default_instance()
        if not instance:
            logger.error("Failed to setup default instance")
            return False
        
        logger.info("✅ Railway environment setup completed successfully!")
        logger.info("🚀 Super Admin Login:")
        logger.info("   Email: stefan@axiestudio.se")
        logger.info("   Password: STEfanjohn!12")
        logger.info("   URL: /super-admin/login")
        logger.info("")
        logger.info("🎯 Instance Admin Login:")
        logger.info("   Email: stefan@axiestudio.se")
        logger.info("   Password: STEfanjohn!12")
        logger.info("   URL: /admin/login")
        logger.info("")
        logger.info("💬 Chat Interface:")
        logger.info("   URL: /")
        
        return True
        
    except Exception as e:
        logger.error(f"Railway environment setup failed: {e}")
        return False


def run_railway_setup():
    """Run Railway setup synchronously"""
    return asyncio.run(setup_railway_environment())
