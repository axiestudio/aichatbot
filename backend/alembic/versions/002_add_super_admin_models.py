"""Add super admin and multi-tenancy models

Revision ID: 002
Revises: 001
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # Create chat_instances table
    op.create_table('chat_instances',
        sa.Column('id', sa.String(255), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('subdomain', sa.String(100), nullable=False),
        sa.Column('domain', sa.String(255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('owner_email', sa.String(255), nullable=False),
        sa.Column('owner_name', sa.String(255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('max_monthly_messages', sa.Integer(), nullable=True, default=1000),
        sa.Column('current_monthly_messages', sa.Integer(), nullable=True, default=0),
        sa.Column('logo_url', sa.String(500), nullable=True),
        sa.Column('primary_color', sa.String(7), nullable=True, default='#3b82f6'),
        sa.Column('secondary_color', sa.String(7), nullable=True, default='#e5e7eb'),
        sa.Column('plan_type', sa.String(50), nullable=True, default='free'),
        sa.Column('billing_email', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('subdomain')
    )

    # Create super_admins table
    op.create_table('super_admins',
        sa.Column('id', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('can_create_instances', sa.Boolean(), nullable=True, default=True),
        sa.Column('can_delete_instances', sa.Boolean(), nullable=True, default=True),
        sa.Column('can_manage_billing', sa.Boolean(), nullable=True, default=True),
        sa.Column('can_view_all_analytics', sa.Boolean(), nullable=True, default=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )

    # Create instance_admins table
    op.create_table('instance_admins',
        sa.Column('id', sa.String(255), nullable=False),
        sa.Column('instance_id', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('role', sa.String(50), nullable=True, default='admin'),
        sa.Column('permissions', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['instance_id'], ['chat_instances.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Add instance_id to existing tables for multi-tenancy
    op.add_column('api_configurations', sa.Column('instance_id', sa.String(255), nullable=True))
    op.add_column('rag_instructions', sa.Column('instance_id', sa.String(255), nullable=True))

    # Create foreign key constraints
    op.create_foreign_key(
        'fk_api_configurations_instance_id',
        'api_configurations', 'chat_instances',
        ['instance_id'], ['id']
    )
    op.create_foreign_key(
        'fk_rag_instructions_instance_id',
        'rag_instructions', 'chat_instances',
        ['instance_id'], ['id']
    )

    # Create live_configurations table
    op.create_table('live_configurations',
        sa.Column('id', sa.String(255), nullable=False),
        sa.Column('instance_id', sa.String(255), nullable=False),
        sa.Column('chat_title', sa.String(255), nullable=True, default='AI Assistant'),
        sa.Column('chat_subtitle', sa.String(255), nullable=True, default='How can I help you today?'),
        sa.Column('welcome_message', sa.Text(), nullable=True, default='Hello! How can I assist you today?'),
        sa.Column('placeholder_text', sa.String(255), nullable=True, default='Type your message...'),
        sa.Column('primary_color', sa.String(7), nullable=True, default='#3b82f6'),
        sa.Column('secondary_color', sa.String(7), nullable=True, default='#e5e7eb'),
        sa.Column('accent_color', sa.String(7), nullable=True, default='#10b981'),
        sa.Column('background_color', sa.String(7), nullable=True, default='#ffffff'),
        sa.Column('text_color', sa.String(7), nullable=True, default='#1f2937'),
        sa.Column('logo_url', sa.String(500), nullable=True),
        sa.Column('company_name', sa.String(255), nullable=True),
        sa.Column('show_branding', sa.Boolean(), nullable=True, default=True),
        sa.Column('custom_css', sa.Text(), nullable=True),
        sa.Column('typing_indicator', sa.Boolean(), nullable=True, default=True),
        sa.Column('sound_enabled', sa.Boolean(), nullable=True, default=False),
        sa.Column('auto_scroll', sa.Boolean(), nullable=True, default=True),
        sa.Column('message_timestamps', sa.Boolean(), nullable=True, default=True),
        sa.Column('file_upload_enabled', sa.Boolean(), nullable=True, default=True),
        sa.Column('max_file_size_mb', sa.Integer(), nullable=True, default=10),
        sa.Column('allowed_file_types', sa.JSON(), nullable=True),
        sa.Column('messages_per_minute', sa.Integer(), nullable=True, default=10),
        sa.Column('messages_per_hour', sa.Integer(), nullable=True, default=100),
        sa.Column('conversation_starters', sa.JSON(), nullable=True),
        sa.Column('quick_replies', sa.JSON(), nullable=True),
        sa.Column('custom_fields', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('last_updated_by', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['instance_id'], ['chat_instances.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create configuration_history table
    op.create_table('configuration_history',
        sa.Column('id', sa.String(255), nullable=False),
        sa.Column('instance_id', sa.String(255), nullable=False),
        sa.Column('configuration_id', sa.String(255), nullable=False),
        sa.Column('changed_by', sa.String(255), nullable=False),
        sa.Column('change_type', sa.String(50), nullable=False),
        sa.Column('changes', sa.JSON(), nullable=False),
        sa.Column('previous_values', sa.JSON(), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['instance_id'], ['chat_instances.id'], ),
        sa.ForeignKeyConstraint(['configuration_id'], ['live_configurations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for performance
    op.create_index('idx_chat_instances_subdomain', 'chat_instances', ['subdomain'])
    op.create_index('idx_chat_instances_owner_email', 'chat_instances', ['owner_email'])
    op.create_index('idx_chat_instances_plan_type', 'chat_instances', ['plan_type'])
    op.create_index('idx_instance_admins_instance_id', 'instance_admins', ['instance_id'])
    op.create_index('idx_instance_admins_email', 'instance_admins', ['email'])
    op.create_index('idx_api_configurations_instance_id', 'api_configurations', ['instance_id'])
    op.create_index('idx_rag_instructions_instance_id', 'rag_instructions', ['instance_id'])
    op.create_index('idx_live_configurations_instance_id', 'live_configurations', ['instance_id'])
    op.create_index('idx_configuration_history_instance_id', 'configuration_history', ['instance_id'])
    op.create_index('idx_configuration_history_config_id', 'configuration_history', ['configuration_id'])


def downgrade():
    # Drop indexes
    op.drop_index('idx_configuration_history_config_id', table_name='configuration_history')
    op.drop_index('idx_configuration_history_instance_id', table_name='configuration_history')
    op.drop_index('idx_live_configurations_instance_id', table_name='live_configurations')
    op.drop_index('idx_rag_instructions_instance_id', table_name='rag_instructions')
    op.drop_index('idx_api_configurations_instance_id', table_name='api_configurations')
    op.drop_index('idx_instance_admins_email', table_name='instance_admins')
    op.drop_index('idx_instance_admins_instance_id', table_name='instance_admins')
    op.drop_index('idx_chat_instances_plan_type', table_name='chat_instances')
    op.drop_index('idx_chat_instances_owner_email', table_name='chat_instances')
    op.drop_index('idx_chat_instances_subdomain', table_name='chat_instances')

    # Drop foreign key constraints
    op.drop_constraint('fk_rag_instructions_instance_id', 'rag_instructions', type_='foreignkey')
    op.drop_constraint('fk_api_configurations_instance_id', 'api_configurations', type_='foreignkey')

    # Remove instance_id columns
    op.drop_column('rag_instructions', 'instance_id')
    op.drop_column('api_configurations', 'instance_id')

    # Drop tables
    op.drop_table('configuration_history')
    op.drop_table('live_configurations')
    op.drop_table('instance_admins')
    op.drop_table('super_admins')
    op.drop_table('chat_instances')
