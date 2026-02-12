"""Add task recurrence fields

Revision ID: 001_add_task_recurrence
Revises:
Create Date: 2026-02-11

This migration adds recurrence-related fields to the Task table:
- status (replaces completed boolean)
- priority (High/Medium/Low)
- due_date
- recurrence (Daily/Weekly/Monthly)
- recurrence_day_of_week (0-6 for Weekly)
- recurrence_day_of_month (1-31 for Monthly)
- tags (array of strings)
- completed_at
- parent_task_id (for recurring task chains)
- correlation_id (for event tracking)
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '001_add_task_recurrence'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns to task table

    # 1. Add status column (will replace completed boolean)
    op.add_column('task', sa.Column('status', sa.String(20), nullable=True))

    # 2. Migrate existing completed boolean to status
    # completed=True -> status='completed'
    # completed=False -> status='pending'
    op.execute("""
        UPDATE task
        SET status = CASE
            WHEN completed = true THEN 'completed'
            ELSE 'pending'
        END
    """)

    # 3. Make status non-nullable and add default
    op.alter_column('task', 'status', nullable=False, server_default='pending')

    # 4. Add priority column
    op.add_column('task', sa.Column('priority', sa.String(10), nullable=False, server_default='Medium'))

    # 5. Add due_date column
    op.add_column('task', sa.Column('due_date', sa.DateTime(timezone=True), nullable=True))

    # 6. Add recurrence columns
    op.add_column('task', sa.Column('recurrence', sa.String(10), nullable=True))
    op.add_column('task', sa.Column('recurrence_day_of_week', sa.Integer(), nullable=True))
    op.add_column('task', sa.Column('recurrence_day_of_month', sa.Integer(), nullable=True))

    # 7. Add tags column (PostgreSQL array)
    op.add_column('task', sa.Column('tags', postgresql.ARRAY(sa.String(50)), nullable=True, server_default='{}'))

    # 8. Add completed_at column
    op.add_column('task', sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True))

    # 9. Migrate completed_at for existing completed tasks
    op.execute("""
        UPDATE task
        SET completed_at = updated_at
        WHERE status = 'completed' AND completed_at IS NULL
    """)

    # 10. Add parent_task_id for recurring task chains
    op.add_column('task', sa.Column('parent_task_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key('fk_task_parent_task_id', 'task', 'task', ['parent_task_id'], ['id'], ondelete='SET NULL')

    # 11. Add correlation_id for event tracking
    op.add_column('task', sa.Column('correlation_id', postgresql.UUID(as_uuid=True), nullable=True))

    # 12. Create indexes for performance
    op.create_index('ix_task_status', 'task', ['status'])
    op.create_index('ix_task_priority', 'task', ['priority'])
    op.create_index('ix_task_due_date', 'task', ['due_date'])
    op.create_index('ix_task_recurrence', 'task', ['recurrence'])
    op.create_index('ix_task_user_id_status', 'task', ['user_id', 'status'])
    op.create_index('ix_task_correlation_id', 'task', ['correlation_id'])

    # 13. Add check constraints
    op.create_check_constraint(
        'ck_task_status',
        'task',
        "status IN ('pending', 'in_progress', 'completed', 'deleted')"
    )
    op.create_check_constraint(
        'ck_task_priority',
        'task',
        "priority IN ('High', 'Medium', 'Low')"
    )
    op.create_check_constraint(
        'ck_task_recurrence',
        'task',
        "recurrence IS NULL OR recurrence IN ('Daily', 'Weekly', 'Monthly')"
    )
    op.create_check_constraint(
        'ck_task_recurrence_day_of_week',
        'task',
        "recurrence_day_of_week IS NULL OR (recurrence_day_of_week >= 0 AND recurrence_day_of_week <= 6)"
    )
    op.create_check_constraint(
        'ck_task_recurrence_day_of_month',
        'task',
        "recurrence_day_of_month IS NULL OR (recurrence_day_of_month >= 1 AND recurrence_day_of_month <= 31)"
    )


def downgrade() -> None:
    # Remove check constraints
    op.drop_constraint('ck_task_recurrence_day_of_month', 'task', type_='check')
    op.drop_constraint('ck_task_recurrence_day_of_week', 'task', type_='check')
    op.drop_constraint('ck_task_recurrence', 'task', type_='check')
    op.drop_constraint('ck_task_priority', 'task', type_='check')
    op.drop_constraint('ck_task_status', 'task', type_='check')

    # Remove indexes
    op.drop_index('ix_task_correlation_id', 'task')
    op.drop_index('ix_task_user_id_status', 'task')
    op.drop_index('ix_task_recurrence', 'task')
    op.drop_index('ix_task_due_date', 'task')
    op.drop_index('ix_task_priority', 'task')
    op.drop_index('ix_task_status', 'task')

    # Remove foreign key
    op.drop_constraint('fk_task_parent_task_id', 'task', type_='foreignkey')

    # Remove columns
    op.drop_column('task', 'correlation_id')
    op.drop_column('task', 'parent_task_id')
    op.drop_column('task', 'completed_at')
    op.drop_column('task', 'tags')
    op.drop_column('task', 'recurrence_day_of_month')
    op.drop_column('task', 'recurrence_day_of_week')
    op.drop_column('task', 'recurrence')
    op.drop_column('task', 'due_date')
    op.drop_column('task', 'priority')
    op.drop_column('task', 'status')
