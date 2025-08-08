"""
Simplified database models for Railway deployment
SQLAlchemy 1.4 compatible version
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, JSON, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()


class ChatSession(Base):
    """Chat session database model"""
    __tablename__ = "chat_sessions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(255), nullable=True, index=True)
    config_id = Column(String(255), nullable=True, index=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_activity = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    metadata = Column(JSON, nullable=True)
    
    # Relationships
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    """Chat message database model"""
    __tablename__ = "chat_messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey('chat_sessions.id'), nullable=False)
    content = Column(Text, nullable=False)
    role = Column(String(20), nullable=False)  # user, assistant, system
    status = Column(String(20), default='sent', nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    edited_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)
    reply_to_message_id = Column(String(36), ForeignKey('chat_messages.id'), nullable=True)
    response_time = Column(Float, nullable=True)
    tokens_used = Column(Integer, default=0)
    config_used = Column(String(255), nullable=True)
    rag_context = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    
    # Relationships
    session = relationship("ChatSession", back_populates="messages")
    attachments = relationship("MessageAttachment", back_populates="message", cascade="all, delete-orphan")
    reactions = relationship("MessageReaction", back_populates="message", cascade="all, delete-orphan")


class MessageAttachment(Base):
    """Message attachment database model"""
    __tablename__ = "message_attachments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    message_id = Column(String(36), ForeignKey('chat_messages.id'), nullable=False)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    attachment_type = Column(String(20), nullable=False)
    file_path = Column(String(500), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    message = relationship("ChatMessage", back_populates="attachments")


class MessageReaction(Base):
    """Message reaction database model"""
    __tablename__ = "message_reactions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    message_id = Column(String(36), ForeignKey('chat_messages.id'), nullable=False)
    user_id = Column(String(255), nullable=False)
    emoji = Column(String(10), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    message = relationship("ChatMessage", back_populates="reactions")


class Document(Base):
    """Document database model"""
    __tablename__ = "documents"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_type = Column(String(50), nullable=False)
    mime_type = Column(String(100), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    processed_at = Column(DateTime, nullable=True)
    status = Column(String(20), default='uploaded', nullable=False)
    user_id = Column(String(255), nullable=True, index=True)
    
    # Relationships
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    metadata = relationship("DocumentMetadata", back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    """Document chunk database model"""
    __tablename__ = "document_chunks"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(36), ForeignKey('documents.id'), nullable=False)
    content = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    start_char = Column(Integer, nullable=False)
    end_char = Column(Integer, nullable=False)
    embedding = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    document = relationship("Document", back_populates="chunks")


class DocumentMetadata(Base):
    """Document metadata database model"""
    __tablename__ = "document_metadata"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(36), ForeignKey('documents.id'), nullable=False)
    title = Column(String(500), nullable=True)
    author = Column(String(255), nullable=True)
    subject = Column(String(500), nullable=True)
    keywords = Column(JSON, nullable=True)
    language = Column(String(10), default='en')
    page_count = Column(Integer, nullable=True)
    word_count = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    document = relationship("Document", back_populates="metadata")


# Basic models for essential functionality
class SuperAdmin(Base):
    """Super admin database model"""
    __tablename__ = "super_admins"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)


class ChatInstance(Base):
    """Chat instance database model"""
    __tablename__ = "chat_instances"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    subdomain = Column(String(100), unique=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    settings = Column(JSON, nullable=True)


class InstanceAdmin(Base):
    """Instance admin database model"""
    __tablename__ = "instance_admins"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    instance_id = Column(String(36), ForeignKey('chat_instances.id'), nullable=False)
    username = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)


class LiveConfiguration(Base):
    """Live configuration database model"""
    __tablename__ = "live_configurations"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    instance_id = Column(String(36), ForeignKey('chat_instances.id'), nullable=False)
    chat_title = Column(String(255), default="AI Assistant")
    chat_subtitle = Column(String(255), nullable=True)
    welcome_message = Column(Text, default="Hello! How can I help you today?")
    placeholder_text = Column(String(255), default="Type your message here...")
    primary_color = Column(String(7), default="#3b82f6")
    secondary_color = Column(String(7), default="#e5e7eb")
    accent_color = Column(String(7), default="#10b981")
    background_color = Column(String(7), default="#ffffff")
    text_color = Column(String(7), default="#1f2937")
    company_name = Column(String(255), nullable=True)
    show_branding = Column(Boolean, default=True)
    typing_indicator = Column(Boolean, default=True)
    sound_enabled = Column(Boolean, default=False)
    auto_scroll = Column(Boolean, default=True)
    message_timestamps = Column(Boolean, default=True)
    file_upload_enabled = Column(Boolean, default=True)
    max_file_size_mb = Column(Integer, default=10)
    allowed_file_types = Column(JSON, default=lambda: ["pdf", "txt", "docx", "jpg", "png"])
    messages_per_minute = Column(Integer, default=10)
    messages_per_hour = Column(Integer, default=100)
    conversation_starters = Column(JSON, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
