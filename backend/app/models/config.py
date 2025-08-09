"""
Configuration models and classes for the chat service
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel


class ChatConfig(BaseModel):
    """Chat configuration model"""
    id: str
    name: str
    primary_color: str = "#3b82f6"
    secondary_color: str = "#e5e7eb"
    font_family: str = "Inter"
    font_size: int = 14
    border_radius: int = 12
    position: str = "bottom-right"
    welcome_message: str = "Hello! How can I help you today?"
    placeholder: str = "Type your message..."
    height: int = 500
    width: int = 350
    is_active: bool = True
    created_at: datetime
    updated_at: datetime


class CacheConfig(BaseModel):
    """Cache configuration model"""
    ttl: int = 300  # Time to live in seconds
    max_size: int = 1000  # Maximum number of items
    namespace: str = "default"
    
    class Config:
        arbitrary_types_allowed = True


class CircuitBreakerConfig(BaseModel):
    """Circuit breaker configuration model"""
    failure_threshold: int = 5  # Number of failures before opening
    recovery_timeout: int = 60  # Seconds to wait before trying again
    timeout: float = 30.0  # Request timeout in seconds
    
    class Config:
        arbitrary_types_allowed = True


class ApiConfig(BaseModel):
    """API configuration model"""
    id: str
    name: str
    provider: str  # openai, anthropic, etc.
    api_key: str
    model: str
    temperature: float = 0.7
    max_tokens: int = 1000
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    is_active: bool = True
    created_at: datetime
    updated_at: datetime


class SupabaseConfig(BaseModel):
    """Supabase configuration model"""
    id: str
    url: str
    anon_key: str
    service_key: Optional[str] = None
    table_name: str
    search_columns: List[str]
    is_active: bool = True
    created_at: datetime
    updated_at: datetime


class RagInstruction(BaseModel):
    """RAG instruction model"""
    id: str
    name: str
    system_prompt: str
    context_prompt: str
    max_context_length: int = 2000
    search_limit: int = 5
    similarity_threshold: float = 0.7
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
