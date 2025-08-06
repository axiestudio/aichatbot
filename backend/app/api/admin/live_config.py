"""
Live Configuration API - Real-time chat interface configuration
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, validator
import uuid
import json

from ...core.database import get_db
from ...core.auth import get_current_admin_user
from ...models.database import LiveConfiguration, ConfigurationHistory, InstanceAdmin
from ...middleware.multi_tenant import get_current_tenant
from ...services.websocket_manager import websocket_manager

router = APIRouter(prefix="/live-config", tags=["admin-live-config"])


class LiveConfigUpdate(BaseModel):
    # Chat Interface
    chat_title: Optional[str] = None
    chat_subtitle: Optional[str] = None
    welcome_message: Optional[str] = None
    placeholder_text: Optional[str] = None
    
    # Visual Configuration
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    accent_color: Optional[str] = None
    background_color: Optional[str] = None
    text_color: Optional[str] = None
    
    # Branding
    logo_url: Optional[str] = None
    company_name: Optional[str] = None
    show_branding: Optional[bool] = None
    custom_css: Optional[str] = None
    
    # Behavior
    typing_indicator: Optional[bool] = None
    sound_enabled: Optional[bool] = None
    auto_scroll: Optional[bool] = None
    message_timestamps: Optional[bool] = None
    
    # Features
    file_upload_enabled: Optional[bool] = None
    max_file_size_mb: Optional[int] = None
    allowed_file_types: Optional[List[str]] = None
    
    # Rate Limiting
    messages_per_minute: Optional[int] = None
    messages_per_hour: Optional[int] = None
    
    # Advanced
    conversation_starters: Optional[List[str]] = None
    quick_replies: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None
    
    @validator('primary_color', 'secondary_color', 'accent_color', 'background_color', 'text_color')
    def validate_color(cls, v):
        if v and not v.startswith('#') or len(v) != 7:
            raise ValueError('Color must be in hex format (#RRGGBB)')
        return v


class LiveConfigResponse(BaseModel):
    id: str
    instance_id: str
    
    # All configuration fields
    chat_title: str
    chat_subtitle: str
    welcome_message: str
    placeholder_text: str
    primary_color: str
    secondary_color: str
    accent_color: str
    background_color: str
    text_color: str
    logo_url: Optional[str]
    company_name: Optional[str]
    show_branding: bool
    custom_css: Optional[str]
    typing_indicator: bool
    sound_enabled: bool
    auto_scroll: bool
    message_timestamps: bool
    file_upload_enabled: bool
    max_file_size_mb: int
    allowed_file_types: List[str]
    messages_per_minute: int
    messages_per_hour: int
    conversation_starters: List[str]
    quick_replies: List[str]
    custom_fields: Dict[str, Any]
    
    is_active: bool
    last_updated_by: Optional[str]
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


@router.get("/", response_model=LiveConfigResponse)
async def get_live_config(
    request: Request,
    db: Session = Depends(get_db),
    current_admin: InstanceAdmin = Depends(get_current_admin_user)
):
    """Get current live configuration for the instance"""
    
    tenant = get_current_tenant(request)
    if not tenant:
        raise HTTPException(status_code=400, detail="Tenant context required")
    
    # Get or create live configuration
    config = db.query(LiveConfiguration).filter(
        LiveConfiguration.instance_id == tenant["id"]
    ).first()
    
    if not config:
        # Create default configuration
        config = LiveConfiguration(
            id=str(uuid.uuid4()),
            instance_id=tenant["id"],
            last_updated_by=current_admin.id
        )
        db.add(config)
        db.commit()
        db.refresh(config)
    
    return LiveConfigResponse.from_orm(config)


@router.put("/", response_model=LiveConfigResponse)
async def update_live_config(
    config_update: LiveConfigUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_admin: InstanceAdmin = Depends(get_current_admin_user)
):
    """Update live configuration with real-time effect"""
    
    tenant = get_current_tenant(request)
    if not tenant:
        raise HTTPException(status_code=400, detail="Tenant context required")
    
    # Get existing configuration
    config = db.query(LiveConfiguration).filter(
        LiveConfiguration.instance_id == tenant["id"]
    ).first()
    
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    # Track changes for history
    changes = {}
    previous_values = {}
    
    # Update fields
    update_data = config_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(config, field):
            old_value = getattr(config, field)
            if old_value != value:
                changes[field] = value
                previous_values[field] = old_value
                setattr(config, field, value)
    
    if changes:
        config.last_updated_by = current_admin.id
        
        # Save configuration
        db.commit()
        db.refresh(config)
        
        # Record change history
        history = ConfigurationHistory(
            id=str(uuid.uuid4()),
            instance_id=tenant["id"],
            configuration_id=config.id,
            changed_by=current_admin.id,
            change_type="update",
            changes=changes,
            previous_values=previous_values,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )
        db.add(history)
        db.commit()
        
        # Trigger real-time update to connected clients
        await websocket_manager.broadcast_config_update(tenant["id"], changes)
    
    return LiveConfigResponse.from_orm(config)


@router.get("/history")
async def get_config_history(
    request: Request,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_admin: InstanceAdmin = Depends(get_current_admin_user)
):
    """Get configuration change history"""
    
    tenant = get_current_tenant(request)
    if not tenant:
        raise HTTPException(status_code=400, detail="Tenant context required")
    
    history = db.query(ConfigurationHistory).filter(
        ConfigurationHistory.instance_id == tenant["id"]
    ).order_by(ConfigurationHistory.created_at.desc()).limit(limit).all()
    
    return [
        {
            "id": h.id,
            "changed_by": h.changed_by,
            "change_type": h.change_type,
            "changes": h.changes,
            "previous_values": h.previous_values,
            "created_at": h.created_at.isoformat()
        }
        for h in history
    ]


@router.post("/rollback/{history_id}")
async def rollback_config(
    history_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_admin: InstanceAdmin = Depends(get_current_admin_user)
):
    """Rollback configuration to a previous state"""
    
    tenant = get_current_tenant(request)
    if not tenant:
        raise HTTPException(status_code=400, detail="Tenant context required")
    
    # Get history record
    history = db.query(ConfigurationHistory).filter(
        ConfigurationHistory.id == history_id,
        ConfigurationHistory.instance_id == tenant["id"]
    ).first()
    
    if not history:
        raise HTTPException(status_code=404, detail="History record not found")
    
    # Get current configuration
    config = db.query(LiveConfiguration).filter(
        LiveConfiguration.instance_id == tenant["id"]
    ).first()
    
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    # Apply rollback
    if history.previous_values:
        for field, value in history.previous_values.items():
            if hasattr(config, field):
                setattr(config, field, value)
        
        config.last_updated_by = current_admin.id
        db.commit()
        
        # Record rollback in history
        rollback_history = ConfigurationHistory(
            id=str(uuid.uuid4()),
            instance_id=tenant["id"],
            configuration_id=config.id,
            changed_by=current_admin.id,
            change_type="rollback",
            changes={"rollback_to": history_id},
            previous_values=history.changes,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )
        db.add(rollback_history)
        db.commit()
        
        # Broadcast update
        await websocket_manager.broadcast_config_update(tenant["id"], history.previous_values)
    
    return {"message": "Configuration rolled back successfully"}


@router.get("/preview")
async def preview_config(
    request: Request,
    db: Session = Depends(get_db)
):
    """Get configuration for chat interface preview (public endpoint)"""
    
    tenant = get_current_tenant(request)
    if not tenant:
        # Return default configuration for preview
        return {
            "chat_title": "AI Assistant",
            "chat_subtitle": "How can I help you today?",
            "welcome_message": "Hello! How can I assist you today?",
            "placeholder_text": "Type your message...",
            "primary_color": "#3b82f6",
            "secondary_color": "#e5e7eb",
            "accent_color": "#10b981",
            "typing_indicator": True,
            "sound_enabled": False,
            "auto_scroll": True,
            "message_timestamps": True
        }
    
    config = db.query(LiveConfiguration).filter(
        LiveConfiguration.instance_id == tenant["id"],
        LiveConfiguration.is_active == True
    ).first()
    
    if not config:
        return {"error": "Configuration not found"}
    
    # Return public configuration (exclude sensitive data)
    return {
        "chat_title": config.chat_title,
        "chat_subtitle": config.chat_subtitle,
        "welcome_message": config.welcome_message,
        "placeholder_text": config.placeholder_text,
        "primary_color": config.primary_color,
        "secondary_color": config.secondary_color,
        "accent_color": config.accent_color,
        "background_color": config.background_color,
        "text_color": config.text_color,
        "logo_url": config.logo_url,
        "company_name": config.company_name,
        "show_branding": config.show_branding,
        "custom_css": config.custom_css,
        "typing_indicator": config.typing_indicator,
        "sound_enabled": config.sound_enabled,
        "auto_scroll": config.auto_scroll,
        "message_timestamps": config.message_timestamps,
        "file_upload_enabled": config.file_upload_enabled,
        "max_file_size_mb": config.max_file_size_mb,
        "allowed_file_types": config.allowed_file_types,
        "conversation_starters": config.conversation_starters,
        "quick_replies": config.quick_replies
    }


# Remove the old broadcast function as it's now handled by websocket_manager
