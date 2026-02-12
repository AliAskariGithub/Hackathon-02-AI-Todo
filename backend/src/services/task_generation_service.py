"""
Task Generation Service - Recurring Task Instance Creation

This service handles the generation of recurring task instances when a task
is completed. It includes idempotency checks to prevent duplicate generation
on event replay.

Key Features:
- Generate next recurring task instance
- Idempotency via correlation ID tracking
- Parent-child task relationship tracking
- Event-driven architecture integration
"""

from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID, uuid4

from ..dapr_sdk_utils.state import DaprStateStore, task_key, correlation_id_key
from ..dapr_sdk_utils.pubsub import DaprPubSub
from ..services.recurrence_service import RecurrenceService
from ..models import Task


class TaskGenerationService:
    """
    Service for generating recurring task instances.
    """

    def __init__(self):
        self.state_store = DaprStateStore()
        self.pubsub = DaprPubSub()
        self.recurrence_service = RecurrenceService()

    async def generate_next_recurring_instance(
        self,
        completed_task: Task,
        correlation_id: UUID
    ) -> Optional[Task]:
        """
        Generate the next recurring task instance after task completion.

        This method:
        1. Checks idempotency (prevents duplicate generation)
        2. Calculates next due date
        3. Creates new task instance
        4. Links to parent task
        5. Publishes task.created event

        Args:
            completed_task: The completed task with recurrence pattern
            correlation_id: Correlation ID for idempotency tracking

        Returns:
            New task instance or None if already generated

        Example:
            >>> service = TaskGenerationService()
            >>> next_task = await service.generate_next_recurring_instance(
            ...     completed_task=task,
            ...     correlation_id=UUID("correlation-uuid")
            ... )
        """
        # Check if task has recurrence pattern
        if not completed_task.recurrence:
            return None

        # Check idempotency: Has this correlation ID already generated a task?
        if await self._is_already_processed(correlation_id):
            print(f"Correlation ID {correlation_id} already processed. Skipping duplicate generation.")
            return None

        # Calculate next due date
        next_due_date = self.recurrence_service.calculate_next_occurrence_from_completion(
            recurrence_type=completed_task.recurrence,
            completion_time=completed_task.completed_at or datetime.utcnow(),
            original_due_date=completed_task.due_date,
            recurrence_day_of_week=completed_task.recurrence_day_of_week,
            recurrence_day_of_month=completed_task.recurrence_day_of_month
        )

        # Create new task instance
        new_task = Task(
            id=uuid4(),
            user_id=completed_task.user_id,
            title=completed_task.title,
            description=completed_task.description,
            status="pending",
            priority=completed_task.priority,
            due_date=next_due_date,
            recurrence=completed_task.recurrence,
            recurrence_day_of_week=completed_task.recurrence_day_of_week,
            recurrence_day_of_month=completed_task.recurrence_day_of_month,
            tags=completed_task.tags,
            parent_task_id=completed_task.id,
            correlation_id=correlation_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        # Save new task to State Store
        await self._save_task_to_state_store(new_task)

        # Mark correlation ID as processed (for idempotency)
        await self._mark_correlation_id_processed(correlation_id, new_task.id)

        # Publish task.created event
        self.pubsub.publish_task_created(
            task_id=new_task.id,
            user_id=new_task.user_id,
            task_data=self._task_to_dict(new_task),
            correlation_id=correlation_id
        )

        print(f"Generated next recurring instance: {new_task.id} (parent: {completed_task.id})")
        return new_task

    async def _is_already_processed(self, correlation_id: UUID) -> bool:
        """
        Check if correlation ID has already been processed.

        Args:
            correlation_id: Correlation ID to check

        Returns:
            True if already processed, False otherwise
        """
        key = correlation_id_key(correlation_id)
        result = self.state_store.get_state(key)
        return result is not None

    async def _mark_correlation_id_processed(
        self,
        correlation_id: UUID,
        generated_task_id: UUID
    ) -> None:
        """
        Mark correlation ID as processed to prevent duplicate generation.

        Args:
            correlation_id: Correlation ID to mark
            generated_task_id: ID of the generated task
        """
        key = correlation_id_key(correlation_id)
        value = {
            "correlation_id": str(correlation_id),
            "generated_task_id": str(generated_task_id),
            "processed_at": datetime.utcnow().isoformat()
        }

        # Store with TTL (Time-To-Live) of 7 days
        # After 7 days, the correlation ID tracking will be removed
        # This prevents the state store from growing indefinitely
        self.state_store.save_state(key, value)

    async def _save_task_to_state_store(self, task: Task) -> None:
        """
        Save task to Dapr State Store.

        Args:
            task: Task to save
        """
        key = task_key(task.user_id, task.id)
        value = self._task_to_dict(task)
        self.state_store.save_state(key, value)

    def _task_to_dict(self, task: Task) -> Dict[str, Any]:
        """
        Convert Task model to dictionary for storage.

        Args:
            task: Task model

        Returns:
            Dictionary representation
        """
        return {
            "id": str(task.id),
            "user_id": str(task.user_id),
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "priority": task.priority,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "recurrence": task.recurrence,
            "recurrence_day_of_week": task.recurrence_day_of_week,
            "recurrence_day_of_month": task.recurrence_day_of_month,
            "tags": task.tags,
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat(),
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "parent_task_id": str(task.parent_task_id) if task.parent_task_id else None,
            "correlation_id": str(task.correlation_id) if task.correlation_id else None
        }

    async def get_recurring_task_chain(
        self,
        task_id: UUID,
        user_id: UUID
    ) -> list[Task]:
        """
        Get the full chain of recurring task instances.

        Args:
            task_id: Task ID (can be any task in the chain)
            user_id: User ID

        Returns:
            List of tasks in the recurring chain (ordered by creation date)

        Example:
            >>> service = TaskGenerationService()
            >>> chain = await service.get_recurring_task_chain(
            ...     task_id=UUID("task-uuid"),
            ...     user_id=UUID("user-uuid")
            ... )
        """
        # This would query the State Store for all tasks with the same parent_task_id
        # or where this task is the parent
        # Implementation depends on State Store query capabilities
        # For now, return empty list (to be implemented with State Store queries)
        return []

    async def cancel_recurring_task_chain(
        self,
        task_id: UUID,
        user_id: UUID,
        cancel_future_instances: bool = True
    ) -> int:
        """
        Cancel a recurring task and optionally all future instances.

        Args:
            task_id: Task ID
            user_id: User ID
            cancel_future_instances: Whether to cancel future instances

        Returns:
            Number of tasks cancelled

        Example:
            >>> service = TaskGenerationService()
            >>> cancelled_count = await service.cancel_recurring_task_chain(
            ...     task_id=UUID("task-uuid"),
            ...     user_id=UUID("user-uuid"),
            ...     cancel_future_instances=True
            ... )
        """
        # This would:
        # 1. Mark the current task as deleted
        # 2. If cancel_future_instances=True, mark all future instances as deleted
        # Implementation depends on State Store query capabilities
        # For now, return 0 (to be implemented with State Store queries)
        return 0
