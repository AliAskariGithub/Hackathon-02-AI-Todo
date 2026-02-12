"""
Dapr Pub/Sub API Utility Functions

This module provides utility functions for publishing and subscribing to events
via Dapr Pub/Sub. It enables event-driven architecture with cloud-agnostic
message broker abstraction.

Key Features:
- Publish events to topics
- Subscribe to topics with decorators
- Automatic event serialization
- Correlation ID propagation
- Dead letter queue support
"""

from typing import Any, Callable, Dict, Optional
from uuid import UUID
import json
import os
from pydantic import BaseModel

from ..events.schema import EventSchema, create_event

# Check if Dapr is enabled
ENABLE_DAPR = os.getenv("ENABLE_DAPR", "false").lower() == "true"

if ENABLE_DAPR:
    from dapr.clients import DaprClient
    from dapr.ext.fastapi import DaprApp
else:
    # Mock implementations for local development without Dapr
    DaprClient = None
    DaprApp = None


class DaprPubSub:
    """
    Wrapper for Dapr Pub/Sub operations.

    Provides methods for publishing events and managing subscriptions.
    """

    def __init__(self, pubsub_name: str = "pubsub"):
        """
        Initialize Dapr Pub/Sub client.

        Args:
            pubsub_name: Name of the Dapr Pub/Sub component (default: "pubsub")
        """
        self.pubsub_name = pubsub_name
        self.enabled = ENABLE_DAPR

        if self.enabled and DaprClient:
            self.client = DaprClient()
        else:
            self.client = None
            print("[WARNING] Dapr is disabled - events will be logged but not published")

    def publish_event(
        self,
        topic: str,
        event: EventSchema,
        metadata: Optional[Dict[str, str]] = None
    ) -> None:
        """
        Publish an event to a topic.

        Args:
            topic: Topic name (e.g., "todo.task.created")
            event: Event conforming to EventSchema
            metadata: Optional metadata for the event

        Example:
            >>> pubsub = DaprPubSub()
            >>> event = create_event(
            ...     event_type="todo.task.created",
            ...     payload={"task_id": "123", "title": "Buy groceries"},
            ...     user_id=UUID("user-uuid")
            ... )
            >>> pubsub.publish_event("todo.task.created", event)
        """
        # If Dapr is disabled, just log the event
        if not self.enabled or not self.client:
            print(f"[Event Log] {topic}: {event.event_type}")
            return

        # Serialize event to JSON
        event_data = event.model_dump()

        # Add correlation ID to metadata for distributed tracing
        if metadata is None:
            metadata = {}
        metadata["correlation_id"] = str(event.correlation_id)

        self.client.publish_event(
            pubsub_name=self.pubsub_name,
            topic_name=topic,
            data=json.dumps(event_data),
            data_content_type="application/json",
            metadata=metadata
        )

    def publish_task_created(
        self,
        task_id: UUID,
        user_id: UUID,
        task_data: Dict[str, Any],
        correlation_id: Optional[UUID] = None
    ) -> None:
        """
        Convenience method to publish task.created event.

        Args:
            task_id: Task ID
            user_id: User ID
            task_data: Task data payload
            correlation_id: Optional correlation ID
        """
        event = create_event(
            event_type="todo.task.created",
            payload={"task_id": str(task_id), **task_data},
            user_id=user_id,
            correlation_id=correlation_id
        )
        self.publish_event("todo.task.created", event)

    def publish_task_completed(
        self,
        task_id: UUID,
        user_id: UUID,
        task_data: Dict[str, Any],
        correlation_id: Optional[UUID] = None
    ) -> None:
        """
        Convenience method to publish task.completed event.

        This event triggers recurring task generation if the task has
        a recurrence pattern.

        Args:
            task_id: Task ID
            user_id: User ID
            task_data: Task data payload (must include recurrence info)
            correlation_id: Optional correlation ID
        """
        event = create_event(
            event_type="todo.task.completed",
            payload={"task_id": str(task_id), **task_data},
            user_id=user_id,
            correlation_id=correlation_id
        )
        self.publish_event("todo.task.completed", event)

    def publish_task_updated(
        self,
        task_id: UUID,
        user_id: UUID,
        task_data: Dict[str, Any],
        correlation_id: Optional[UUID] = None
    ) -> None:
        """
        Convenience method to publish task.updated event.

        Args:
            task_id: Task ID
            user_id: User ID
            task_data: Task data payload
            correlation_id: Optional correlation ID
        """
        event = create_event(
            event_type="todo.task.updated",
            payload={"task_id": str(task_id), **task_data},
            user_id=user_id,
            correlation_id=correlation_id
        )
        self.publish_event("todo.task.updated", event)

    def publish_task_deleted(
        self,
        task_id: UUID,
        user_id: UUID,
        correlation_id: Optional[UUID] = None
    ) -> None:
        """
        Convenience method to publish task.deleted event.

        Args:
            task_id: Task ID
            user_id: User ID
            correlation_id: Optional correlation ID
        """
        event = create_event(
            event_type="todo.task.deleted",
            payload={"task_id": str(task_id)},
            user_id=user_id,
            correlation_id=correlation_id
        )
        self.publish_event("todo.task.deleted", event)

    def publish_reminder_scheduled(
        self,
        reminder_id: UUID,
        task_id: UUID,
        user_id: UUID,
        scheduled_time: str,
        correlation_id: Optional[UUID] = None
    ) -> None:
        """
        Convenience method to publish reminder.scheduled event.

        Args:
            reminder_id: Reminder ID
            task_id: Associated task ID
            user_id: User ID
            scheduled_time: ISO 8601 timestamp
            correlation_id: Optional correlation ID
        """
        event = create_event(
            event_type="todo.reminder.scheduled",
            payload={
                "reminder_id": str(reminder_id),
                "task_id": str(task_id),
                "scheduled_time": scheduled_time
            },
            user_id=user_id,
            correlation_id=correlation_id
        )
        self.publish_event("todo.reminder.scheduled", event)

    def publish_reminder_fired(
        self,
        reminder_id: UUID,
        task_id: UUID,
        user_id: UUID,
        correlation_id: Optional[UUID] = None
    ) -> None:
        """
        Convenience method to publish reminder.fired event.

        Args:
            reminder_id: Reminder ID
            task_id: Associated task ID
            user_id: User ID
            correlation_id: Optional correlation ID
        """
        event = create_event(
            event_type="todo.reminder.fired",
            payload={
                "reminder_id": str(reminder_id),
                "task_id": str(task_id)
            },
            user_id=user_id,
            correlation_id=correlation_id
        )
        self.publish_event("todo.reminder.fired", event)


