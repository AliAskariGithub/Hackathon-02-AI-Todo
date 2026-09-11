"""
Job Callback Handler for Notification Service

Handles Dapr Jobs API callbacks when reminders fire.
Processes notifications, validates timing, and publishes events.
"""

import logging
from datetime import datetime
from typing import Dict, Any
from ..services.notification_logger import NotificationLogger
from ..utils.idempotency import IdempotencyChecker

logger = logging.getLogger(__name__)


class JobCallbackHandler:
    """
    Handler for Dapr Jobs API callbacks.
    """

    def __init__(self, idempotency_checker: IdempotencyChecker):
        """
        Initialize the handler.

        Args:
            idempotency_checker: Service for checking event idempotency
        """
        self.notification_logger = NotificationLogger()
        self.idempotency_checker = idempotency_checker

    async def handle_reminder_callback(self, callback_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a reminder callback from Dapr Jobs API.

        Args:
            callback_data: Callback data from Dapr Jobs

        Returns:
            Response dictionary with status and details
        """
        try:
            # Extract callback data
            reminder_id = callback_data.get("reminder_id")
            task_id = callback_data.get("task_id")
            user_id = callback_data.get("user_id")
            scheduled_time_str = callback_data.get("scheduled_time")
            correlation_id = callback_data.get("correlation_id")

            logger.info(
                f"Received reminder callback for reminder {reminder_id}, "
                f"task {task_id}, correlation_id: {correlation_id}"
            )

            # Validate required fields
            if not all([reminder_id, task_id, user_id, scheduled_time_str]):
                logger.error(f"Missing required fields in callback data: {callback_data}")
                return {
                    "status": "error",
                    "message": "Missing required fields in callback data"
                }

            # Check idempotency - prevent duplicate processing
            is_duplicate = await self.idempotency_checker.is_duplicate(correlation_id)
            if is_duplicate:
                logger.info(
                    f"Duplicate callback detected for correlation_id {correlation_id}, skipping"
                )
                return {
                    "status": "skipped",
                    "message": "Duplicate callback"
                }

            # Parse scheduled time
            try:
                scheduled_time = datetime.fromisoformat(scheduled_time_str.replace('Z', '+00:00'))
            except ValueError as e:
                logger.error(f"Invalid scheduled_time format: {scheduled_time_str}, error: {str(e)}")
                return {
                    "status": "error",
                    "message": f"Invalid scheduled_time format: {str(e)}"
                }

            # Get actual callback time
            actual_time = datetime.utcnow()

            # Validate timing accuracy (within 1 second)
            timing_validation = self.notification_logger.validate_timing(
                scheduled_time=scheduled_time,
                actual_time=actual_time
            )

            if not timing_validation["is_on_time"]:
                logger.warning(
                    f"Reminder {reminder_id} timing exceeded tolerance: "
                    f"{timing_validation['time_difference_seconds']:.3f}s "
                    f"(tolerance: {timing_validation['tolerance_seconds']}s)"
                )

            # Log notification
            log_result = self.notification_logger.log_notification(
                reminder_id=reminder_id,
                task_id=task_id,
                user_id=user_id,
                scheduled_time=scheduled_time,
                actual_time=actual_time,
                notification_data=callback_data
            )

            if log_result["status"] == "error":
                logger.error(f"Failed to log notification: {log_result.get('message')}")
                return log_result

            # Publish notification.sent event
            try:
                from ....dapr_sdk_utils.pubsub import DaprPubSub
                pubsub = DaprPubSub()

                pubsub.publish_event(
                    topic="todo.notifications",
                    event_type="todo.notification.sent",
                    payload={
                        "reminder_id": reminder_id,
                        "task_id": task_id,
                        "user_id": user_id,
                        "scheduled_time": scheduled_time.isoformat(),
                        "actual_time": actual_time.isoformat(),
                        "time_difference_seconds": timing_validation["time_difference_seconds"],
                        "is_on_time": timing_validation["is_on_time"]
                    },
                    correlation_id=correlation_id
                )

                logger.info(f"Published notification.sent event for reminder {reminder_id}")

            except Exception as pubsub_error:
                # Log error but don't fail the callback
                logger.warning(f"Failed to publish notification.sent event: {str(pubsub_error)}")

            return {
                "status": "success",
                "message": "Notification processed successfully",
                "reminder_id": reminder_id,
                "timing_validation": timing_validation,
                "log_entry": log_result.get("log_entry")
            }

        except Exception as e:
            logger.error(f"Unexpected error in handle_reminder_callback: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                "status": "error",
                "message": f"Unexpected error: {str(e)}"
            }
