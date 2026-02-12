"""
Reminder scheduling service using Dapr Jobs API.

Handles scheduling, cancellation, and callback processing for reminders.
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4
from sqlmodel import Session, select

from ..models.reminder import (
    Reminder,
    ReminderCreate,
    validate_reminder_time,
    generate_dapr_job_name
)
from ..dapr_sdk_utils.jobs import schedule_job, cancel_job
from ..events.publishers.reminder_events import publish_reminder_scheduled


class ReminderService:
    """Service for managing reminders with Dapr Jobs API."""

    def __init__(self, db: Session):
        self.db = db

    async def schedule_reminder(
        self,
        task_id: UUID,
        user_id: UUID,
        scheduled_time: datetime,
        correlation_id: Optional[UUID] = None
    ) -> Reminder:
        """
        Schedule a reminder using Dapr Jobs API.

        Args:
            task_id: The task to remind about
            user_id: The user to remind
            scheduled_time: When to send the reminder
            correlation_id: Optional correlation ID for tracing

        Returns:
            Created Reminder entity

        Raises:
            ValueError: If scheduled time is invalid
        """
        # Validate scheduled time
        validate_reminder_time(scheduled_time)

        # Create reminder entity
        reminder = Reminder(
            task_id=task_id,
            user_id=user_id,
            scheduled_time=scheduled_time,
            status="scheduled",
            correlation_id=correlation_id or uuid4()
        )

        # Generate Dapr Job name
        job_name = generate_dapr_job_name(reminder.id, user_id)
        reminder.dapr_job_name = job_name

        # Save to database
        self.db.add(reminder)
        self.db.commit()
        self.db.refresh(reminder)

        # Schedule Dapr Job
        callback_url = f"/api/reminders/callback/{reminder.id}"
        await schedule_job(
            job_name=job_name,
            schedule_time=scheduled_time,
            callback_url=callback_url,
            data={
                "reminder_id": str(reminder.id),
                "task_id": str(task_id),
                "user_id": str(user_id)
            }
        )

        # Publish event
        await publish_reminder_scheduled(
            reminder_id=reminder.id,
            task_id=task_id,
            user_id=user_id,
            scheduled_time=scheduled_time,
            correlation_id=reminder.correlation_id
        )

        return reminder

    async def cancel_reminder(self, reminder_id: UUID, user_id: UUID) -> bool:
        """
        Cancel a scheduled reminder and delete Dapr Job.

        Args:
            reminder_id: The reminder to cancel
            user_id: The user ID (for authorization)

        Returns:
            True if cancelled successfully

        Raises:
            ValueError: If reminder not found or already sent
        """
        # Fetch reminder
        reminder = self.db.get(Reminder, reminder_id)
        if not reminder:
            raise ValueError(f"Reminder {reminder_id} not found")

        if reminder.user_id != user_id:
            raise ValueError("Unauthorized to cancel this reminder")

        if reminder.status == "sent":
            raise ValueError("Cannot cancel a reminder that has already been sent")

        # Cancel Dapr Job
        if reminder.dapr_job_name:
            await cancel_job(reminder.dapr_job_name)

        # Update status
        reminder.status = "cancelled"
        self.db.commit()

        return True

    def get_reminders(
        self,
        user_id: UUID,
        task_id: Optional[UUID] = None,
        status: Optional[str] = None
    ) -> List[Reminder]:
        """
        Get reminders for a user with optional filtering.

        Args:
            user_id: The user ID
            task_id: Optional task ID filter
            status: Optional status filter (scheduled/sent/cancelled)

        Returns:
            List of reminders
        """
        query = select(Reminder).where(Reminder.user_id == user_id)

        if task_id:
            query = query.where(Reminder.task_id == task_id)

        if status:
            query = query.where(Reminder.status == status)

        query = query.order_by(Reminder.scheduled_time.desc())

        reminders = self.db.exec(query).all()
        return list(reminders)

    def get_reminder_by_id(self, reminder_id: UUID, user_id: UUID) -> Optional[Reminder]:
        """
        Get a specific reminder by ID.

        Args:
            reminder_id: The reminder ID
            user_id: The user ID (for authorization)

        Returns:
            Reminder if found and authorized, None otherwise
        """
        reminder = self.db.get(Reminder, reminder_id)
        if reminder and reminder.user_id == user_id:
            return reminder
        return None

    async def mark_reminder_sent(self, reminder_id: UUID) -> Reminder:
        """
        Mark a reminder as sent (called by callback handler).

        Args:
            reminder_id: The reminder ID

        Returns:
            Updated Reminder entity

        Raises:
            ValueError: If reminder not found
        """
        reminder = self.db.get(Reminder, reminder_id)
        if not reminder:
            raise ValueError(f"Reminder {reminder_id} not found")

        reminder.status = "sent"
        reminder.sent_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(reminder)

        return reminder


async def schedule_reminder_for_task(
    db: Session,
    task_id: UUID,
    user_id: UUID,
    scheduled_time: datetime,
    correlation_id: Optional[UUID] = None
) -> Reminder:
    """
    Convenience function to schedule a reminder for a task.

    Args:
        db: Database session
        task_id: The task to remind about
        user_id: The user to remind
        scheduled_time: When to send the reminder
        correlation_id: Optional correlation ID

    Returns:
        Created Reminder entity
    """
    service = ReminderService(db)
    return await service.schedule_reminder(
        task_id=task_id,
        user_id=user_id,
        scheduled_time=scheduled_time,
        correlation_id=correlation_id
    )
