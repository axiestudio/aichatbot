"""
Real-Time Configuration API - Enhanced configuration management with instant updates
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import json
import uuid
from datetime import datetime

from ....core.database import get_db
from ....core.auth import get_current_admin_user
from ....models.database import LiveConfiguration, ConfigurationHistory
from ....services.websocket_manager import websocket_manager
from ....services.white_label_manager import white_label_manager
from ....services.tenant_manager import tenant_manager
from ....middleware.multi_tenant import get_current_tenant

router = APIRouter(prefix="/realtime-config", tags=["realtime-configuration"])


class ConfigurationUpdate(BaseModel):
    """Real-time configuration update model"""
    changes: Dict[str, Any]
    preview_mode: bool = False
    apply_immediately: bool = True
    version_name: Optional[str] = None
    description: Optional[str] = None


class ConfigurationPreview(BaseModel):
    """Configuration preview response"""
    preview_id: str
    changes: Dict[str, Any]
    preview_url: str
    expires_at: datetime


class ConfigurationVersion(BaseModel):
    """Configuration version model"""
    id: str
    version_name: str
    description: Optional[str]
    configuration: Dict[str, Any]
    created_by: str
    created_at: datetime
    is_active: bool


@router.post("/update")
async def update_configuration_realtime(
    update: ConfigurationUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin_user),
    tenant_info = Depends(get_current_tenant)
):
    """Update configuration with real-time propagation"""
    
    if not tenant_info:
        raise HTTPException(status_code=400, detail="Tenant context required")
    
    tenant_id = tenant_info["id"]
    
    try:
        # Get current configuration
        config = db.query(LiveConfiguration).filter(
            LiveConfiguration.instance_id == tenant_id
        ).first()
        
        if not config:
            raise HTTPException(status_code=404, detail="Configuration not found")
        
        # Validate changes
        validation_result = await _validate_configuration_changes(update.changes, tenant_id)
        if not validation_result["valid"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid configuration: {validation_result['errors']}"
            )
        
        if update.preview_mode:
            # Create preview
            preview = await _create_configuration_preview(
                tenant_id, update.changes, current_admin["id"]
            )
            return preview
        
        # Save configuration history
        if update.version_name:
            await _save_configuration_version(
                tenant_id, config, update.version_name, 
                update.description, current_admin["id"], db
            )
        
        # Apply changes to configuration
        updated_config = await _apply_configuration_changes(
            config, update.changes, current_admin["id"], db
        )
        
        # Update white-label theme
        await white_label_manager.update_tenant_theme(tenant_id, update.changes)
        
        if update.apply_immediately:
            # Broadcast changes to all connected clients
            await _broadcast_configuration_update(tenant_id, update.changes)
        
        return {
            "success": True,
            "message": "Configuration updated successfully",
            "configuration": _serialize_configuration(updated_config),
            "applied_immediately": update.apply_immediately
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/preview/{preview_id}")
async def get_configuration_preview(
    preview_id: str,
    tenant_info = Depends(get_current_tenant)
):
    """Get configuration preview"""
    
    # TODO: Implement preview storage and retrieval
    # For now, return a mock response
    return {
        "preview_id": preview_id,
        "configuration": {},
        "expires_at": datetime.utcnow()
    }


@router.post("/preview")
async def create_configuration_preview(
    changes: Dict[str, Any],
    current_admin = Depends(get_current_admin_user),
    tenant_info = Depends(get_current_tenant)
):
    """Create a configuration preview"""
    
    if not tenant_info:
        raise HTTPException(status_code=400, detail="Tenant context required")
    
    preview = await _create_configuration_preview(
        tenant_info["id"], changes, current_admin["id"]
    )
    
    return preview


@router.get("/versions")
async def get_configuration_versions(
    db: Session = Depends(get_db),
    tenant_info = Depends(get_current_tenant)
):
    """Get configuration version history"""
    
    if not tenant_info:
        raise HTTPException(status_code=400, detail="Tenant context required")
    
    versions = db.query(ConfigurationHistory).filter(
        ConfigurationHistory.instance_id == tenant_info["id"]
    ).order_by(ConfigurationHistory.created_at.desc()).limit(50).all()
    
    return [
        ConfigurationVersion(
            id=version.id,
            version_name=version.version_name,
            description=version.description,
            configuration=json.loads(version.configuration_data),
            created_by=version.created_by,
            created_at=version.created_at,
            is_active=version.is_active
        )
        for version in versions
    ]


@router.post("/versions/{version_id}/restore")
async def restore_configuration_version(
    version_id: str,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin_user),
    tenant_info = Depends(get_current_tenant)
):
    """Restore a configuration version"""
    
    if not tenant_info:
        raise HTTPException(status_code=400, detail="Tenant context required")
    
    # Get version
    version = db.query(ConfigurationHistory).filter(
        ConfigurationHistory.id == version_id,
        ConfigurationHistory.instance_id == tenant_info["id"]
    ).first()
    
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    
    # Get current configuration
    config = db.query(LiveConfiguration).filter(
        LiveConfiguration.instance_id == tenant_info["id"]
    ).first()
    
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    # Restore configuration
    version_data = json.loads(version.configuration_data)
    updated_config = await _apply_configuration_changes(
        config, version_data, current_admin["id"], db
    )
    
    # Update white-label theme
    await white_label_manager.update_tenant_theme(tenant_info["id"], version_data)
    
    # Broadcast changes
    await _broadcast_configuration_update(tenant_info["id"], version_data)
    
    return {
        "success": True,
        "message": f"Configuration restored to version: {version.version_name}",
        "configuration": _serialize_configuration(updated_config)
    }


@router.websocket("/ws/{tenant_id}")
async def configuration_websocket(
    websocket: WebSocket,
    tenant_id: str
):
    """WebSocket endpoint for real-time configuration updates"""
    
    await websocket.accept()
    
    # Register connection for configuration updates
    await websocket_manager.connect(websocket, tenant_id, "config")
    
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                
                if message.get("type") == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
                elif message.get("type") == "subscribe_config":
                    # Send current configuration
                    current_config = await _get_current_configuration(tenant_id)
                    await websocket.send_text(json.dumps({
                        "type": "config_snapshot",
                        "configuration": current_config
                    }))
                    
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": "Invalid JSON format"
                }))
                
    except WebSocketDisconnect:
        await websocket_manager.disconnect(websocket, tenant_id)


# Helper functions

async def _validate_configuration_changes(changes: Dict[str, Any], tenant_id: str) -> Dict[str, Any]:
    """Validate configuration changes"""
    
    validation_result = {
        "valid": True,
        "errors": [],
        "warnings": []
    }
    
    # Validate color formats
    color_fields = ["primary_color", "secondary_color", "accent_color", "background_color", "text_color"]
    for field in color_fields:
        if field in changes:
            color = changes[field]
            if not isinstance(color, str) or not color.startswith("#") or len(color) != 7:
                validation_result["valid"] = False
                validation_result["errors"].append(f"Invalid color format for {field}")
    
    # Validate custom CSS if present
    if "custom_css" in changes:
        css_validation = await white_label_manager.validate_custom_css(changes["custom_css"])
        if not css_validation["valid"]:
            validation_result["valid"] = False
            validation_result["errors"].extend(css_validation["errors"])
        validation_result["warnings"].extend(css_validation.get("warnings", []))
    
    # Check tenant quotas
    if not await tenant_manager.check_tenant_quota(tenant_id, "configurations"):
        validation_result["valid"] = False
        validation_result["errors"].append("Configuration quota exceeded")
    
    return validation_result


async def _create_configuration_preview(
    tenant_id: str, changes: Dict[str, Any], admin_id: str
) -> ConfigurationPreview:
    """Create a configuration preview"""
    
    preview_id = str(uuid.uuid4())
    
    # TODO: Store preview in cache/database with expiration
    
    preview_url = f"/chat/{tenant_id}?preview={preview_id}"
    
    return ConfigurationPreview(
        preview_id=preview_id,
        changes=changes,
        preview_url=preview_url,
        expires_at=datetime.utcnow()
    )


async def _save_configuration_version(
    tenant_id: str, config: LiveConfiguration, version_name: str,
    description: Optional[str], admin_id: str, db: Session
):
    """Save configuration version to history"""
    
    # Serialize current configuration
    config_data = _serialize_configuration(config)
    
    # Create history record
    history = ConfigurationHistory(
        id=str(uuid.uuid4()),
        instance_id=tenant_id,
        version_name=version_name,
        description=description,
        configuration_data=json.dumps(config_data),
        created_by=admin_id,
        created_at=datetime.utcnow(),
        is_active=True
    )
    
    db.add(history)
    db.commit()


async def _apply_configuration_changes(
    config: LiveConfiguration, changes: Dict[str, Any], 
    admin_id: str, db: Session
) -> LiveConfiguration:
    """Apply changes to configuration"""
    
    # Update configuration fields
    for field, value in changes.items():
        if hasattr(config, field):
            setattr(config, field, value)
    
    config.last_updated_by = admin_id
    config.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(config)
    
    return config


async def _broadcast_configuration_update(tenant_id: str, changes: Dict[str, Any]):
    """Broadcast configuration changes to all connected clients"""
    
    message = {
        "type": "config_update",
        "changes": changes,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Send to chat interfaces
    await websocket_manager.send_to_instance(tenant_id, message, "chat")
    
    # Send to admin interfaces
    await websocket_manager.send_to_instance(tenant_id, message, "admin")


async def _get_current_configuration(tenant_id: str) -> Dict[str, Any]:
    """Get current configuration for tenant"""
    
    try:
        db = next(get_db())
        config = db.query(LiveConfiguration).filter(
            LiveConfiguration.instance_id == tenant_id
        ).first()
        
        if config:
            return _serialize_configuration(config)
        
    except Exception as e:
        logger.error(f"Error getting configuration for tenant {tenant_id}: {e}")
    
    return {}


def _serialize_configuration(config: LiveConfiguration) -> Dict[str, Any]:
    """Serialize configuration to dictionary"""
    
    return {
        "id": config.id,
        "instance_id": config.instance_id,
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
        "messages_per_minute": config.messages_per_minute,
        "messages_per_hour": config.messages_per_hour,
        "conversation_starters": config.conversation_starters,
        "quick_replies": config.quick_replies,
        "custom_fields": config.custom_fields,
        "is_active": config.is_active,
        "last_updated_by": config.last_updated_by,
        "created_at": config.created_at.isoformat() if config.created_at else None,
        "updated_at": config.updated_at.isoformat() if config.updated_at else None
    }
