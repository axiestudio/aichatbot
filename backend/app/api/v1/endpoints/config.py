from fastapi import APIRouter, HTTPException, Depends
from typing import List
import logging

from app.models.config import ApiConfig, SupabaseConfig, RagInstruction, ChatConfig
from app.services.config_service import ConfigService
from app.core.dependencies import get_config_service

router = APIRouter()
logger = logging.getLogger(__name__)


# Chat Configuration Endpoints
@router.post("/chat", response_model=ChatConfig)
async def create_chat_config(
    config: ChatConfig,
    config_service: ConfigService = Depends(get_config_service)
):
    """Create a new chat configuration"""
    try:
        return await config_service.create_chat_config(config)
    except Exception as e:
        logger.error(f"Error creating chat config: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create chat configuration")


@router.get("/chat/{config_id}", response_model=ChatConfig)
async def get_chat_config(
    config_id: str,
    config_service: ConfigService = Depends(get_config_service)
):
    """Get a chat configuration by ID"""
    try:
        config = await config_service.get_chat_config(config_id)
        if not config:
            raise HTTPException(status_code=404, detail="Configuration not found")
        return config
    except Exception as e:
        logger.error(f"Error retrieving chat config {config_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve chat configuration")


@router.put("/chat/{config_id}", response_model=ChatConfig)
async def update_chat_config(
    config_id: str,
    config: ChatConfig,
    config_service: ConfigService = Depends(get_config_service)
):
    """Update a chat configuration"""
    try:
        updated_config = await config_service.update_chat_config(config_id, config)
        if not updated_config:
            raise HTTPException(status_code=404, detail="Configuration not found")
        return updated_config
    except Exception as e:
        logger.error(f"Error updating chat config {config_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update chat configuration")


# API Configuration Endpoints
@router.post("/api", response_model=ApiConfig)
async def create_api_config(
    config: ApiConfig,
    config_service: ConfigService = Depends(get_config_service)
):
    """Create a new API configuration"""
    try:
        return await config_service.create_api_config(config)
    except Exception as e:
        logger.error(f"Error creating API config: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create API configuration")


@router.get("/api/{config_id}", response_model=ApiConfig)
async def get_api_config(
    config_id: str,
    config_service: ConfigService = Depends(get_config_service)
):
    """Get an API configuration by ID"""
    try:
        config = await config_service.get_api_config(config_id)
        if not config:
            raise HTTPException(status_code=404, detail="Configuration not found")
        return config
    except Exception as e:
        logger.error(f"Error retrieving API config {config_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve API configuration")


# Supabase Configuration Endpoints
@router.post("/supabase", response_model=SupabaseConfig)
async def create_supabase_config(
    config: SupabaseConfig,
    config_service: ConfigService = Depends(get_config_service)
):
    """Create a new Supabase configuration"""
    try:
        return await config_service.create_supabase_config(config)
    except Exception as e:
        logger.error(f"Error creating Supabase config: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create Supabase configuration")


@router.get("/supabase/{config_id}", response_model=SupabaseConfig)
async def get_supabase_config(
    config_id: str,
    config_service: ConfigService = Depends(get_config_service)
):
    """Get a Supabase configuration by ID"""
    try:
        config = await config_service.get_supabase_config(config_id)
        if not config:
            raise HTTPException(status_code=404, detail="Configuration not found")
        return config
    except Exception as e:
        logger.error(f"Error retrieving Supabase config {config_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve Supabase configuration")


# RAG Instructions Endpoints
@router.post("/rag", response_model=RagInstruction)
async def create_rag_instruction(
    instruction: RagInstruction,
    config_service: ConfigService = Depends(get_config_service)
):
    """Create a new RAG instruction"""
    try:
        return await config_service.create_rag_instruction(instruction)
    except Exception as e:
        logger.error(f"Error creating RAG instruction: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create RAG instruction")


@router.get("/rag/{instruction_id}", response_model=RagInstruction)
async def get_rag_instruction(
    instruction_id: str,
    config_service: ConfigService = Depends(get_config_service)
):
    """Get a RAG instruction by ID"""
    try:
        instruction = await config_service.get_rag_instruction(instruction_id)
        if not instruction:
            raise HTTPException(status_code=404, detail="Instruction not found")
        return instruction
    except Exception as e:
        logger.error(f"Error retrieving RAG instruction {instruction_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve RAG instruction")


@router.put("/rag/{instruction_id}", response_model=RagInstruction)
async def update_rag_instruction(
    instruction_id: str,
    instruction: RagInstruction,
    config_service: ConfigService = Depends(get_config_service)
):
    """Update a RAG instruction"""
    try:
        updated_instruction = await config_service.update_rag_instruction(instruction_id, instruction)
        if not updated_instruction:
            raise HTTPException(status_code=404, detail="Instruction not found")
        return updated_instruction
    except Exception as e:
        logger.error(f"Error updating RAG instruction {instruction_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update RAG instruction")


# Test Endpoints
@router.post("/test/api")
async def test_api_connection(
    config: ApiConfig,
    config_service: ConfigService = Depends(get_config_service)
):
    """Test API connection"""
    try:
        result = await config_service.test_api_connection(config)
        return {"success": result, "message": "API connection successful" if result else "API connection failed"}
    except Exception as e:
        logger.error(f"Error testing API connection: {str(e)}")
        return {"success": False, "message": str(e)}


@router.post("/test/supabase")
async def test_supabase_connection(
    config: SupabaseConfig,
    config_service: ConfigService = Depends(get_config_service)
):
    """Test Supabase connection"""
    try:
        result = await config_service.test_supabase_connection(config)
        return {"success": result, "message": "Supabase connection successful" if result else "Supabase connection failed"}
    except Exception as e:
        logger.error(f"Error testing Supabase connection: {str(e)}")
        return {"success": False, "message": str(e)}
