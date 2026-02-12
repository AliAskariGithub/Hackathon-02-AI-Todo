"""
Reminder model with Dapr Jobs API integration.

Represents a scheduled reminder for a task with exact-time delivery.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel, Relationship


class ReminderBase(SQLModel):
    """Base Reminder model with shared fields."""
    task_id: UUID = Field(foreign_key="task.id", index=True)
    user_id: UUID = Field(index=True)
    scheduled_time: datetime = Field(index=True)
    status: str = Field(default="scheduled")  # scheduled | sent | cancelled
    dapr_job_name: Optional[str] = Field(default=None)
    correlation_id: Optional[UUID] = Field(default=None, index=True)


class Reminder(ReminderBase, table=True):
    """Reminder entity stored in database."""
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    sent_at: Optional[datetime] = Field(default=None)

    # Relationship to Task
    # task: Optional["Task"] = Relationship(back_populates="reminders")


class ReminderCreate(ReminderBase):
    """Schema for creating a new reminder."""
    pass


class ReminderUpdate(SQLModel):
    """Schema for updating a reminder."""
    scheduled_time: Optional[datetime] = None
    status: Optional[str] = None


class ReminderRead(ReminderBase):
    """Schema for reading a reminder."""
    id: UUID
    created_at: datetime
    sent_at: Optional[datetime]


def validate_reminder_time(scheduled_time: datetime) -> None:
    """
    Validate that reminder time is in the future and at least 1 minute ahead.

    Args:
        scheduled_time: The scheduled time for the reminder

    Raises:
        ValueError: If scheduled time is invalid
    """
    now = datetime.utcnow()

    if scheduled_time <= now:
        raise ValueError("Scheduled time must be in the future")

    min_time = now + timedelta(minutes=1)
    if scheduled_time < min_time:
        raise ValueError("Scheduled time must be at least 1 minute in the future")


def generate_dapr_job_name(reminder_id: UUID, user_id: UUID) -> str:
    """
    Generate a unique Dapr Job name for a reminder.

    Args:
        reminder_id: The reminder ID
        user_id: The user ID

    Returns:
        Unique job name for Dapr Jobs API
    """
    return f"reminder-{user_id}-{reminder_id}"
