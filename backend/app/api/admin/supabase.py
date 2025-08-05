"""
Admin API endpoints for Supabase configuration
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from pydantic import BaseModel, validator
import uuid

from ...core.database import get_db
from ...core.auth import get_current_admin_user
from ...models.database import SupabaseConfiguration
from ...services.supabase_service import supabase_service

router = APIRouter(prefix="/supabase", tags=["admin-supabase"])


class SupabaseConfigCreate(BaseModel):
    name: str
    url: str
    anon_key: str
    service_key: str = None
    table_name: str = "documents"
    table_prefix: str = "chatbot_"
    auto_create_tables: bool = True
    store_chat_messages: bool = True
    store_user_sessions: bool = True
    store_analytics: bool = True
    
    @validator('url')
    def validate_url(cls, v):
        if not v.startswith('https://') or not v.endswith('.supabase.co'):
            raise ValueError('Invalid Supabase URL format')
        return v


class SupabaseConfigUpdate(BaseModel):
    name: str = None
    url: str = None
    anon_key: str = None
    service_key: str = None
    table_name: str = None
    table_prefix: str = None
    auto_create_tables: bool = None
    store_chat_messages: bool = None
    store_user_sessions: bool = None
    store_analytics: bool = None
    is_active: bool = None


class SupabaseConfigResponse(BaseModel):
    id: str
    name: str
    url: str
    table_name: str
    table_prefix: str
    auto_create_tables: bool
    store_chat_messages: bool
    store_user_sessions: bool
    store_analytics: bool
    is_active: bool
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


@router.post("/configs", response_model=SupabaseConfigResponse)
async def create_supabase_config(
    config: SupabaseConfigCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    """Create new Supabase configuration"""
    
    # Test connection first
    test_config = SupabaseConfiguration(
        url=config.url,
        anon_key=config.anon_key,
        table_name=config.table_name
    )
    
    connection_test = await supabase_service.test_connection(test_config)
    if not connection_test:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to connect to Supabase with provided credentials"
        )
    
    # Deactivate other configs if this is being set as active
    if config.auto_create_tables:
        db.query(SupabaseConfiguration).update({'is_active': False})
    
    # Create new config
    db_config = SupabaseConfiguration(
        id=str(uuid.uuid4()),
        name=config.name,
        url=config.url,
        anon_key=config.anon_key,
        service_key=config.service_key,
        table_name=config.table_name,
        table_prefix=config.table_prefix,
        auto_create_tables=config.auto_create_tables,
        store_chat_messages=config.store_chat_messages,
        store_user_sessions=config.store_user_sessions,
        store_analytics=config.store_analytics,
        is_active=True
    )
    
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    
    # Configure the service with new config
    supabase_service.configure(db_config)
    
    return db_config


@router.get("/configs", response_model=List[SupabaseConfigResponse])
async def get_supabase_configs(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    """Get all Supabase configurations"""
    configs = db.query(SupabaseConfiguration).all()
    return configs


@router.get("/configs/{config_id}", response_model=SupabaseConfigResponse)
async def get_supabase_config(
    config_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    """Get specific Supabase configuration"""
    config = db.query(SupabaseConfiguration).filter(SupabaseConfiguration.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    return config


@router.put("/configs/{config_id}", response_model=SupabaseConfigResponse)
async def update_supabase_config(
    config_id: str,
    config_update: SupabaseConfigUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    """Update Supabase configuration"""
    config = db.query(SupabaseConfiguration).filter(SupabaseConfiguration.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    # Update fields
    update_data = config_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(config, field, value)
    
    # Test connection if URL or key changed
    if 'url' in update_data or 'anon_key' in update_data:
        connection_test = await supabase_service.test_connection(config)
        if not connection_test:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to connect to Supabase with updated credentials"
            )
    
    db.commit()
    db.refresh(config)
    
    # Reconfigure service if this is the active config
    if config.is_active:
        supabase_service.configure(config)
    
    return config


@router.delete("/configs/{config_id}")
async def delete_supabase_config(
    config_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    """Delete Supabase configuration"""
    config = db.query(SupabaseConfiguration).filter(SupabaseConfiguration.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    db.delete(config)
    db.commit()
    
    return {"message": "Configuration deleted successfully"}


@router.post("/configs/{config_id}/activate")
async def activate_supabase_config(
    config_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    """Activate specific Supabase configuration"""
    config = db.query(SupabaseConfiguration).filter(SupabaseConfiguration.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    # Test connection
    connection_test = await supabase_service.test_connection(config)
    if not connection_test:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot activate - connection test failed"
        )
    
    # Deactivate all other configs
    db.query(SupabaseConfiguration).update({'is_active': False})
    
    # Activate this config
    config.is_active = True
    db.commit()
    
    # Configure the service
    supabase_service.configure(config)
    
    return {"message": "Configuration activated successfully"}


@router.post("/configs/{config_id}/test")
async def test_supabase_connection(
    config_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    """Test Supabase connection"""
    config = db.query(SupabaseConfiguration).filter(SupabaseConfiguration.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    try:
        connection_test = await supabase_service.test_connection(config)
        if connection_test:
            return {"status": "success", "message": "Connection successful"}
        else:
            return {"status": "error", "message": "Connection failed"}
    except Exception as e:
        return {"status": "error", "message": f"Connection error: {str(e)}"}


@router.get("/analytics")
async def get_supabase_analytics(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    """Get analytics from active Supabase configuration"""
    active_config = db.query(SupabaseConfiguration).filter(SupabaseConfiguration.is_active == True).first()
    
    if not active_config:
        return {"error": "No active Supabase configuration"}
    
    try:
        # Configure service with active config
        supabase_service.configure(active_config)
        
        # Get analytics data
        analytics = await supabase_service.get_analytics()
        return analytics
    except Exception as e:
        return {"error": f"Failed to get analytics: {str(e)}"}
