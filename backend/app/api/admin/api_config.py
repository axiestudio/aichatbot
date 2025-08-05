"""
Admin API endpoints for AI API configuration
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from pydantic import BaseModel, validator
import uuid

from ...core.database import get_db
from ...core.auth import get_current_admin_user
from ...models.database import ApiConfiguration

router = APIRouter(prefix="/api-config", tags=["admin-api-config"])


class ApiConfigCreate(BaseModel):
    name: str
    provider: str  # openai, anthropic, etc.
    api_key: str
    model: str
    temperature: float = 0.7
    max_tokens: int = 1000
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    
    @validator('provider')
    def validate_provider(cls, v):
        allowed_providers = ['openai', 'anthropic', 'cohere', 'huggingface']
        if v.lower() not in allowed_providers:
            raise ValueError(f'Provider must be one of: {", ".join(allowed_providers)}')
        return v.lower()
    
    @validator('temperature')
    def validate_temperature(cls, v):
        if not 0.0 <= v <= 2.0:
            raise ValueError('Temperature must be between 0.0 and 2.0')
        return v
    
    @validator('max_tokens')
    def validate_max_tokens(cls, v):
        if not 1 <= v <= 32000:
            raise ValueError('Max tokens must be between 1 and 32000')
        return v


class ApiConfigUpdate(BaseModel):
    name: str = None
    provider: str = None
    api_key: str = None
    model: str = None
    temperature: float = None
    max_tokens: int = None
    top_p: float = None
    frequency_penalty: float = None
    presence_penalty: float = None
    is_active: bool = None


class ApiConfigResponse(BaseModel):
    id: str
    name: str
    provider: str
    model: str
    temperature: float
    max_tokens: int
    top_p: float
    frequency_penalty: float
    presence_penalty: float
    is_active: bool
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


@router.post("/configs", response_model=ApiConfigResponse)
async def create_api_config(
    config: ApiConfigCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    """Create new API configuration"""
    
    # Deactivate other configs if this is being set as active
    db.query(ApiConfiguration).update({'is_active': False})
    
    # Create new config
    db_config = ApiConfiguration(
        id=str(uuid.uuid4()),
        name=config.name,
        provider=config.provider,
        api_key=config.api_key,  # In production, this should be encrypted
        model=config.model,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
        top_p=config.top_p,
        frequency_penalty=config.frequency_penalty,
        presence_penalty=config.presence_penalty,
        is_active=True
    )
    
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    
    return db_config


@router.get("/configs", response_model=List[ApiConfigResponse])
async def get_api_configs(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    """Get all API configurations"""
    configs = db.query(ApiConfiguration).all()
    return configs


@router.get("/configs/{config_id}", response_model=ApiConfigResponse)
async def get_api_config(
    config_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    """Get specific API configuration"""
    config = db.query(ApiConfiguration).filter(ApiConfiguration.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    return config


@router.put("/configs/{config_id}", response_model=ApiConfigResponse)
async def update_api_config(
    config_id: str,
    config_update: ApiConfigUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    """Update API configuration"""
    config = db.query(ApiConfiguration).filter(ApiConfiguration.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    # Update fields
    update_data = config_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(config, field, value)
    
    db.commit()
    db.refresh(config)
    
    return config


@router.delete("/configs/{config_id}")
async def delete_api_config(
    config_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    """Delete API configuration"""
    config = db.query(ApiConfiguration).filter(ApiConfiguration.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    db.delete(config)
    db.commit()
    
    return {"message": "Configuration deleted successfully"}


@router.post("/configs/{config_id}/activate")
async def activate_api_config(
    config_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    """Activate specific API configuration"""
    config = db.query(ApiConfiguration).filter(ApiConfiguration.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    # Deactivate all other configs
    db.query(ApiConfiguration).update({'is_active': False})
    
    # Activate this config
    config.is_active = True
    db.commit()
    
    return {"message": "Configuration activated successfully"}


@router.post("/configs/{config_id}/test")
async def test_api_config(
    config_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    """Test API configuration"""
    config = db.query(ApiConfiguration).filter(ApiConfiguration.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    try:
        # Test the API configuration
        if config.provider == "openai":
            import openai
            client = openai.OpenAI(api_key=config.api_key)
            response = client.chat.completions.create(
                model=config.model,
                messages=[{"role": "user", "content": "Hello, this is a test."}],
                max_tokens=10
            )
            return {"status": "success", "message": "OpenAI API connection successful"}
        
        elif config.provider == "anthropic":
            import anthropic
            client = anthropic.Anthropic(api_key=config.api_key)
            response = client.messages.create(
                model=config.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "Hello, this is a test."}]
            )
            return {"status": "success", "message": "Anthropic API connection successful"}
        
        else:
            return {"status": "error", "message": f"Testing not implemented for provider: {config.provider}"}
            
    except Exception as e:
        return {"status": "error", "message": f"API test failed: {str(e)}"}


@router.get("/providers")
async def get_supported_providers(
    current_user: dict = Depends(get_current_admin_user)
):
    """Get list of supported AI providers"""
    return {
        "providers": [
            {
                "id": "openai",
                "name": "OpenAI",
                "models": ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo-preview"],
                "description": "OpenAI's GPT models"
            },
            {
                "id": "anthropic",
                "name": "Anthropic",
                "models": ["claude-3-haiku-20240307", "claude-3-sonnet-20240229", "claude-3-opus-20240229"],
                "description": "Anthropic's Claude models"
            }
        ]
    }
