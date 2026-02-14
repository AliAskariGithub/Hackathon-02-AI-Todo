"""
Reminder Scheduler Service

Integrates with Dapr Jobs API to schedule reminder notifications at exact times.
Provides functionality to schedule, cancel, and manage reminder jobs.
"""

import httpx
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID

logger = logging.getLogger(__name__)


class ReminderScheduler:
    """
    Service for scheduling reminders using Dapr Jobs API.
    """

    def __init__(self, dapr_http_port: int = 3500, callback_app_id: str = "notification-service"):
        """
        Initialize the ReminderScheduler.

        Args:
            dapr_http_port: Dapr sidecar HTTP port (default: 3500)
            callback_app_id: Dapr app ID of the notification service that handles callbacks
        """
        self.dapr_http_port = dapr_http_port
        self.callback_app_id = callback_app_id
        self.dapr_url = f"http://localhost:{dapr_http_port}"

    async def schedule_reminder(
        self,
        job_name: str,
        scheduled_time: datetime,
        reminder_data: Dict[str, Any],
        correlation_id: str
    ) -> bool:
        """
        Schedule a reminder using Dapr Jobs API.

        Args:
            job_name: Unique name for the job
            scheduled_time: When the reminder should fire
            reminder_data: Data to pass to the callback (reminder details)
            correlation_id: Correlation ID for tracing

        Returns:
            True if scheduling succeeded, False otherwise

        Raises:
            Exception: If scheduling fails
        """
        try:
            # Dapr Jobs API URL format: http://localhost:3500/v1.0-alpha1/jobs/{job-name}
            url = f"{self.dapr_url}/v1.0-alpha1/jobs/{job_name}"

            # Calculate schedule time in RFC3339 format
            schedule_time_rfc3339 = scheduled_time.strftime("%Y-%m-%dT%H:%M:%SZ")

            # Prepare job payload
            job_payload = {
                "schedule": f"@once {schedule_time_rfc3339}",  # One-time job at specific time
                "data": reminder_data,  # Data passed to callback
                "metadata": {
                    "correlation_id": correlation_id
                }
            }

            logger.info(
                f"Scheduling reminder job '{job_name}' for {schedule_time_rfc3339}, "
                f"correlation_id: {correlation_id}"
            )

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.put(
                    url,
                    json=job_payload,
                    headers={
                        "Content-Type": "application/json",
                        "X-Correlation-ID": correlation_id,
                    }
                )

                if response.status_code in [200, 201, 204]:
                    logger.info(f"Successfully scheduled reminder job '{job_name}'")
                    return True
                else:
                    logger.error(
                        f"Failed to schedule reminder job '{job_name}'. "
                        f"Status: {response.status_code}, Response: {response.text}"
                    )
                    return False

        except httpx.TimeoutException as e:
            logger.error(f"Timeout scheduling reminder job '{job_name}': {str(e)}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error scheduling reminder job '{job_name}': {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error scheduling reminder job '{job_name}': {str(e)}")
            raise

    async def cancel_reminder(self, job_name: str) -> bool:
        """
        Cancel a scheduled reminder using Dapr Jobs API.

        Args:
            job_name: Name of the job to cancel

        Returns:
            True if cancellation succeeded, False otherwise
        """
        try:
            # Dapr Jobs API URL format: http://localhost:3500/v1.0-alpha1/jobs/{job-name}
            url = f"{self.dapr_url}/v1.0-alpha1/jobs/{job_name}"

            logger.info(f"Cancelling reminder job '{job_name}'")

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.delete(url)

                if response.status_code in [200, 204, 404]:
                    # 404 is acceptable - job may have already fired or been deleted
                    logger.info(f"Successfully cancelled reminder job '{job_name}'")
                    return True
                else:
                    logger.error(
                        f"Failed to cancel reminder job '{job_name}'. "
                        f"Status: {response.status_code}, Response: {response.text}"
                    )
                    return False

        except httpx.TimeoutException as e:
            logger.error(f"Timeout cancelling reminder job '{job_name}': {str(e)}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error cancelling reminder job '{job_name}': {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error cancelling reminder job '{job_name}': {str(e)}")
            raise

    async def get_reminder_status(self, job_name: str) -> Optional[Dict[str, Any]]:
        """
        Get the status of a scheduled reminder job.

        Args:
            job_name: Name of the job to check

        Returns:
            Job status information or None if job doesn't exist
        """
        try:
            # Dapr Jobs API URL format: http://localhost:3500/v1.0-alpha1/jobs/{job-name}
            url = f"{self.dapr_url}/v1.0-alpha1/jobs/{job_name}"

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)

                if response.status_code == 200:
                    job_info = response.json()
                    logger.info(f"Retrieved status for reminder job '{job_name}'")
                    return job_info
                elif response.status_code == 404:
                    logger.info(f"Reminder job '{job_name}' not found")
                    return None
                else:
                    logger.error(
                        f"Failed to get status for reminder job '{job_name}'. "
                        f"Status: {response.status_code}, Response: {response.text}"
                    )
                    return None

        except Exception as e:
            logger.error(f"Error getting status for reminder job '{job_name}': {str(e)}")
            return None
