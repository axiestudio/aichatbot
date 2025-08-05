from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum
import uuid


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MessageStatus(str, Enum):
    SENDING = "sending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"


class AttachmentType(str, Enum):
    IMAGE = "image"
    AUDIO = "audio"
    DOCUMENT = "document"
    VIDEO = "video"


class MessageAttachment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    filename: str
    original_filename: str
    file_size: int
    mime_type: str
    attachment_type: AttachmentType
    url: str
    thumbnail_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)


class MessageReaction(BaseModel):
    emoji: str
    count: int = 1
    users: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class MessageReply(BaseModel):
    message_id: str
    content: str
    role: MessageRole
    timestamp: datetime


class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    content: str
    role: MessageRole
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: MessageStatus = MessageStatus.SENT
    attachments: List[MessageAttachment] = Field(default_factory=list)
    reactions: List[MessageReaction] = Field(default_factory=list)
    reply_to: Optional[MessageReply] = None
    edited_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @validator('content')
    def validate_content(cls, v):
        if not v and not hasattr(cls, 'attachments'):
            raise ValueError('Message must have content or attachments')
        return v


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: Optional[str] = None
    config_id: Optional[str] = None
    use_rag: bool = Field(default=True, description="Whether to use RAG for context")
    context_strategy: Optional[str] = Field(default="comprehensive", description="RAG context strategy")
    attachments: List[str] = Field(default_factory=list, description="List of attachment IDs")
    reply_to_message_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ChatResponse(BaseModel):
    response: str
    session_id: str
    message_id: str
    sources: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None


class UserInfo(BaseModel):
    id: str
    username: Optional[str] = None
    email: Optional[str] = None
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool = True
    last_seen: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ChatSession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    config_id: Optional[str] = None
    messages: List[ChatMessage] = Field(default_factory=list)
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    message_count: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def add_message(self, message: ChatMessage):
        """Add a message to the session"""
        self.messages.append(message)
        self.message_count = len(self.messages)
        self.updated_at = datetime.utcnow()
        self.last_activity = datetime.utcnow()


class WebSocketMessage(BaseModel):
    type: str
    data: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    session_id: Optional[str] = None
    user_id: Optional[str] = None


class WebSocketConnection(BaseModel):
    connection_id: str
    session_id: str
    user_id: Optional[str] = None
    connected_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TypingIndicator(BaseModel):
    session_id: str
    user_id: str
    is_typing: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ChatConfig(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
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
    system_prompt: str = "You are a helpful AI assistant."
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=1000, ge=1, le=4000)
    model: str = Field(default="gpt-3.5-turbo")
    use_rag: bool = Field(default=True)
    rag_config: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)
