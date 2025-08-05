"""
Admin API endpoints for RAG configuration
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from pydantic import BaseModel, validator
import uuid

from ...core.database import get_db
from ...core.auth import get_current_admin_user
from ...models.database import RagInstruction

router = APIRouter(prefix="/rag-config", tags=["admin-rag-config"])


class RagConfigCreate(BaseModel):
    name: str
    system_prompt: str
    context_prompt: str
    max_context_length: int = 2000
    search_limit: int = 5
    similarity_threshold: float = 0.7
    
    @validator('max_context_length')
    def validate_max_context_length(cls, v):
        if not 100 <= v <= 10000:
            raise ValueError('Max context length must be between 100 and 10000')
        return v
    
    @validator('search_limit')
    def validate_search_limit(cls, v):
        if not 1 <= v <= 20:
            raise ValueError('Search limit must be between 1 and 20')
        return v
    
    @validator('similarity_threshold')
    def validate_similarity_threshold(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('Similarity threshold must be between 0.0 and 1.0')
        return v


class RagConfigUpdate(BaseModel):
    name: str = None
    system_prompt: str = None
    context_prompt: str = None
    max_context_length: int = None
    search_limit: int = None
    similarity_threshold: float = None
    is_active: bool = None


class RagConfigResponse(BaseModel):
    id: str
    name: str
    system_prompt: str
    context_prompt: str
    max_context_length: int
    search_limit: int
    similarity_threshold: float
    is_active: bool
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


@router.post("/configs", response_model=RagConfigResponse)
async def create_rag_config(
    config: RagConfigCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    """Create new RAG configuration"""
    
    # Deactivate other configs if this is being set as active
    db.query(RagInstruction).update({'is_active': False})
    
    # Create new config
    db_config = RagInstruction(
        id=str(uuid.uuid4()),
        name=config.name,
        system_prompt=config.system_prompt,
        context_prompt=config.context_prompt,
        max_context_length=config.max_context_length,
        search_limit=config.search_limit,
        similarity_threshold=config.similarity_threshold,
        is_active=True
    )
    
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    
    return db_config


@router.get("/configs", response_model=List[RagConfigResponse])
async def get_rag_configs(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    """Get all RAG configurations"""
    configs = db.query(RagInstruction).all()
    return configs


@router.get("/configs/{config_id}", response_model=RagConfigResponse)
async def get_rag_config(
    config_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    """Get specific RAG configuration"""
    config = db.query(RagInstruction).filter(RagInstruction.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    return config


@router.put("/configs/{config_id}", response_model=RagConfigResponse)
async def update_rag_config(
    config_id: str,
    config_update: RagConfigUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    """Update RAG configuration"""
    config = db.query(RagInstruction).filter(RagInstruction.id == config_id).first()
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
async def delete_rag_config(
    config_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    """Delete RAG configuration"""
    config = db.query(RagInstruction).filter(RagInstruction.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    db.delete(config)
    db.commit()
    
    return {"message": "Configuration deleted successfully"}


@router.post("/configs/{config_id}/activate")
async def activate_rag_config(
    config_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    """Activate specific RAG configuration"""
    config = db.query(RagInstruction).filter(RagInstruction.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    # Deactivate all other configs
    db.query(RagInstruction).update({'is_active': False})
    
    # Activate this config
    config.is_active = True
    db.commit()
    
    return {"message": "Configuration activated successfully"}


@router.get("/templates")
async def get_rag_templates(
    current_user: dict = Depends(get_current_admin_user)
):
    """Get RAG configuration templates"""
    return {
        "templates": [
            {
                "name": "General Assistant",
                "system_prompt": "You are a helpful AI assistant. Use the provided context to answer questions accurately and helpfully. If the context doesn't contain relevant information, say so clearly.",
                "context_prompt": "Context: {context}\n\nQuestion: {question}\n\nAnswer:",
                "description": "General purpose assistant for Q&A"
            },
            {
                "name": "Technical Support",
                "system_prompt": "You are a technical support specialist. Use the provided documentation and context to help users solve technical problems. Be precise and provide step-by-step solutions when possible.",
                "context_prompt": "Documentation: {context}\n\nUser Issue: {question}\n\nSolution:",
                "description": "Specialized for technical support and troubleshooting"
            },
            {
                "name": "Customer Service",
                "system_prompt": "You are a friendly customer service representative. Use the provided company information and policies to help customers. Always be polite and helpful.",
                "context_prompt": "Company Information: {context}\n\nCustomer Question: {question}\n\nResponse:",
                "description": "Customer service focused responses"
            }
        ]
    }
