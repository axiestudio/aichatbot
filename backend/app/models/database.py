from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, JSON, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

# SQLAlchemy 1.4 compatible UUID handling
try:
    from sqlalchemy.dialects.postgresql import UUID
    USE_POSTGRESQL_UUID = True
except ImportError:
    USE_POSTGRESQL_UUID = False

Base = declarative_base()


class ChatSession(Base):
    """Chat session database model"""
    __tablename__ = "chat_sessions"

    # Use String for UUID to ensure compatibility
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
    
    # Indexes
    __table_args__ = (
        Index('idx_chat_sessions_user_id', 'user_id'),
        Index('idx_chat_sessions_created_at', 'created_at'),
        Index('idx_chat_sessions_active', 'is_active'),
    )


class ChatMessage(Base):
    """Enhanced chat message database model"""
    __tablename__ = "chat_messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey('chat_sessions.id'), nullable=False)
    content = Column(Text, nullable=False)
    role = Column(String(20), nullable=False)  # user, assistant, system
    status = Column(String(20), default='sent', nullable=False)  # sending, sent, delivered, read, failed
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    edited_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)
    reply_to_message_id = Column(String(36), ForeignKey('chat_messages.id'), nullable=True)
    response_time = Column(Float, nullable=True)
    tokens_used = Column(Integer, default=0)
    config_used = Column(String(255), nullable=True)
    rag_context = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    flagged = Column(Boolean, default=False)
    metadata = Column(JSON, nullable=True)
    admin_notes = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)
    
    # Relationships
    session = relationship("ChatSession", back_populates="messages")
    attachments = relationship("MessageAttachment", back_populates="message", cascade="all, delete-orphan")
    reactions = relationship("MessageReaction", back_populates="message", cascade="all, delete-orphan")
    reply_to = relationship("ChatMessage", remote_side=[id])

    # Indexes
    __table_args__ = (
        Index('idx_chat_messages_session_id', 'session_id'),
        Index('idx_chat_messages_timestamp', 'timestamp'),
        Index('idx_chat_messages_role', 'role'),
        Index('idx_chat_messages_status', 'status'),
        Index('idx_chat_messages_flagged', 'flagged'),
    )


