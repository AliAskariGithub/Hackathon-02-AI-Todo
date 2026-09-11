"""
Notification Logger Service

Handles logging and processing of notification events.
Validates timing accuracy and publishes notification.sent events.
"""

import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)


class NotificationLogger:
    """
    Service for logging and processing notifications.
    """

    def __init__(self):
        self.timing_tolerance_seconds = 1.0  # 1-second accuracy requirement

    def log_notification(
        self,
        reminder_id: str,
        task_id: str,
        user_id: str,
        scheduled_time: datetime,
        actual_time: datetime,
        notification_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Log a notification and validate timing accuracy.

        Args:
            reminder_id: The reminder ID
            task_id: The task ID
            user_id: The user ID
            scheduled_time: When the notification was scheduled
            actual_time: When the notification actually fired
            notification_data: Additional notification data

        Returns:
            Dictionary with notification log details and timing validation
        """
        try:
            # Calculate timing difference
            time_diff = abs((actual_time - scheduled_time).total_seconds())
            is_on_time = time_diff <= self.timing_tolerance_seconds

            # Log notification
            log_entry = {
                "reminder_id": reminder_id,
                "task_id": task_id,
                "user_id": user_id,
                "scheduled_time": scheduled_time.isoformat(),
                "actual_time": actual_time.isoformat(),
                "time_difference_seconds": time_diff,
                "is_on_time": is_on_time,
                "notification_data": notification_data,
                "logged_at": datetime.utcnow().isoformat()
            }

            # Log with appropriate level based on timing
            if is_on_time:
                logger.info(
                    f"Notification sent on time for reminder {reminder_id}: "
                    f"scheduled={scheduled_time.isoformat()}, "
                    f"actual={actual_time.isoformat()}, "
                    f"diff={time_diff:.3f}s"
                )
            else:
                logger.warning(
                    f"Notification timing exceeded tolerance for reminder {reminder_id}: "
                    f"scheduled={scheduled_time.isoformat()}, "
                    f"actual={actual_time.isoformat()}, "
                    f"diff={time_diff:.3f}s (tolerance={self.timing_tolerance_seconds}s)"
                )

            return {
                "status": "success",
                "log_entry": log_entry,
                "timing_validation": {
                    "is_on_time": is_on_time,
                    "time_difference_seconds": time_diff,
                    "tolerance_seconds": self.timing_tolerance_seconds
                }
            }

        except Exception as e:
            logger.error(f"Error logging notification for reminder {reminder_id}: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }

    def validate_timing(
        self,
        scheduled_time: datetime,
        actual_time: datetime
    ) -> Dict[str, Any]:
        """
        Validate that notification was triggered within timing tolerance.

        Args:
            scheduled_time: When the notification was scheduled
            actual_time: When the notification actually fired

        Returns:
            Dictionary with validation results
        """
        time_diff = abs((actual_time - scheduled_time).total_seconds())
        is_on_time = time_diff <= self.timing_tolerance_seconds

        return {
            "is_on_time": is_on_time,
            "time_difference_seconds": time_diff,
            "tolerance_seconds": self.timing_tolerance_seconds,
            "scheduled_time": scheduled_time.isoformat(),
            "actual_time": actual_time.isoformat()
        }