def create_subscription_handler(
    dapr_app: DaprApp,
    pubsub_name: str,
    topic: str,
    handler: Callable
) -> Callable:
    """
    Create a subscription handler for a topic.

    This is a decorator factory that registers a handler function
    to be called when events are published to the specified topic.

    Args:
        dapr_app: DaprApp instance
        pubsub_name: Pub/Sub component name
        topic: Topic to subscribe to
        handler: Handler function (receives event data)

    Returns:
        Decorated handler function

    Example:
        >>> from dapr.ext.fastapi import DaprApp
        >>> dapr_app = DaprApp()
        >>>
        >>> @create_subscription_handler(
        ...     dapr_app=dapr_app,
        ...     pubsub_name="pubsub",
        ...     topic="todo.task.completed",
        ...     handler=handle_task_completed
        ... )
        >>> async def handle_task_completed(event_data: dict):
        ...     # Process task completion event
        ...     pass
    """
    return dapr_app.subscribe(
        pubsub=pubsub_name,
        topic=topic
    )(handler)


# Topic name constants
TOPIC_TASK_CREATED = "todo.task.created"
TOPIC_TASK_UPDATED = "todo.task.updated"
TOPIC_TASK_COMPLETED = "todo.task.completed"
TOPIC_TASK_DELETED = "todo.task.deleted"
TOPIC_TASK_PRIORITY_CHANGED = "todo.task.priority_changed"
TOPIC_REMINDER_SCHEDULED = "todo.reminder.scheduled"
TOPIC_REMINDER_FIRED = "todo.reminder.fired"
TOPIC_REMINDER_CANCELLED = "todo.reminder.cancelled"