class MessageAttachment(Base):
    """Message attachment database model"""
    __tablename__ = "message_attachments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id = Column(UUID(as_uuid=True), ForeignKey('chat_messages.id'), nullable=False)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    attachment_type = Column(String(20), nullable=False)  # image, audio, document, video
    file_path = Column(String(500), nullable=False)
    file_hash = Column(String(64), nullable=False)
    url = Column(String(500), nullable=True)
    thumbnail_url = Column(String(500), nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    metadata = Column(JSON, nullable=True)

    # Relationships
    message = relationship("ChatMessage", back_populates="attachments")

    # Indexes
    __table_args__ = (
        Index('idx_message_attachments_message_id', 'message_id'),
        Index('idx_message_attachments_type', 'attachment_type'),
        Index('idx_message_attachments_hash', 'file_hash'),
    )


class MessageReaction(Base):
    """Message reaction database model"""
    __tablename__ = "message_reactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id = Column(UUID(as_uuid=True), ForeignKey('chat_messages.id'), nullable=False)
    user_id = Column(String(255), nullable=False)
    emoji = Column(String(10), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    message = relationship("ChatMessage", back_populates="reactions")

    # Indexes
    __table_args__ = (
        Index('idx_message_reactions_message_id', 'message_id'),
        Index('idx_message_reactions_user_id', 'user_id'),
        Index('idx_message_reactions_emoji', 'emoji'),
        Index('idx_message_reactions_unique', 'message_id', 'user_id', 'emoji', unique=True),
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
    instance_id = Column(String(255), ForeignKey('chat_instances.id'), nullable=True)  # NULL for global configs
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
    instance_id = Column(String(255), ForeignKey('chat_instances.id'), nullable=True)  # NULL for global configs
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
    table_prefix = Column(String(50), default='chatbot_')
    auto_create_tables = Column(Boolean, default=True)
    store_chat_messages = Column(Boolean, default=True)
    store_user_sessions = Column(Boolean, default=True)
    store_analytics = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


# Alias for backward compatibility
SupabaseConfig = SupabaseConfiguration


class ChatInstance(Base):
    """Chat instance model for multi-tenancy"""
    __tablename__ = "chat_instances"

    id = Column(String(255), primary_key=True)
    name = Column(String(255), nullable=False)
    subdomain = Column(String(100), unique=True, nullable=False)  # e.g., 'company1'
    domain = Column(String(255), nullable=True)  # Custom domain
    description = Column(Text, nullable=True)

    # Owner information
    owner_email = Column(String(255), nullable=False)
    owner_name = Column(String(255), nullable=False)

    # Instance settings
    is_active = Column(Boolean, default=True)
    max_monthly_messages = Column(Integer, default=1000)
    current_monthly_messages = Column(Integer, default=0)

    # Branding
    logo_url = Column(String(500), nullable=True)
    primary_color = Column(String(7), default="#3b82f6")
    secondary_color = Column(String(7), default="#e5e7eb")

    # Billing
    plan_type = Column(String(50), default="free")  # free, pro, enterprise
    billing_email = Column(String(255), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class InstanceAdmin(Base):
    """Instance admin users"""
    __tablename__ = "instance_admins"

    id = Column(String(255), primary_key=True)
    instance_id = Column(String(255), ForeignKey('chat_instances.id'), nullable=False)
    email = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)

    # Permissions
    role = Column(String(50), default="admin")  # admin, viewer
    permissions = Column(JSON, nullable=True)

    # Status
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class SuperAdmin(Base):
    """Super admin users who can manage all instances"""
    __tablename__ = "super_admins"

    id = Column(String(255), primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)

    # Super admin permissions
    can_create_instances = Column(Boolean, default=True)
    can_delete_instances = Column(Boolean, default=True)
    can_manage_billing = Column(Boolean, default=True)
    can_view_all_analytics = Column(Boolean, default=True)

    # Status
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class LiveConfiguration(Base):
    """Live configuration that updates chat interface in real-time"""
    __tablename__ = "live_configurations"

    id = Column(String(255), primary_key=True)
    instance_id = Column(String(255), ForeignKey('chat_instances.id'), nullable=False)

    # Chat Interface Configuration
    chat_title = Column(String(255), default="AI Assistant")
    chat_subtitle = Column(String(255), default="How can I help you today?")
    welcome_message = Column(Text, default="Hello! How can I assist you today?")
    placeholder_text = Column(String(255), default="Type your message...")

    # Visual Configuration
    primary_color = Column(String(7), default="#3b82f6")
    secondary_color = Column(String(7), default="#e5e7eb")
    accent_color = Column(String(7), default="#10b981")
    background_color = Column(String(7), default="#ffffff")
    text_color = Column(String(7), default="#1f2937")

    # Branding
    logo_url = Column(String(500), nullable=True)
    company_name = Column(String(255), nullable=True)
    show_branding = Column(Boolean, default=True)
    custom_css = Column(Text, nullable=True)

    # Behavior Configuration
    typing_indicator = Column(Boolean, default=True)
    sound_enabled = Column(Boolean, default=False)
    auto_scroll = Column(Boolean, default=True)
    message_timestamps = Column(Boolean, default=True)

    # Chat Features
    file_upload_enabled = Column(Boolean, default=True)
    max_file_size_mb = Column(Integer, default=10)
    allowed_file_types = Column(JSON, default=lambda: ["pdf", "txt", "docx", "jpg", "png"])

    # Rate Limiting
    messages_per_minute = Column(Integer, default=10)
    messages_per_hour = Column(Integer, default=100)

    # Advanced Features
    conversation_starters = Column(JSON, default=lambda: [])
    quick_replies = Column(JSON, default=lambda: [])
    custom_fields = Column(JSON, default=lambda: {})

    # Status
    is_active = Column(Boolean, default=True)
    last_updated_by = Column(String(255), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class ConfigurationHistory(Base):
    """Track configuration changes for audit and rollback"""
    __tablename__ = "configuration_history"

    id = Column(String(255), primary_key=True)
    instance_id = Column(String(255), ForeignKey('chat_instances.id'), nullable=False)
    configuration_id = Column(String(255), ForeignKey('live_configurations.id'), nullable=False)

    # Change tracking
    changed_by = Column(String(255), nullable=False)  # Admin ID
    change_type = Column(String(50), nullable=False)  # create, update, delete
    changes = Column(JSON, nullable=False)  # What changed
    previous_values = Column(JSON, nullable=True)  # Previous values

    # Metadata
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


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


class WebSocketConnectionDB(Base):
    """WebSocket connection tracking"""
    __tablename__ = "websocket_connections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    connection_id = Column(String(255), nullable=False, unique=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey('chat_sessions.id'), nullable=False)
    user_id = Column(String(255), nullable=True)
    connected_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    disconnected_at = Column(DateTime, nullable=True)
    last_activity = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)

    # Relationships
    session = relationship("ChatSession")

    # Indexes
    __table_args__ = (
        Index('idx_websocket_connections_session_id', 'session_id'),
        Index('idx_websocket_connections_user_id', 'user_id'),
        Index('idx_websocket_connections_active', 'is_active'),
        Index('idx_websocket_connections_connected_at', 'connected_at'),
    )


class User(Base):
    """User database model"""
    __tablename__ = "users"

    id = Column(String(255), primary_key=True)
    username = Column(String(100), nullable=True, unique=True)
    email = Column(String(255), nullable=True, unique=True)
    display_name = Column(String(255), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_seen = Column(DateTime, nullable=True)
    login_count = Column(Integer, default=0, nullable=False)
    metadata = Column(JSON, nullable=True)

    # Indexes
    __table_args__ = (
        Index('idx_users_username', 'username'),
        Index('idx_users_email', 'email'),
        Index('idx_users_active', 'is_active'),
        Index('idx_users_last_seen', 'last_seen'),
    )


class FileUploadDB(Base):
    """File upload tracking"""
    __tablename__ = "file_uploads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(255), nullable=True)
    session_id = Column(UUID(as_uuid=True), nullable=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    file_hash = Column(String(64), nullable=False, unique=True)
    file_path = Column(String(500), nullable=False)
    upload_status = Column(String(20), default='uploaded', nullable=False)
    scan_status = Column(String(20), default='pending', nullable=False)
    scan_result = Column(JSON, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    processed_at = Column(DateTime, nullable=True)
    metadata = Column(JSON, nullable=True)

    # Indexes
    __table_args__ = (
        Index('idx_file_uploads_user_id', 'user_id'),
        Index('idx_file_uploads_hash', 'file_hash'),
        Index('idx_file_uploads_status', 'upload_status'),
        Index('idx_file_uploads_scan_status', 'scan_status'),
        Index('idx_file_uploads_uploaded_at', 'uploaded_at'),
    )
