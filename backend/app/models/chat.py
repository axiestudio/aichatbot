from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatMessage(BaseModel):
    id: Optional[str] = None
    content: str
    role: MessageRole
    timestamp: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: Optional[str] = None
    config_id: Optional[str] = None
    use_rag: bool = Field(default=True, description="Whether to use RAG for context")
    context_strategy: Optional[str] = Field(default="comprehensive", description="RAG context strategy")
    context: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str
    message_id: str
    sources: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None


class ChatSession(BaseModel):
    id: str
    messages: List[ChatMessage]
    config_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    metadata: Optional[Dict[str, Any]] = None


class ChatConfig(BaseModel):
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
