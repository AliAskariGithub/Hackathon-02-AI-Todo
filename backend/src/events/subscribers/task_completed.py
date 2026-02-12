"""
Task Completed Event Subscriber

This module subscribes to the 'todo.task.completed' event and triggers
recurring task generation when a task with a recurrence pattern is completed.

Key Features:
- Subscribe to task.completed events via Dapr Pub/Sub
- Trigger recurring task generation
- Idempotency via correlation ID
- Error handling and logging
"""

from typing import Dict, Any
from uuid import UUID
from datetime import datetime
import logging

from dapr.ext.fastapi import DaprApp
from fastapi import Request

from ...services.task_generation_service import TaskGenerationService
from ...services.recurrence_service import RecurrenceService
from ...models import Task
from ...events.schema import EventSchema

logger = logging.getLogger(__name__)


class TaskCompletedSubscriber:
    """
    Subscriber for task.completed events.

    This subscriber listens for task completion events and generates
    the next recurring task instance if the task has a recurrence pattern.
    """

    def __init__(self, dapr_app: DaprApp):
        """
        Initialize the subscriber.

        Args:
            dapr_app: DaprApp instance for registering subscriptions
        """
        self.dapr_app = dapr_app
        self.task_generation_service = TaskGenerationService()
        self.recurrence_service = RecurrenceService()

        # Register subscription
        self._register_subscription()

    def _register_subscription(self):
        """
        Register subscription to task.completed topic.
        """
        @self.dapr_app.subscribe(
            pubsub="pubsub",
            topic="todo.task.completed"
        )
        async def handle_task_completed(event_data: Dict[str, Any]):
            """
            Handle task.completed event.

            Args:
                event_data: Event data from Dapr Pub/Sub
            """
            await self.process_task_completed_event(event_data)

    async def process_task_completed_event(self, event_data: Dict[str, Any]):
        """
        Process task.completed event and generate next recurring instance.

        Args:
            event_data: Event data containing task information

        Example event_data:
        {
            "event_type": "todo.task.completed",
            "payload": {
                "task_id": "uuid",
                "title": "Buy groceries",
                "recurrence": "Daily",
                ...
            },
            "user_id": "uuid",
            "timestamp": "2026-02-11T10:00:00Z",
            "correlation_id": "uuid"
        }
        """
        try:
            # Parse event
            event = EventSchema(**event_data)
            payload = event.payload

            logger.info(
                f"Processing task.completed event: task_id={payload.get('task_id')}, "
                f"correlation_id={event.correlation_id}"
            )

            # Extract task data
            task_id = UUID(payload.get('task_id'))
            user_id = event.user_id
            recurrence = payload.get('recurrence')

            # Check if task has recurrence pattern
            if not recurrence:
                logger.info(f"Task {task_id} has no recurrence pattern. Skipping.")
                return

            # Check if we should generate next instance
            if not self.recurrence_service.should_generate_next_instance(
                task_status=payload.get('status', 'completed'),
                has_recurrence=bool(recurrence)
            ):
                logger.info(f"Task {task_id} should not generate next instance. Skipping.")
                return

            # Reconstruct Task object from payload
            completed_task = self._reconstruct_task_from_payload(payload, user_id)

            # Generate next recurring instance
            next_task = await self.task_generation_service.generate_next_recurring_instance(
                completed_task=completed_task,
                correlation_id=event.correlation_id
            )

            if next_task:
                logger.info(
                    f"Successfully generated next recurring instance: {next_task.id} "
                    f"(parent: {task_id})"
                )
            else:
                logger.info(
                    f"Next recurring instance not generated for task {task_id} "
                    "(possibly already processed)"
                )

        except Exception as e:
            logger.error(
                f"Error processing task.completed event: {e}",
                exc_info=True
            )
            # Don't raise exception - this would cause Dapr to retry indefinitely
            # Instead, log the error and continue
            # In production, you might want to publish to a dead letter queue

    def _reconstruct_task_from_payload(
        self,
        payload: Dict[str, Any],
        user_id: UUID
    ) -> Task:
        """
        Reconstruct Task object from event payload.

        Args:
            payload: Event payload containing task data
            user_id: User ID

        Returns:
            Task object
        """
        return Task(
            id=UUID(payload.get('task_id')),
            user_id=user_id,
            title=payload.get('title'),
            description=payload.get('description'),
            status=payload.get('status', 'completed'),
            priority=payload.get('priority', 'Medium'),
            due_date=self._parse_datetime(payload.get('due_date')),
            recurrence=payload.get('recurrence'),
            recurrence_day_of_week=payload.get('recurrence_day_of_week'),
            recurrence_day_of_month=payload.get('recurrence_day_of_month'),
            tags=payload.get('tags'),
            created_at=self._parse_datetime(payload.get('created_at')) or datetime.utcnow(),
            updated_at=self._parse_datetime(payload.get('updated_at')) or datetime.utcnow(),
            completed_at=self._parse_datetime(payload.get('completed_at')) or datetime.utcnow(),
            parent_task_id=UUID(payload.get('parent_task_id')) if payload.get('parent_task_id') else None,
            correlation_id=UUID(payload.get('correlation_id')) if payload.get('correlation_id') else None
        )

    def _parse_datetime(self, datetime_str: str | None) -> datetime | None:
        """
        Parse datetime string to datetime object.

        Args:
            datetime_str: ISO 8601 datetime string

        Returns:
            datetime object or None
        """
        if not datetime_str:
            return None

        try:
            # Handle ISO 8601 format with 'Z' suffix
            if datetime_str.endswith('Z'):
                datetime_str = datetime_str[:-1] + '+00:00'
            return datetime.fromisoformat(datetime_str)
        except (ValueError, AttributeError):
            logger.warning(f"Failed to parse datetime: {datetime_str}")
            return None


def register_task_completed_subscriber(dapr_app: DaprApp):
    """
    Register task.completed event subscriber.

    This function should be called during application startup to register
    the subscriber with the Dapr app.

    Args:
        dapr_app: DaprApp instance

    Example:
        >>> from dapr.ext.fastapi import DaprApp
        >>> from fastapi import FastAPI
        >>>
        >>> app = FastAPI()
        >>> dapr_app = DaprApp(app)
        >>>
        >>> register_task_completed_subscriber(dapr_app)
    """
    TaskCompletedSubscriber(dapr_app)
    logger.info("Registered task.completed event subscriber")
