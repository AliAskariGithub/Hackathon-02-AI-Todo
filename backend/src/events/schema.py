"""
Event Schema for Phase-V Event-Driven Architecture

This module defines the standardized event schema for all events published
via Dapr Pub/Sub. All events must conform to this schema to ensure consistency
across the system.

Event Types:
- todo.task.created: Task creation event
- todo.task.updated: Task update event
- todo.task.completed: Task completion event (triggers recurring task generation)
- todo.task.deleted: Task deletion event
- todo.task.priority_changed: Task priority change event
- todo.reminder.scheduled: Reminder scheduled event
- todo.reminder.fired: Reminder delivery event
- todo.reminder.cancelled: Reminder cancellation event
"""

from datetime import datetime
from typing import Any, Dict, Optional, Literal
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class EventSchema(BaseModel):
    """
    Standardized event schema for all Dapr Pub/Sub events.

    All events published to the event bus must conform to this schema
    to ensure consistency and enable distributed tracing.
    """
    event_type: str = Field(
        ...,
        description="Event type identifier (e.g., 'todo.task.created')",
        pattern="^[a-z]+\\.[a-z]+\\.[a-z_]+$"
    )
    payload: Dict[str, Any] = Field(
        ...,
        description="Event-specific data payload"
    )
    user_id: UUID = Field(
        ...,
        description="User ID associated with this event"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Event creation timestamp (UTC)"
    )
    correlation_id: UUID = Field(
        default_factory=uuid4,
        description="Correlation ID for distributed tracing and idempotency"
    )

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


class TaskCreatedEvent(EventSchema):
    """Event published when a new task is created."""
    event_type: Literal["todo.task.created"] = "todo.task.created"


class TaskUpdatedEvent(EventSchema):
    """Event published when a task is updated."""
    event_type: Literal["todo.task.updated"] = "todo.task.updated"


class TaskCompletedEvent(EventSchema):
    """
    Event published when a task is marked as completed.

    This event triggers recurring task generation if the task has
    a recurrence pattern defined.
    """
    event_type: Literal["todo.task.completed"] = "todo.task.completed"


class TaskDeletedEvent(EventSchema):
    """Event published when a task is deleted."""
    event_type: Literal["todo.task.deleted"] = "todo.task.deleted"


class TaskPriorityChangedEvent(EventSchema):
    """Event published when a task's priority is changed."""
    event_type: Literal["todo.task.priority_changed"] = "todo.task.priority_changed"


class ReminderScheduledEvent(EventSchema):
    """Event published when a reminder is scheduled via Dapr Jobs API."""
    event_type: Literal["todo.reminder.scheduled"] = "todo.reminder.scheduled"


class ReminderFiredEvent(EventSchema):
    """Event published when a reminder is delivered."""
    event_type: Literal["todo.reminder.fired"] = "todo.reminder.fired"


class ReminderCancelledEvent(EventSchema):
    """Event published when a reminder is cancelled."""
    event_type: Literal["todo.reminder.cancelled"] = "todo.reminder.cancelled"


def create_event(
    event_type: str,
    payload: Dict[str, Any],
    user_id: UUID,
    correlation_id: Optional[UUID] = None
) -> EventSchema:
    """
    Factory function to create standardized events.

    Args:
        event_type: Event type identifier (e.g., 'todo.task.created')
        payload: Event-specific data
        user_id: User ID associated with the event
        correlation_id: Optional correlation ID (generated if not provided)

    Returns:
        EventSchema instance with standardized format

    Example:
        >>> event = create_event(
        ...     event_type="todo.task.created",
        ...     payload={"task_id": "123", "title": "Buy groceries"},
        ...     user_id=UUID("user-uuid")
        ... )
    """
    return EventSchema(
        event_type=event_type,
        payload=payload,
        user_id=user_id,
        correlation_id=correlation_id or uuid4()
    )
