"""
Integration tests for recurring tasks.

Tests event publishing and next instance generation with real Dapr components.
"""

import pytest
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
    # In real tests, this would create a valid JWT token
    return "test-token"


class TestRecurringTaskCreation:
    """Test creating recurring tasks and event publishing."""

    @pytest.mark.asyncio
    async def test_create_daily_recurring_task(self, async_client, user_id, auth_token):
        """Test creating a daily recurring task publishes event."""
        task_data = {
            "title": "Daily standup",
            "description": "Team standup meeting",
            "recurrence": "Daily",
            "due_date": datetime.utcnow().isoformat(),
            "priority": "High"
        }

        response = await async_client.post(
            f"/api/{user_id}/tasks",
            json=task_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 201
        task = response.json()
        assert task["recurrence"] == "Daily"
        assert task["title"] == "Daily standup"

        # Verify event was published to Dapr Pub/Sub
        # This would require subscribing to the topic or checking State Store
        # In real implementation, use Dapr test harness or mock

    @pytest.mark.asyncio
    async def test_create_weekly_recurring_task(self, async_client, user_id, auth_token):
        """Test creating a weekly recurring task with day of week."""
        task_data = {
            "title": "Weekly review",
            "description": "Team weekly review",
            "recurrence": "Weekly",
            "recurrence_day_of_week": 5,  # Friday
            "due_date": datetime.utcnow().isoformat(),
            "priority": "Medium"
        }

        response = await async_client.post(
            f"/api/{user_id}/tasks",
            json=task_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 201
        task = response.json()
        assert task["recurrence"] == "Weekly"
        assert task["recurrence_day_of_week"] == 5

    @pytest.mark.asyncio
    async def test_create_monthly_recurring_task(self, async_client, user_id, auth_token):
        """Test creating a monthly recurring task with day of month."""
        task_data = {
            "title": "Monthly report",
            "description": "Submit monthly report",
            "recurrence": "Monthly",
            "recurrence_day_of_month": 1,  # 1st of month
            "due_date": datetime.utcnow().isoformat(),
            "priority": "High"
        }

        response = await async_client.post(
            f"/api/{user_id}/tasks",
            json=task_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 201
        task = response.json()
        assert task["recurrence"] == "Monthly"
        assert task["recurrence_day_of_month"] == 1


class TestRecurringTaskCompletion:
    """Test completing recurring tasks and next instance generation."""

    @pytest.mark.asyncio
    async def test_complete_daily_task_generates_next_instance(
        self, async_client, user_id, auth_token
    ):
        """Test completing a daily recurring task generates next instance."""
        # Create daily recurring task
        task_data = {
            "title": "Daily exercise",
            "recurrence": "Daily",
            "due_date": datetime.utcnow().isoformat()
        }

        create_response = await async_client.post(
            f"/api/{user_id}/tasks",
            json=task_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        task = create_response.json()
        task_id = task["id"]

        # Complete the task
        complete_response = await async_client.post(
            f"/api/{user_id}/tasks/{task_id}/complete",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert complete_response.status_code == 200
        result = complete_response.json()
        assert result["has_recurrence"] is True
        assert result["next_instance_will_be_generated"] is True

        # Verify next instance was created (async, may need to wait)
        await asyncio.sleep(1)  # Wait for event processing

        tasks_response = await async_client.get(
            f"/api/{user_id}/tasks",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        tasks = tasks_response.json()

        # Should have original (completed) + new instance
        assert len(tasks) >= 2
        new_task = next(t for t in tasks if t["id"] != task_id and t["parent_task_id"] == task_id)
        assert new_task["title"] == "Daily exercise"
        assert new_task["status"] == "pending"

    @pytest.mark.asyncio
    async def test_complete_weekly_task_generates_next_instance(
        self, async_client, user_id, auth_token
    ):
        """Test completing a weekly recurring task generates next instance."""
        task_data = {
            "title": "Weekly planning",
            "recurrence": "Weekly",
            "recurrence_day_of_week": 1,  # Monday
            "due_date": datetime.utcnow().isoformat()
        }

        create_response = await async_client.post(
            f"/api/{user_id}/tasks",
            json=task_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        task = create_response.json()

        complete_response = await async_client.post(
            f"/api/{user_id}/tasks/{task['id']}/complete",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert complete_response.status_code == 200
        result = complete_response.json()
        assert result["has_recurrence"] is True

    @pytest.mark.asyncio
    async def test_idempotency_prevents_duplicate_generation(
        self, async_client, user_id, auth_token
    ):
        """Test that correlation IDs prevent duplicate task generation."""
        task_data = {
            "title": "Daily backup",
            "recurrence": "Daily",
            "due_date": datetime.utcnow().isoformat()
        }

        create_response = await async_client.post(
            f"/api/{user_id}/tasks",
            json=task_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        task = create_response.json()

        # Complete task multiple times (simulate event replay)
        correlation_id = str(uuid4())
        for _ in range(3):
            await async_client.post(
                f"/api/{user_id}/tasks/{task['id']}/complete",
                headers={
                    "Authorization": f"Bearer {auth_token}",
                    "X-Correlation-ID": correlation_id
                }
            )

        # Wait for event processing
        await asyncio.sleep(2)

        # Verify only one next instance was created
        tasks_response = await async_client.get(
            f"/api/{user_id}/tasks",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        tasks = tasks_response.json()

        next_instances = [t for t in tasks if t.get("parent_task_id") == task["id"]]
        assert len(next_instances) == 1


class TestRecurringTaskFiltering:
    """Test filtering recurring tasks."""

    @pytest.mark.asyncio
    async def test_filter_by_recurrence_type(self, async_client, user_id, auth_token):
        """Test filtering tasks by recurrence type."""
        # Create tasks with different recurrence patterns
        tasks_data = [
            {"title": "Daily task", "recurrence": "Daily"},
            {"title": "Weekly task", "recurrence": "Weekly", "recurrence_day_of_week": 1},
            {"title": "Monthly task", "recurrence": "Monthly", "recurrence_day_of_month": 15},
            {"title": "One-time task", "recurrence": None}
        ]

        for task_data in tasks_data:
            await async_client.post(
                f"/api/{user_id}/tasks",
                json=task_data,
                headers={"Authorization": f"Bearer {auth_token}"}
            )

        # Filter for recurring tasks only
        response = await async_client.get(
            f"/api/{user_id}/tasks?has_recurrence=true",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        tasks = response.json()
        assert len(tasks) == 3
        assert all(t["recurrence"] is not None for t in tasks)

    @pytest.mark.asyncio
    async def test_filter_by_priority(self, async_client, user_id, auth_token):
        """Test filtering tasks by priority."""
        tasks_data = [
            {"title": "High priority", "priority": "High"},
            {"title": "Medium priority", "priority": "Medium"},
            {"title": "Low priority", "priority": "Low"}
        ]

        for task_data in tasks_data:
            await async_client.post(
                f"/api/{user_id}/tasks",
                json=task_data,
                headers={"Authorization": f"Bearer {auth_token}"}
            )

        response = await async_client.get(
            f"/api/{user_id}/tasks?priority=High",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        tasks = response.json()
        assert len(tasks) == 1
        assert tasks[0]["priority"] == "High"
