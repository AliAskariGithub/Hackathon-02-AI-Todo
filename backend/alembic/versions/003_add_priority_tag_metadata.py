"""Add priority and tag metadata tables

Revision ID: 003_add_priority_tag_metadata
Revises: 002_add_reminder_entity
Create Date: 2026-02-11

This migration creates metadata tables for Priority levels and Tags.
Note: Priority and Tags are already added to the Task table in migration 001.
This migration adds helper tables for:
- Priority level definitions (for UI display)
- Tag suggestions (for autocomplete)
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '003_add_priority_tag_metadata'
down_revision = '002_add_reminder_entity'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create priority_level table for metadata
    op.create_table(
        'priority_level',
        sa.Column('name', sa.String(10), primary_key=True),
        sa.Column('display_name', sa.String(50), nullable=False),
        sa.Column('color', sa.String(20), nullable=False),
        sa.Column('sort_order', sa.Integer(), nullable=False),
        sa.Column('description', sa.String(255), nullable=True),
    )

    # Insert default priority levels
    op.execute("""
        INSERT INTO priority_level (name, display_name, color, sort_order, description) VALUES
        ('High', 'High Priority', 'red', 1, 'Urgent tasks requiring immediate attention'),
        ('Medium', 'Medium Priority', 'yellow', 2, 'Important tasks with moderate urgency'),
        ('Low', 'Low Priority', 'green', 3, 'Tasks that can be completed when time permits')
    """)

    # Create tag_suggestion table for autocomplete
    op.create_table(
        'tag_suggestion',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tag_name', sa.String(50), nullable=False),
        sa.Column('usage_count', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # Add foreign key for user_id
    op.create_foreign_key(
        'fk_tag_suggestion_user_id',
        'tag_suggestion',
        'user',
        ['user_id'],
        ['id'],
        ondelete='CASCADE'
    )

    # Create indexes for tag suggestions
    op.create_index('ix_tag_suggestion_user_id', 'tag_suggestion', ['user_id'])
    op.create_index('ix_tag_suggestion_tag_name', 'tag_suggestion', ['tag_name'])
    op.create_index('ix_tag_suggestion_user_id_tag_name', 'tag_suggestion', ['user_id', 'tag_name'], unique=True)
    op.create_index('ix_tag_suggestion_usage_count', 'tag_suggestion', ['usage_count'])

    # Create a view for popular tags per user
    op.execute("""
        CREATE VIEW user_popular_tags AS
        SELECT
            user_id,
            tag_name,
            usage_count,
            last_used_at
        FROM tag_suggestion
        ORDER BY user_id, usage_count DESC, last_used_at DESC
    """)


def downgrade() -> None:
    # Drop view
    op.execute("DROP VIEW IF EXISTS user_popular_tags")

    # Remove indexes
    op.drop_index('ix_tag_suggestion_usage_count', 'tag_suggestion')
    op.drop_index('ix_tag_suggestion_user_id_tag_name', 'tag_suggestion')
    op.drop_index('ix_tag_suggestion_tag_name', 'tag_suggestion')
    op.drop_index('ix_tag_suggestion_user_id', 'tag_suggestion')

    # Remove foreign key
    op.drop_constraint('fk_tag_suggestion_user_id', 'tag_suggestion', type_='foreignkey')

    # Drop tables
    op.drop_table('tag_suggestion')
    op.drop_table('priority_level')
