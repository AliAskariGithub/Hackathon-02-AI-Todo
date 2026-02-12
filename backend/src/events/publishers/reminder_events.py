"""
Event publishers for reminder-related events.

Publishes events to Dapr Pub/Sub for reminder lifecycle.
"""

from datetime import datetime
from uuid import UUID
from typing import Dict, Any

from backend.src.dapr_sdk_utils.pubsub import publish_event
from backend.src.events.schema import EventSchema


# Topic constants
TOPIC_REMINDER_SCHEDULED = "todo.reminder.scheduled"
TOPIC_REMINDER_FIRED = "todo.reminder.fired"
TOPIC_REMINDER_CANCELLED = "todo.reminder.cancelled"


async def publish_reminder_scheduled(
    reminder_id: UUID,
    task_id: UUID,
    user_id: UUID,
    scheduled_time: datetime,
    correlation_id: UUID
) -> None:
    """
    Publish event when a reminder is scheduled.

    Args:
        reminder_id: The reminder ID
        task_id: The task ID
        user_id: The user ID
        scheduled_time: When the reminder will fire
        correlation_id: Correlation ID for tracing
    """
    event = EventSchema(
        event_type="reminder.scheduled",
        payload={
            "reminder_id": str(reminder_id),
            "task_id": str(task_id),
            "scheduled_time": scheduled_time.isoformat(),
        },
        user_id=user_id,
        timestamp=datetime.utcnow(),
        correlation_id=correlation_id
    )

    await publish_event(
        topic=TOPIC_REMINDER_SCHEDULED,
        event=event
    )


async def publish_reminder_fired(
    reminder_id: UUID,
    task_id: UUID,
    user_id: UUID,
    fired_at: datetime,
    correlation_id: UUID
) -> None:
    """
    Publish event when a reminder fires.

    Args:
        reminder_id: The reminder ID
        task_id: The task ID
        user_id: The user ID
        fired_at: When the reminder fired
        correlation_id: Correlation ID for tracing
    """
    event = EventSchema(
        event_type="reminder.fired",
        payload={
            "reminder_id": str(reminder_id),
            "task_id": str(task_id),
            "fired_at": fired_at.isoformat(),
        },
        user_id=user_id,
        timestamp=datetime.utcnow(),
        correlation_id=correlation_id
    )

    await publish_event(
        topic=TOPIC_REMINDER_FIRED,
        event=event
    )


async def publish_reminder_cancelled(
    reminder_id: UUID,
    task_id: UUID,
    user_id: UUID,
    correlation_id: UUID
) -> None:
    """
    Publish event when a reminder is cancelled.

    Args:
        reminder_id: The reminder ID
        task_id: The task ID
        user_id: The user ID
        correlation_id: Correlation ID for tracing
    """
    event = EventSchema(
        event_type="reminder.cancelled",
        payload={
            "reminder_id": str(reminder_id),
            "task_id": str(task_id),
        },
        user_id=user_id,
        timestamp=datetime.utcnow(),
        correlation_id=correlation_id
    )

    await publish_event(
        topic=TOPIC_REMINDER_CANCELLED,
        event=event
    )
