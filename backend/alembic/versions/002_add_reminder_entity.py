"""Add reminder entity

Revision ID: 002_add_reminder_entity
Revises: 001_add_task_recurrence
Create Date: 2026-02-11

This migration creates the Reminder table for intelligent time-based reminders
scheduled via Dapr Jobs API.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '002_add_reminder_entity'
down_revision = '001_add_task_recurrence'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create reminder table
    op.create_table(
        'reminder',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('scheduled_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='scheduled'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('dapr_job_name', sa.String(255), nullable=False),
        sa.Column('correlation_id', postgresql.UUID(as_uuid=True), nullable=True),
    )

    # Add foreign keys
    op.create_foreign_key(
        'fk_reminder_task_id',
        'reminder',
        'task',
        ['task_id'],
        ['id'],
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'fk_reminder_user_id',
        'reminder',
        'user',
        ['user_id'],
        ['id'],
        ondelete='CASCADE'
    )

    # Create indexes for performance
    op.create_index('ix_reminder_task_id', 'reminder', ['task_id'])
    op.create_index('ix_reminder_user_id', 'reminder', ['user_id'])
    op.create_index('ix_reminder_status', 'reminder', ['status'])
    op.create_index('ix_reminder_scheduled_time', 'reminder', ['scheduled_time'])
    op.create_index('ix_reminder_dapr_job_name', 'reminder', ['dapr_job_name'], unique=True)
    op.create_index('ix_reminder_user_id_status', 'reminder', ['user_id', 'status'])

    # Add check constraint for status
    op.create_check_constraint(
        'ck_reminder_status',
        'reminder',
        "status IN ('scheduled', 'sent', 'cancelled')"
    )

    # Add check constraint for scheduled_time (must be in the future at creation)
    # Note: This is enforced at application level, not database level


def downgrade() -> None:
    # Remove check constraint
    op.drop_constraint('ck_reminder_status', 'reminder', type_='check')

    # Remove indexes
    op.drop_index('ix_reminder_user_id_status', 'reminder')
    op.drop_index('ix_reminder_dapr_job_name', 'reminder')
    op.drop_index('ix_reminder_scheduled_time', 'reminder')
    op.drop_index('ix_reminder_status', 'reminder')
    op.drop_index('ix_reminder_user_id', 'reminder')
    op.drop_index('ix_reminder_task_id', 'reminder')

    # Remove foreign keys
    op.drop_constraint('fk_reminder_user_id', 'reminder', type_='foreignkey')
    op.drop_constraint('fk_reminder_task_id', 'reminder', type_='foreignkey')

    # Drop table
    op.drop_table('reminder')
