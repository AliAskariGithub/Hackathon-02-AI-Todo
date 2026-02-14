"""
Task Completed Event Handler

Handles task.completed events from Kafka and generates next recurring task instances.
Implements idempotency checks and error handling for reliable task generation.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from ..services.recurrence_calculator import RecurrenceCalculator
from ..services.task_creator import TaskCreator
from ..utils.idempotency import IdempotencyChecker

logger = logging.getLogger(__name__)


class TaskCompletedHandler:
    """
    Handler for task.completed events that generates recurring task instances.
    """

    def __init__(
        self,
        task_creator: TaskCreator,
        idempotency_checker: IdempotencyChecker
    ):
        """
        Initialize the handler.

        Args:
            task_creator: Service for creating tasks via Dapr
            idempotency_checker: Service for checking event idempotency
        """
        self.task_creator = task_creator
        self.idempotency_checker = idempotency_checker
        self.recurrence_calculator = RecurrenceCalculator()

    async def handle_task_completed(self, event: Dict[str, Any]) -> Dict[str, str]:
        """
        Handle a task.completed event and generate next recurring instance if applicable.

        Args:
            event: The task.completed event data

        Returns:
            Response dictionary with status and message
        """
        try:
            # Extract event data
            event_type = event.get("event_type")
            correlation_id = event.get("correlation_id")
            payload = event.get("payload", {})
            task_data = payload.get("task_data", {})
            user_id = payload.get("user_id")
            task_id = task_data.get("task_id") or task_data.get("id")

            logger.info(
                f"Received {event_type} event for task {task_id}, "
                f"correlation_id: {correlation_id}"
            )

            # Validate required fields
            if not user_id or not task_id:
                logger.error(f"Missing required fields: user_id={user_id}, task_id={task_id}")
                return {"status": "error", "message": "Missing required fields"}

            # Check idempotency - prevent duplicate processing
            is_duplicate = await self.idempotency_checker.is_duplicate(correlation_id)
            if is_duplicate:
                logger.info(
                    f"Duplicate event detected for correlation_id {correlation_id}, skipping"
                )
                return {"status": "skipped", "message": "Duplicate event"}

            # Check if task has recurrence pattern
            recurrence = task_data.get("recurrence")
            if not recurrence:
                logger.info(f"Task {task_id} has no recurrence pattern, skipping")
                return {"status": "skipped", "message": "No recurrence pattern"}

            # Extract recurrence parameters
            recurrence_day_of_week = task_data.get("recurrence_day_of_week")
            recurrence_day_of_month = task_data.get("recurrence_day_of_month")

            # Validate recurrence pattern
            is_valid = self.recurrence_calculator.validate_recurrence_pattern(
                recurrence=recurrence,
                recurrence_day_of_week=recurrence_day_of_week,
                recurrence_day_of_month=recurrence_day_of_month
            )

            if not is_valid:
                logger.error(
                    f"Invalid recurrence pattern for task {task_id}: "
                    f"recurrence={recurrence}, day_of_week={recurrence_day_of_week}, "
                    f"day_of_month={recurrence_day_of_month}"
                )
                return {"status": "error", "message": "Invalid recurrence pattern"}

            # Get current due date
            due_date_str = task_data.get("due_date")
            if not due_date_str:
                logger.warning(
                    f"Task {task_id} has recurrence but no due_date, using current time"
                )
                current_due_date = datetime.utcnow()
            else:
                try:
                    current_due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
                except ValueError as e:
                    logger.error(f"Invalid due_date format: {due_date_str}, error: {str(e)}")
                    current_due_date = datetime.utcnow()

            # Calculate next due date
            try:
                next_due_date = self.recurrence_calculator.calculate_next_due_date(
                    current_due_date=current_due_date,
                    recurrence=recurrence,
                    recurrence_day_of_week=recurrence_day_of_week,
                    recurrence_day_of_month=recurrence_day_of_month
                )

                logger.info(
                    f"Calculated next due date for task {task_id}: "
                    f"{current_due_date} -> {next_due_date}"
                )
            except ValueError as e:
                logger.error(f"Error calculating next due date: {str(e)}")
                return {"status": "error", "message": f"Calculation error: {str(e)}"}

            # Prepare new task data
            new_task_data = {
                "title": task_data.get("title"),
                "description": task_data.get("description"),
                "priority": task_data.get("priority", "Medium"),
                "due_date": next_due_date.isoformat(),
                "recurrence": recurrence,
                "recurrence_day_of_week": recurrence_day_of_week,
                "recurrence_day_of_month": recurrence_day_of_month,
                "tags": task_data.get("tags", []),
            }

            # Create new task instance with retry logic
            try:
                created_task = await self.task_creator.create_task_with_retry(
                    user_id=str(user_id),
                    parent_task_id=str(task_id),
                    task_data=new_task_data,
                    correlation_id=correlation_id,
                    max_retries=3
                )

                if created_task:
                    logger.info(
                        f"Successfully generated recurring task instance: "
                        f"{created_task.get('id')} for parent task {task_id}"
                    )
                    return {
                        "status": "success",
                        "message": "Recurring task instance created",
                        "new_task_id": created_task.get("id")
                    }
                else:
                    logger.error(f"Failed to create recurring task instance for task {task_id}")
                    return {"status": "error", "message": "Task creation failed"}

            except Exception as e:
                logger.error(
                    f"Error creating recurring task instance for task {task_id}: {str(e)}"
                )
                return {"status": "error", "message": f"Creation error: {str(e)}"}

        except Exception as e:
            logger.error(f"Unexpected error in handle_task_completed: {str(e)}")
            return {"status": "error", "message": f"Unexpected error: {str(e)}"}
