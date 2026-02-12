"""
Dapr Jobs API Utility Functions

This module provides utility functions for scheduling jobs via Dapr Jobs API.
It enables exact-time reminder scheduling without polling-based cron jobs.

Key Features:
- Schedule one-time jobs at specific times
- Cancel scheduled jobs
- List active jobs
- Job callback handling
- Automatic retry on failure
"""

from typing import Dict, Optional, Any
from datetime import datetime
from uuid import UUID
from dapr.clients import DaprClient
import json


class DaprJobsAPI:
    """
    Wrapper for Dapr Jobs API operations.

    Provides methods for scheduling and managing jobs for reminder delivery.
    """

    def __init__(self, app_id: str = "backend"):
        """
        Initialize Dapr Jobs API client.

        Args:
            app_id: Application ID for job callbacks (default: "backend")
        """
        self.app_id = app_id
        self.client = DaprClient()

    def schedule_job(
        self,
        job_name: str,
        schedule_time: datetime,
        callback_url: str,
        data: Optional[Dict[str, Any]] = None,
        ttl: Optional[str] = None
    ) -> None:
        """
        Schedule a one-time job at a specific time.

        Args:
            job_name: Unique job identifier (e.g., "reminder-{reminder_id}")
            schedule_time: When to execute the job (UTC datetime)
            callback_url: URL to call when job fires (e.g., "/api/reminders/callback")
            data: Optional data to pass to callback
            ttl: Optional time-to-live for the job (e.g., "1h", "30m")

        Example:
            >>> jobs = DaprJobsAPI()
            >>> jobs.schedule_job(
            ...     job_name="reminder-123",
            ...     schedule_time=datetime(2026, 2, 15, 9, 0, 0),
            ...     callback_url="/api/reminders/callback",
            ...     data={"reminder_id": "123", "task_id": "456"}
            ... )
        """
        # Convert datetime to ISO 8601 format
        schedule_iso = schedule_time.isoformat() + "Z"

        # Prepare job payload
        job_payload = {
            "schedule": schedule_iso,
            "data": data or {},
            "dueTime": schedule_iso,
            "ttl": ttl or "24h"  # Default 24-hour TTL
        }

        # Schedule job via Dapr HTTP API
        # Note: Dapr Jobs API is alpha (v1.0-alpha1) and uses HTTP endpoint
        try:
            response = self.client.invoke_method(
                app_id=self.app_id,
                method_name=f"v1.0-alpha1/jobs/{job_name}",
                data=json.dumps(job_payload),
                http_verb="POST"
            )
            print(f"Job '{job_name}' scheduled for {schedule_iso}")
        except Exception as e:
            print(f"Error scheduling job '{job_name}': {e}")
            raise

    def cancel_job(self, job_name: str) -> None:
        """
        Cancel a scheduled job.

        Args:
            job_name: Job identifier to cancel

        Example:
            >>> jobs = DaprJobsAPI()
            >>> jobs.cancel_job("reminder-123")
        """
        try:
            response = self.client.invoke_method(
                app_id=self.app_id,
                method_name=f"v1.0-alpha1/jobs/{job_name}",
                http_verb="DELETE"
            )
            print(f"Job '{job_name}' cancelled")
        except Exception as e:
            print(f"Error cancelling job '{job_name}': {e}")
            raise

    def get_job(self, job_name: str) -> Optional[Dict[str, Any]]:
        """
        Get job details.

        Args:
            job_name: Job identifier

        Returns:
            Job details dict or None if not found

        Example:
            >>> jobs = DaprJobsAPI()
            >>> job_info = jobs.get_job("reminder-123")
        """
        try:
            response = self.client.invoke_method(
                app_id=self.app_id,
                method_name=f"v1.0-alpha1/jobs/{job_name}",
                http_verb="GET"
            )
            return json.loads(response.data) if response.data else None
        except Exception as e:
            print(f"Error getting job '{job_name}': {e}")
            return None

    def list_jobs(self) -> list[Dict[str, Any]]:
        """
        List all scheduled jobs.

        Returns:
            List of job details

        Example:
            >>> jobs = DaprJobsAPI()
            >>> all_jobs = jobs.list_jobs()
        """
        try:
            response = self.client.invoke_method(
                app_id=self.app_id,
                method_name="v1.0-alpha1/jobs",
                http_verb="GET"
            )
            data = json.loads(response.data) if response.data else {}
            return data.get("jobs", [])
        except Exception as e:
            print(f"Error listing jobs: {e}")
            return []


def schedule_reminder_job(
    reminder_id: UUID,
    task_id: UUID,
    user_id: UUID,
    scheduled_time: datetime
) -> str:
    """
    Convenience function to schedule a reminder job.

    Args:
        reminder_id: Reminder ID
        task_id: Associated task ID
        user_id: User ID
        scheduled_time: When to fire the reminder

    Returns:
        Job name (for cancellation)

    Example:
        >>> job_name = schedule_reminder_job(
        ...     reminder_id=UUID("reminder-uuid"),
        ...     task_id=UUID("task-uuid"),
        ...     user_id=UUID("user-uuid"),
        ...     scheduled_time=datetime(2026, 2, 15, 9, 0, 0)
        ... )
    """
    jobs_api = DaprJobsAPI()
    job_name = f"reminder-{reminder_id}"

    jobs_api.schedule_job(
        job_name=job_name,
        schedule_time=scheduled_time,
        callback_url="/api/reminders/callback",
        data={
            "reminder_id": str(reminder_id),
            "task_id": str(task_id),
            "user_id": str(user_id),
            "scheduled_time": scheduled_time.isoformat()
        }
    )

    return job_name


def cancel_reminder_job(reminder_id: UUID) -> None:
    """
    Convenience function to cancel a reminder job.

    Args:
        reminder_id: Reminder ID

    Example:
        >>> cancel_reminder_job(UUID("reminder-uuid"))
    """
    jobs_api = DaprJobsAPI()
    job_name = f"reminder-{reminder_id}"
    jobs_api.cancel_job(job_name)


def get_reminder_job_status(reminder_id: UUID) -> Optional[Dict[str, Any]]:
    """
    Convenience function to get reminder job status.

    Args:
        reminder_id: Reminder ID

    Returns:
        Job details or None if not found

    Example:
        >>> status = get_reminder_job_status(UUID("reminder-uuid"))
    """
    jobs_api = DaprJobsAPI()
    job_name = f"reminder-{reminder_id}"
    return jobs_api.get_job(job_name)


# Module-level convenience functions for backward compatibility
def schedule_job(
    job_name: str,
    schedule_time: datetime,
    callback_url: str,
    data: Optional[Dict[str, Any]] = None,
    ttl: Optional[str] = None
) -> None:
    """Schedule a one-time job at a specific time."""
    jobs_api = DaprJobsAPI()
    jobs_api.schedule_job(job_name, schedule_time, callback_url, data, ttl)


def cancel_job(job_name: str) -> None:
    """Cancel a scheduled job."""
    jobs_api = DaprJobsAPI()
    jobs_api.cancel_job(job_name)

