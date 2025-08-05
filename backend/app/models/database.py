from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, JSON, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

Base = declarative_base()


class ChatSession(Base):
    """Chat session database model"""
    __tablename__ = "chat_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
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
    
    # Indexes
    __table_args__ = (
        Index('idx_chat_sessions_user_id', 'user_id'),
        Index('idx_chat_sessions_created_at', 'created_at'),
        Index('idx_chat_sessions_active', 'is_active'),
    )


class ChatMessage(Base):
    """Chat message database model"""
    __tablename__ = "chat_messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey('chat_sessions.id'), nullable=False)
    user_message = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    response_time = Column(Float, nullable=True)
    tokens_used = Column(Integer, default=0)
    config_used = Column(String(255), nullable=True)
    rag_context = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    flagged = Column(Boolean, default=False)
    admin_notes = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)
    
    # Relationships
    session = relationship("ChatSession", back_populates="messages")
    
    # Indexes
    __table_args__ = (
        Index('idx_chat_messages_session_id', 'session_id'),
        Index('idx_chat_messages_timestamp', 'timestamp'),
        Index('idx_chat_messages_flagged', 'flagged'),
    )


class Document(Base):
    """Document database model"""
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_type = Column(String(50), nullable=False)
    mime_type = Column(String(100), nullable=False)
    status = Column(String(50), default='uploading', nullable=False)
    content = Column(Text, nullable=True)
    chunk_count = Column(Integer, default=0)
    processing_error = Column(Text, nullable=True)
    config_id = Column(String(255), nullable=True, index=True)
    uploaded_by = Column(String(255), nullable=True)
    tags = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    processed_at = Column(DateTime, nullable=True)
    
    # Relationships
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    metadata_record = relationship("DocumentMetadata", back_populates="document", uselist=False, cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_documents_status', 'status'),
        Index('idx_documents_config_id', 'config_id'),
        Index('idx_documents_created_at', 'created_at'),
        Index('idx_documents_file_type', 'file_type'),
    )


class DocumentChunk(Base):
    """Document chunk database model"""
    __tablename__ = "document_chunks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey('documents.id'), nullable=False)
    content = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    start_char = Column(Integer, nullable=False)
    end_char = Column(Integer, nullable=False)
    embedding = Column(JSON, nullable=True)  # Store as JSON array
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    document = relationship("Document", back_populates="chunks")
    
    # Indexes
    __table_args__ = (
        Index('idx_document_chunks_document_id', 'document_id'),
        Index('idx_document_chunks_chunk_index', 'chunk_index'),
    )


class DocumentMetadata(Base):
    """Document metadata database model"""
    __tablename__ = "document_metadata"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey('documents.id'), nullable=False)
    title = Column(String(500), nullable=True)
    author = Column(String(255), nullable=True)
    subject = Column(String(500), nullable=True)
    keywords = Column(JSON, nullable=True)
    language = Column(String(10), default='en')
    page_count = Column(Integer, nullable=True)
    word_count = Column(Integer, nullable=True)
    char_count = Column(Integer, nullable=True)
    encoding = Column(String(50), nullable=True)
    created_date = Column(DateTime, nullable=True)
    modified_date = Column(DateTime, nullable=True)
    extracted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    document = relationship("Document", back_populates="metadata_record")


class ChatConfiguration(Base):
    """Chat configuration database model"""
    __tablename__ = "chat_configurations"
    
    id = Column(String(255), primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    primary_color = Column(String(7), default='#3b82f6')
    secondary_color = Column(String(7), default='#e5e7eb')
    font_family = Column(String(100), default='Inter')
    font_size = Column(Integer, default=14)
    border_radius = Column(Integer, default=12)
    chat_height = Column(Integer, default=600)
    show_timestamps = Column(Boolean, default=True)
    show_avatars = Column(Boolean, default=True)
    enable_sound = Column(Boolean, default=False)
    welcome_message = Column(Text, nullable=True)
    placeholder_text = Column(String(255), default='Type your message...')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class ApiConfiguration(Base):
    """API configuration database model"""
    __tablename__ = "api_configurations"
    
    id = Column(String(255), primary_key=True)
    name = Column(String(255), nullable=False)
    provider = Column(String(50), nullable=False)  # openai, anthropic, etc.
    api_key = Column(String(500), nullable=False)  # Encrypted
    model = Column(String(100), nullable=False)
    temperature = Column(Float, default=0.7)
    max_tokens = Column(Integer, default=1000)
    top_p = Column(Float, default=1.0)
    frequency_penalty = Column(Float, default=0.0)
    presence_penalty = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class RagInstruction(Base):
    """RAG instruction database model"""
    __tablename__ = "rag_instructions"
    
    id = Column(String(255), primary_key=True)
    name = Column(String(255), nullable=False)
    system_prompt = Column(Text, nullable=False)
    context_prompt = Column(Text, nullable=False)
    max_context_length = Column(Integer, default=2000)
    search_limit = Column(Integer, default=5)
    similarity_threshold = Column(Float, default=0.7)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class SupabaseConfiguration(Base):
    """Supabase configuration database model"""
    __tablename__ = "supabase_configurations"
    
    id = Column(String(255), primary_key=True)
    name = Column(String(255), nullable=False)
    url = Column(String(500), nullable=False)
    anon_key = Column(String(500), nullable=False)  # Encrypted
    service_key = Column(String(500), nullable=True)  # Encrypted
    table_name = Column(String(100), default='documents')
    search_columns = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class SecurityEvent(Base):
    """Security event database model"""
    __tablename__ = "security_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    client_ip = Column(String(45), nullable=False)
    event_type = Column(String(100), nullable=False)
    details = Column(Text, nullable=False)
    path = Column(String(500), nullable=True)
    method = Column(String(10), nullable=True)
    user_agent = Column(Text, nullable=True)
    severity = Column(String(20), default='medium')
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(String(255), nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_security_events_timestamp', 'timestamp'),
        Index('idx_security_events_client_ip', 'client_ip'),
        Index('idx_security_events_event_type', 'event_type'),
        Index('idx_security_events_severity', 'severity'),
    )


class SystemMetrics(Base):
    """System metrics database model"""
    __tablename__ = "system_metrics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String(50), nullable=True)
    tags = Column(JSON, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_system_metrics_timestamp', 'timestamp'),
        Index('idx_system_metrics_name', 'metric_name'),
        Index('idx_system_metrics_name_timestamp', 'metric_name', 'timestamp'),
    )


class UserSession(Base):
    """User session database model"""
    __tablename__ = "user_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(255), nullable=False, index=True)
    session_token = Column(String(500), nullable=False, unique=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    last_activity = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_user_sessions_user_id', 'user_id'),
        Index('idx_user_sessions_token', 'session_token'),
        Index('idx_user_sessions_expires_at', 'expires_at'),
    )


class AuditLog(Base):
    """Audit log database model"""
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    user_id = Column(String(255), nullable=True, index=True)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(100), nullable=True)
    resource_id = Column(String(255), nullable=True)
    details = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_audit_logs_timestamp', 'timestamp'),
        Index('idx_audit_logs_user_id', 'user_id'),
        Index('idx_audit_logs_action', 'action'),
        Index('idx_audit_logs_resource', 'resource_type', 'resource_id'),
    )
