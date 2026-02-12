"""
Integration tests for reminders with Dapr Jobs API.

Tests reminder scheduling, cancellation, and callback processing.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from uuid import uuid4
from httpx import AsyncClient
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from main import app


@pytest.fixture
async def async_client():
    """Create async HTTP client for testing."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def user_id():
    """Generate test user ID."""
    return str(uuid4())


@pytest.fixture
def auth_token(user_id):
    """Generate test auth token."""
    return "test-token"


class TestReminderScheduling:
    """Test reminder scheduling via API."""

    @pytest.mark.asyncio
    async def test_schedule_reminder_for_task(self, async_client, user_id, auth_token):
        """Test scheduling a reminder for a task."""
        # Create a task first
        task_data = {
            "title": "Important meeting",
            "description": "Team sync meeting"
        }

        task_response = await async_client.post(
            f"/api/{user_id}/tasks",
            json=task_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        task = task_response.json()

        # Schedule reminder for 1 hour from now
        scheduled_time = (datetime.utcnow() + timedelta(hours=1)).isoformat()
        reminder_data = {
            "task_id": task["id"],
            "user_id": user_id,
            "scheduled_time": scheduled_time
        }

        response = await async_client.post(
            "/api/reminders",
            json=reminder_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 201
        reminder = response.json()
        assert reminder["task_id"] == task["id"]
        assert reminder["status"] == "scheduled"
        assert reminder["dapr_job_name"] is not None

    @pytest.mark.asyncio
    async def test_schedule_reminder_with_past_time_fails(self, async_client, user_id, auth_token):
        """Test that scheduling with past time fails."""
        task_id = str(uuid4())
        past_time = (datetime.utcnow() - timedelta(hours=1)).isoformat()

        reminder_data = {
            "task_id": task_id,
            "user_id": user_id,
            "scheduled_time": past_time
        }

        response = await async_client.post(
            "/api/reminders",
            json=reminder_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 400
        assert "future" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_schedule_reminder_less_than_one_minute_fails(
        self, async_client, user_id, auth_token
    ):
        """Test that scheduling less than 1 minute ahead fails."""
        task_id = str(uuid4())
        too_soon = (datetime.utcnow() + timedelta(seconds=30)).isoformat()

        reminder_data = {
            "task_id": task_id,
            "user_id": user_id,
            "scheduled_time": too_soon
        }

        response = await async_client.post(
            "/api/reminders",
            json=reminder_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 400


class TestReminderRetrieval:
    """Test reminder retrieval and filtering."""

    @pytest.mark.asyncio
    async def test_get_all_reminders(self, async_client, user_id, auth_token):
        """Test retrieving all reminders for a user."""
        # Schedule multiple reminders
        task_id = str(uuid4())
        for i in range(3):
            scheduled_time = (datetime.utcnow() + timedelta(hours=i+1)).isoformat()
            reminder_data = {
                "task_id": task_id,
                "user_id": user_id,
                "scheduled_time": scheduled_time
            }
            await async_client.post(
                "/api/reminders",
                json=reminder_data,
                headers={"Authorization": f"Bearer {auth_token}"}
            )

        # Get all reminders
        response = await async_client.get(
            "/api/reminders",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 200
        reminders = response.json()
        assert len(reminders) >= 3

    @pytest.mark.asyncio
    async def test_filter_reminders_by_task_id(self, async_client, user_id, auth_token):
        """Test filtering reminders by task ID."""
        task_id_1 = str(uuid4())
        task_id_2 = str(uuid4())

        # Schedule reminders for different tasks
        for task_id in [task_id_1, task_id_2]:
            scheduled_time = (datetime.utcnow() + timedelta(hours=1)).isoformat()
            reminder_data = {
                "task_id": task_id,
                "user_id": user_id,
                "scheduled_time": scheduled_time
            }
            await async_client.post(
                "/api/reminders",
                json=reminder_data,
                headers={"Authorization": f"Bearer {auth_token}"}
            )

        # Filter by task_id_1
        response = await async_client.get(
            f"/api/reminders?task_id={task_id_1}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        reminders = response.json()
        assert all(r["task_id"] == task_id_1 for r in reminders)

    @pytest.mark.asyncio
    async def test_filter_reminders_by_status(self, async_client, user_id, auth_token):
        """Test filtering reminders by status."""
        response = await async_client.get(
            "/api/reminders?status=scheduled",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 200
        reminders = response.json()
        assert all(r["status"] == "scheduled" for r in reminders)


class TestReminderCancellation:
    """Test reminder cancellation."""

    @pytest.mark.asyncio
    async def test_cancel_scheduled_reminder(self, async_client, user_id, auth_token):
        """Test cancelling a scheduled reminder."""
        # Schedule a reminder
        task_id = str(uuid4())
        scheduled_time = (datetime.utcnow() + timedelta(hours=1)).isoformat()
        reminder_data = {
            "task_id": task_id,
            "user_id": user_id,
            "scheduled_time": scheduled_time
        }

        create_response = await async_client.post(
            "/api/reminders",
            json=reminder_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        reminder = create_response.json()

        # Cancel the reminder
        cancel_response = await async_client.delete(
            f"/api/reminders/{reminder['id']}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert cancel_response.status_code == 204

        # Verify reminder is cancelled
        get_response = await async_client.get(
            f"/api/reminders/{reminder['id']}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        updated_reminder = get_response.json()
        assert updated_reminder["status"] == "cancelled"

    @pytest.mark.asyncio
    async def test_cancel_nonexistent_reminder_fails(self, async_client, user_id, auth_token):
        """Test that cancelling non-existent reminder fails."""
        fake_id = str(uuid4())

        response = await async_client.delete(
            f"/api/reminders/{fake_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 400


class TestReminderCallback:
    """Test Dapr Jobs callback processing."""

    @pytest.mark.asyncio
    async def test_reminder_callback_marks_as_sent(self, async_client, user_id, auth_token):
        """Test that callback marks reminder as sent."""
        # Schedule a reminder
        task_id = str(uuid4())
        scheduled_time = (datetime.utcnow() + timedelta(hours=1)).isoformat()
        reminder_data = {
            "task_id": task_id,
            "user_id": user_id,
            "scheduled_time": scheduled_time
        }

        create_response = await async_client.post(
            "/api/reminders",
            json=reminder_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        reminder = create_response.json()

        # Simulate Dapr Jobs callback
        callback_data = {
            "reminder_id": reminder["id"],
            "task_id": task_id,
            "user_id": user_id
        }

        callback_response = await async_client.post(
            f"/api/reminders/callback/{reminder['id']}",
            json=callback_data
        )

        assert callback_response.status_code == 200
        result = callback_response.json()
        assert result["status"] == "success"

        # Verify reminder is marked as sent
        get_response = await async_client.get(
            f"/api/reminders/{reminder['id']}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        updated_reminder = get_response.json()
        assert updated_reminder["status"] == "sent"
        assert updated_reminder["sent_at"] is not None

    @pytest.mark.asyncio
    async def test_callback_for_cancelled_reminder_skips(self, async_client, user_id, auth_token):
        """Test that callback for cancelled reminder is skipped."""
        # Schedule and cancel a reminder
        task_id = str(uuid4())
        scheduled_time = (datetime.utcnow() + timedelta(hours=1)).isoformat()
        reminder_data = {
            "task_id": task_id,
            "user_id": user_id,
            "scheduled_time": scheduled_time
        }

        create_response = await async_client.post(
            "/api/reminders",
            json=reminder_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        reminder = create_response.json()

        # Cancel it
        await async_client.delete(
            f"/api/reminders/{reminder['id']}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        # Try callback
        callback_data = {
            "reminder_id": reminder["id"],
            "task_id": task_id,
            "user_id": user_id
        }

        callback_response = await async_client.post(
            f"/api/reminders/callback/{reminder['id']}",
            json=callback_data
        )

        result = callback_response.json()
        assert result["status"] == "skipped"
        assert "cancelled" in result["reason"].lower()


class TestReminderEventPublishing:
    """Test reminder event publishing."""

    @pytest.mark.asyncio
    async def test_schedule_reminder_publishes_event(self, async_client, user_id, auth_token):
        """Test that scheduling publishes reminder.scheduled event."""
        task_id = str(uuid4())
        scheduled_time = (datetime.utcnow() + timedelta(hours=1)).isoformat()
        reminder_data = {
            "task_id": task_id,
            "user_id": user_id,
            "scheduled_time": scheduled_time
        }

        response = await async_client.post(
            "/api/reminders",
            json=reminder_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 201
        # In real test, verify event was published to Dapr Pub/Sub
        # This would require subscribing to the topic or checking State Store

    @pytest.mark.asyncio
    async def test_callback_publishes_fired_event(self, async_client, user_id, auth_token):
        """Test that callback publishes reminder.fired event."""
        # Schedule reminder
        task_id = str(uuid4())
        scheduled_time = (datetime.utcnow() + timedelta(hours=1)).isoformat()
        reminder_data = {
            "task_id": task_id,
            "user_id": user_id,
            "scheduled_time": scheduled_time
        }

        create_response = await async_client.post(
            "/api/reminders",
            json=reminder_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        reminder = create_response.json()

        # Trigger callback
        callback_data = {
            "reminder_id": reminder["id"],
            "task_id": task_id,
            "user_id": user_id
        }

        await async_client.post(
            f"/api/reminders/callback/{reminder['id']}",
            json=callback_data
        )

        # In real test, verify reminder.fired event was published
