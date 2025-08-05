from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class AIProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    CUSTOM = "custom"


class ApiConfig(BaseModel):
    id: str
    provider: AIProvider
    api_key: str = Field(..., min_length=1)
    model: str
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=1000, ge=1, le=8000)
    custom_endpoint: Optional[str] = None
    custom_headers: Optional[Dict[str, str]] = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime


class SupabaseConfig(BaseModel):
    id: str
    url: str = Field(..., regex=r"^https://[a-zA-Z0-9-]+\.supabase\.co$")
    anon_key: str = Field(..., min_length=1)
    service_key: Optional[str] = None
    table_name: str = Field(default="knowledge_base", min_length=1)
    search_columns: List[str] = Field(default=["title", "content"])
    is_active: bool = True
    created_at: datetime
    updated_at: datetime


class RagInstruction(BaseModel):
    id: str
    name: str
    system_prompt: str = Field(..., min_length=1)
    context_prompt: str = Field(..., min_length=1)
    max_context_length: int = Field(default=2000, ge=100, le=8000)
    search_limit: int = Field(default=5, ge=1, le=20)
    is_active: bool = True
    created_at: datetime
    updated_at: datetime


class ConfigurationSet(BaseModel):
    """Complete configuration set for a chatbot instance"""
    chat_config: ChatConfig
    api_config: ApiConfig
    supabase_config: Optional[SupabaseConfig] = None
    rag_instruction: Optional[RagInstruction] = None
