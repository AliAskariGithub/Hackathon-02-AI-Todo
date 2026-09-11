"""
Task Creator Service

Creates new task instances via Dapr Service Invocation to the backend API.
Handles communication with the main backend service for task creation.
"""

import httpx
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class TaskCreator:
    """
    Service for creating tasks via Dapr Service Invocation.
    """

    def __init__(self, dapr_http_port: int = 3500, backend_app_id: str = "backend-api"):
        """
        Initialize the TaskCreator.

        Args:
            dapr_http_port: Dapr sidecar HTTP port (default: 3500)
            backend_app_id: Dapr app ID of the backend service
        """
        self.dapr_http_port = dapr_http_port
        self.backend_app_id = backend_app_id
        self.dapr_url = f"http://localhost:{dapr_http_port}"

    async def create_recurring_task_instance(
        self,
        user_id: str,
        parent_task_id: str,
        task_data: Dict[str, Any],
        correlation_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new recurring task instance via Dapr Service Invocation.

        Args:
            user_id: The user ID who owns the task
            parent_task_id: The ID of the parent task (completed task)
            task_data: Task data for the new instance
            correlation_id: Correlation ID for tracing

        Returns:
            Created task data or None if creation failed

        Raises:
            Exception: If task creation fails after retries
        """
        try:
            # Prepare task data for creation
            new_task_data = {
                "title": task_data.get("title"),
                "description": task_data.get("description"),
                "status": "pending",  # New instance starts as pending
                "priority": task_data.get("priority", "Medium"),
                "due_date": task_data.get("due_date"),  # Already calculated next due date
                "recurrence": task_data.get("recurrence"),
                "recurrence_day_of_week": task_data.get("recurrence_day_of_week"),
                "recurrence_day_of_month": task_data.get("recurrence_day_of_month"),
                "tags": task_data.get("tags", []),
                "parent_task_id": parent_task_id,  # Link to parent task
            }

            # Remove None values
            new_task_data = {k: v for k, v in new_task_data.items() if v is not None}

            logger.info(
                f"Creating recurring task instance for user {user_id}, "
                f"parent task {parent_task_id}, correlation_id: {correlation_id}"
            )

            # Call backend API via Dapr Service Invocation
            # URL format: http://localhost:3500/v1.0/invoke/{app-id}/method/{method-name}
            url = f"{self.dapr_url}/v1.0/invoke/{self.backend_app_id}/method/api/{user_id}/tasks"

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    url,
                    json=new_task_data,
                    headers={
                        "Content-Type": "application/json",
                        "X-Correlation-ID": correlation_id,
                    }
                )

                if response.status_code == 201:
                    created_task = response.json()
                    logger.info(
                        f"Successfully created recurring task instance: {created_task.get('id')}"
                    )
                    return created_task
                else:
                    logger.error(
                        f"Failed to create recurring task instance. "
                        f"Status: {response.status_code}, Response: {response.text}"
                    )
                    return None

        except httpx.TimeoutException as e:
            logger.error(f"Timeout creating recurring task instance: {str(e)}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error creating recurring task instance: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating recurring task instance: {str(e)}")
            raise

    async def create_task_with_retry(
        self,
        user_id: str,
        parent_task_id: str,
        task_data: Dict[str, Any],
        correlation_id: str,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ) -> Optional[Dict[str, Any]]:
        """
        Create a recurring task instance with retry logic.

        Args:
            user_id: The user ID who owns the task
            parent_task_id: The ID of the parent task
            task_data: Task data for the new instance
            correlation_id: Correlation ID for tracing
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds

        Returns:
            Created task data or None if all retries failed
        """
        import asyncio

        for attempt in range(max_retries):
            try:
                result = await self.create_recurring_task_instance(
                    user_id=user_id,
                    parent_task_id=parent_task_id,
                    task_data=task_data,
                    correlation_id=correlation_id
                )

                if result:
                    return result

                # If creation returned None (non-exception failure), retry
                if attempt < max_retries - 1:
                    logger.warning(
                        f"Task creation returned None, retrying in {retry_delay}s "
                        f"(attempt {attempt + 1}/{max_retries})"
                    )
                    await asyncio.sleep(retry_delay * (attempt + 1))  # Exponential backoff

            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(
                        f"Task creation failed with error: {str(e)}, "
                        f"retrying in {retry_delay}s (attempt {attempt + 1}/{max_retries})"
                    )
                    await asyncio.sleep(retry_delay * (attempt + 1))  # Exponential backoff
                else:
                    logger.error(
                        f"Task creation failed after {max_retries} attempts: {str(e)}"
                    )
                    raise

        logger.error(f"Failed to create recurring task instance after {max_retries} attempts")
        return None
