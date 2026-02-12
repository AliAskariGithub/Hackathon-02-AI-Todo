"""
Reminder callback handler for Dapr Jobs.

Processes callbacks from Dapr Jobs API when reminders fire.
"""

from datetime import datetime
from typing import Dict, Any
from uuid import UUID
from sqlmodel import Session

from backend.src.services.reminder_service import ReminderService
from backend.src.events.publishers.reminder_events import publish_reminder_fired


class ReminderCallbackService:
    """Service for handling Dapr Jobs callbacks."""

    def __init__(self, db: Session):
        self.db = db
        self.reminder_service = ReminderService(db)

    async def handle_reminder_callback(
        self,
        reminder_id: UUID,
        callback_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle callback from Dapr Jobs when reminder fires.

        Args:
            reminder_id: The reminder ID
            callback_data: Data from Dapr Jobs callback

        Returns:
            Response data for Dapr Jobs

        Raises:
            ValueError: If reminder not found or invalid
        """
        # Fetch reminder
        reminder = self.db.get(Reminder, reminder_id)
        if not reminder:
            raise ValueError(f"Reminder {reminder_id} not found")

        # Verify reminder is scheduled (not already sent or cancelled)
        if reminder.status != "scheduled":
            return {
                "status": "skipped",
                "reason": f"Reminder status is {reminder.status}, not scheduled"
            }

        # Mark reminder as sent
        await self.reminder_service.mark_reminder_sent(reminder_id)

        # Publish reminder fired event
        await publish_reminder_fired(
            reminder_id=reminder.id,
            task_id=reminder.task_id,
            user_id=reminder.user_id,
            fired_at=datetime.utcnow(),
            correlation_id=reminder.correlation_id
        )

        return {
            "status": "success",
            "reminder_id": str(reminder_id),
            "task_id": str(reminder.task_id),
            "user_id": str(reminder.user_id),
            "fired_at": datetime.utcnow().isoformat()
        }

    async def handle_callback_error(
        self,
        reminder_id: UUID,
        error: Exception
    ) -> Dict[str, Any]:
        """
        Handle errors during callback processing.

        Args:
            reminder_id: The reminder ID
            error: The error that occurred

        Returns:
            Error response data
        """
        return {
            "status": "error",
            "reminder_id": str(reminder_id),
            "error": str(error),
            "timestamp": datetime.utcnow().isoformat()
        }


async def process_reminder_callback(
    db: Session,
    reminder_id: UUID,
    callback_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Convenience function to process reminder callback.

    Args:
        db: Database session
        reminder_id: The reminder ID
        callback_data: Callback data from Dapr Jobs

    Returns:
        Response data
    """
    service = ReminderCallbackService(db)
    try:
        return await service.handle_reminder_callback(reminder_id, callback_data)
    except Exception as e:
        return await service.handle_callback_error(reminder_id, e)
