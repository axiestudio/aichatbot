"""Enhanced features migration

Revision ID: 002_enhanced_features
Revises: 001_initial_migration
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002_enhanced_features'
down_revision = '001_initial_migration'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Update chat_messages table with new columns
    op.add_column('chat_messages', sa.Column('content', sa.Text(), nullable=False, server_default=''))
    op.add_column('chat_messages', sa.Column('role', sa.String(20), nullable=False, server_default='user'))
    op.add_column('chat_messages', sa.Column('status', sa.String(20), nullable=False, server_default='sent'))
    op.add_column('chat_messages', sa.Column('edited_at', sa.DateTime(), nullable=True))
    op.add_column('chat_messages', sa.Column('deleted_at', sa.DateTime(), nullable=True))
    op.add_column('chat_messages', sa.Column('reply_to_message_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('chat_messages', sa.Column('metadata', sa.JSON(), nullable=True))
    
    # Add foreign key for reply_to_message_id
    op.create_foreign_key(
        'fk_chat_messages_reply_to',
        'chat_messages', 'chat_messages',
        ['reply_to_message_id'], ['id']
    )
    
    # Create indexes for new columns
    op.create_index('idx_chat_messages_role', 'chat_messages', ['role'])
    op.create_index('idx_chat_messages_status', 'chat_messages', ['status'])
    
    # Create message_attachments table
    op.create_table('message_attachments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('message_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('filename', sa.String(255), nullable=False),
        sa.Column('original_filename', sa.String(255), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('mime_type', sa.String(100), nullable=False),
        sa.Column('attachment_type', sa.String(20), nullable=False),
        sa.Column('file_path', sa.String(500), nullable=False),
        sa.Column('file_hash', sa.String(64), nullable=False),
        sa.Column('url', sa.String(500), nullable=True),
        sa.Column('thumbnail_url', sa.String(500), nullable=True),
        sa.Column('uploaded_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['message_id'], ['chat_messages.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for message_attachments
    op.create_index('idx_message_attachments_message_id', 'message_attachments', ['message_id'])
    op.create_index('idx_message_attachments_type', 'message_attachments', ['attachment_type'])
    op.create_index('idx_message_attachments_hash', 'message_attachments', ['file_hash'])
    
    # Create message_reactions table
    op.create_table('message_reactions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('message_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', sa.String(255), nullable=False),
        sa.Column('emoji', sa.String(10), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['message_id'], ['chat_messages.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for message_reactions
    op.create_index('idx_message_reactions_message_id', 'message_reactions', ['message_id'])
    op.create_index('idx_message_reactions_user_id', 'message_reactions', ['user_id'])
    op.create_index('idx_message_reactions_emoji', 'message_reactions', ['emoji'])
    op.create_index('idx_message_reactions_unique', 'message_reactions', ['message_id', 'user_id', 'emoji'], unique=True)
    
    # Create websocket_connections table
    op.create_table('websocket_connections',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('connection_id', sa.String(255), nullable=False, unique=True),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', sa.String(255), nullable=True),
        sa.Column('connected_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('disconnected_at', sa.DateTime(), nullable=True),
        sa.Column('last_activity', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['chat_sessions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for websocket_connections
    op.create_index('idx_websocket_connections_session_id', 'websocket_connections', ['session_id'])
    op.create_index('idx_websocket_connections_user_id', 'websocket_connections', ['user_id'])
    op.create_index('idx_websocket_connections_active', 'websocket_connections', ['is_active'])
    op.create_index('idx_websocket_connections_connected_at', 'websocket_connections', ['connected_at'])
    
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.String(255), primary_key=True),
        sa.Column('username', sa.String(100), nullable=True, unique=True),
        sa.Column('email', sa.String(255), nullable=True, unique=True),
        sa.Column('display_name', sa.String(255), nullable=True),
        sa.Column('avatar_url', sa.String(500), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_admin', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('last_seen', sa.DateTime(), nullable=True),
        sa.Column('login_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for users
    op.create_index('idx_users_username', 'users', ['username'])
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_active', 'users', ['is_active'])
    op.create_index('idx_users_last_seen', 'users', ['last_seen'])
    
    # Create file_uploads table
    op.create_table('file_uploads',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', sa.String(255), nullable=True),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('filename', sa.String(255), nullable=False),
        sa.Column('original_filename', sa.String(255), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('mime_type', sa.String(100), nullable=False),
        sa.Column('file_hash', sa.String(64), nullable=False, unique=True),
        sa.Column('file_path', sa.String(500), nullable=False),
        sa.Column('upload_status', sa.String(20), nullable=False, server_default='uploaded'),
        sa.Column('scan_status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('scan_result', sa.JSON(), nullable=True),
        sa.Column('uploaded_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for file_uploads
    op.create_index('idx_file_uploads_user_id', 'file_uploads', ['user_id'])
    op.create_index('idx_file_uploads_hash', 'file_uploads', ['file_hash'])
    op.create_index('idx_file_uploads_status', 'file_uploads', ['upload_status'])
    op.create_index('idx_file_uploads_scan_status', 'file_uploads', ['scan_status'])
    op.create_index('idx_file_uploads_uploaded_at', 'file_uploads', ['uploaded_at'])
    
    # Update chat_configs table with new UI columns
    op.add_column('chat_configs', sa.Column('primary_color', sa.String(7), nullable=False, server_default='#3b82f6'))
    op.add_column('chat_configs', sa.Column('secondary_color', sa.String(7), nullable=False, server_default='#e5e7eb'))
    op.add_column('chat_configs', sa.Column('font_family', sa.String(100), nullable=False, server_default='Inter'))
    op.add_column('chat_configs', sa.Column('font_size', sa.Integer(), nullable=False, server_default='14'))
    op.add_column('chat_configs', sa.Column('border_radius', sa.Integer(), nullable=False, server_default='12'))
    op.add_column('chat_configs', sa.Column('position', sa.String(20), nullable=False, server_default='bottom-right'))
    op.add_column('chat_configs', sa.Column('welcome_message', sa.Text(), nullable=False, server_default='Hello! How can I help you today?'))
    op.add_column('chat_configs', sa.Column('placeholder', sa.String(255), nullable=False, server_default='Type your message...'))
    op.add_column('chat_configs', sa.Column('height', sa.Integer(), nullable=False, server_default='500'))
    op.add_column('chat_configs', sa.Column('width', sa.Integer(), nullable=False, server_default='350'))
    op.add_column('chat_configs', sa.Column('system_prompt', sa.Text(), nullable=False, server_default='You are a helpful AI assistant.'))
    op.add_column('chat_configs', sa.Column('temperature', sa.Float(), nullable=False, server_default='0.7'))
    op.add_column('chat_configs', sa.Column('max_tokens', sa.Integer(), nullable=False, server_default='1000'))
    op.add_column('chat_configs', sa.Column('model', sa.String(100), nullable=False, server_default='gpt-3.5-turbo'))
    op.add_column('chat_configs', sa.Column('use_rag', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('chat_configs', sa.Column('rag_config', sa.JSON(), nullable=True))
    
    # Update chat_sessions table with new columns
    op.add_column('chat_sessions', sa.Column('user_id', sa.String(255), nullable=True))
    op.add_column('chat_sessions', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('chat_sessions', sa.Column('last_activity', sa.DateTime(), nullable=False, server_default=sa.func.now()))
    op.add_column('chat_sessions', sa.Column('message_count', sa.Integer(), nullable=False, server_default='0'))


def downgrade() -> None:
    # Remove new columns from chat_sessions
    op.drop_column('chat_sessions', 'message_count')
    op.drop_column('chat_sessions', 'last_activity')
    op.drop_column('chat_sessions', 'is_active')
    op.drop_column('chat_sessions', 'user_id')
    
    # Remove new columns from chat_configs
    op.drop_column('chat_configs', 'rag_config')
    op.drop_column('chat_configs', 'use_rag')
    op.drop_column('chat_configs', 'model')
    op.drop_column('chat_configs', 'max_tokens')
    op.drop_column('chat_configs', 'temperature')
    op.drop_column('chat_configs', 'system_prompt')
    op.drop_column('chat_configs', 'width')
    op.drop_column('chat_configs', 'height')
    op.drop_column('chat_configs', 'placeholder')
    op.drop_column('chat_configs', 'welcome_message')
    op.drop_column('chat_configs', 'position')
    op.drop_column('chat_configs', 'border_radius')
    op.drop_column('chat_configs', 'font_size')
    op.drop_column('chat_configs', 'font_family')
    op.drop_column('chat_configs', 'secondary_color')
    op.drop_column('chat_configs', 'primary_color')
    
    # Drop tables
    op.drop_table('file_uploads')
    op.drop_table('users')
    op.drop_table('websocket_connections')
    op.drop_table('message_reactions')
    op.drop_table('message_attachments')
    
    # Remove new columns from chat_messages
    op.drop_constraint('fk_chat_messages_reply_to', 'chat_messages', type_='foreignkey')
    op.drop_column('chat_messages', 'metadata')
    op.drop_column('chat_messages', 'reply_to_message_id')
    op.drop_column('chat_messages', 'deleted_at')
    op.drop_column('chat_messages', 'edited_at')
    op.drop_column('chat_messages', 'status')
    op.drop_column('chat_messages', 'role')
    op.drop_column('chat_messages', 'content')
