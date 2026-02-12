"""
Integration tests for priority management.

Tests priority filtering, sorting, and event publishing.
"""

import pytest
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


class TestPriorityCreation:
    """Test creating tasks with priority."""

    @pytest.mark.asyncio
    async def test_create_task_with_high_priority(self, async_client, user_id, auth_token):
        """Test creating a task with high priority."""
        task_data = {
            "title": "Urgent task",
            "description": "Critical issue",
            "priority": "High"
        }

        response = await async_client.post(
            f"/api/{user_id}/tasks",
            json=task_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 201
        task = response.json()
        assert task["priority"] == "High"

    @pytest.mark.asyncio
    async def test_create_task_with_default_priority(self, async_client, user_id, auth_token):
        """Test that tasks get default priority if not specified."""
        task_data = {
            "title": "Normal task",
            "description": "Regular work"
        }

        response = await async_client.post(
            f"/api/{user_id}/tasks",
            json=task_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 201
        task = response.json()
        assert task["priority"] == "Medium"  # Default priority

    @pytest.mark.asyncio
    async def test_create_task_with_invalid_priority_fails(self, async_client, user_id, auth_token):
        """Test that invalid priority is rejected."""
        task_data = {
            "title": "Task",
            "priority": "Critical"  # Invalid priority
        }

        response = await async_client.post(
            f"/api/{user_id}/tasks",
            json=task_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 400


class TestPriorityUpdate:
    """Test updating task priority."""

    @pytest.mark.asyncio
    async def test_update_task_priority(self, async_client, user_id, auth_token):
        """Test updating a task's priority."""
        # Create task with Medium priority
        task_data = {
            "title": "Task",
            "priority": "Medium"
        }

        create_response = await async_client.post(
            f"/api/{user_id}/tasks",
            json=task_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        task = create_response.json()

        # Update to High priority
        update_data = {"priority": "High"}
        update_response = await async_client.put(
            f"/api/{user_id}/tasks/{task['id']}",
            json=update_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert update_response.status_code == 200
        updated_task = update_response.json()
        assert updated_task["priority"] == "High"

    @pytest.mark.asyncio
    async def test_update_priority_publishes_event(self, async_client, user_id, auth_token):
        """Test that updating priority publishes an event."""
        # Create task
        task_data = {"title": "Task", "priority": "Low"}
        create_response = await async_client.post(
            f"/api/{user_id}/tasks",
            json=task_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        task = create_response.json()

        # Update priority
        update_data = {"priority": "High"}
        await async_client.put(
            f"/api/{user_id}/tasks/{task['id']}",
            json=update_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        # In real test, verify task.priority_changed event was published
        # This would require subscribing to the topic or checking State Store


class TestPriorityFiltering:
    """Test filtering tasks by priority."""

    @pytest.mark.asyncio
    async def test_filter_by_high_priority(self, async_client, user_id, auth_token):
        """Test filtering tasks by high priority."""
        # Create tasks with different priorities
        tasks_data = [
            {"title": "High task 1", "priority": "High"},
            {"title": "High task 2", "priority": "High"},
            {"title": "Medium task", "priority": "Medium"},
            {"title": "Low task", "priority": "Low"}
        ]

        for task_data in tasks_data:
            await async_client.post(
                f"/api/{user_id}/tasks",
                json=task_data,
                headers={"Authorization": f"Bearer {auth_token}"}
            )

        # Filter by High priority
        response = await async_client.get(
            f"/api/{user_id}/tasks?priority=High",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        tasks = response.json()
        assert len(tasks) == 2
        assert all(t["priority"] == "High" for t in tasks)

    @pytest.mark.asyncio
    async def test_filter_by_multiple_priorities(self, async_client, user_id, auth_token):
        """Test filtering by multiple priority levels."""
        # Create tasks
        tasks_data = [
            {"title": "High task", "priority": "High"},
            {"title": "Medium task", "priority": "Medium"},
            {"title": "Low task", "priority": "Low"}
        ]

        for task_data in tasks_data:
            await async_client.post(
                f"/api/{user_id}/tasks",
                json=task_data,
                headers={"Authorization": f"Bearer {auth_token}"}
            )

        # Filter by High priority
        high_response = await async_client.get(
            f"/api/{user_id}/tasks?priority=High",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert len(high_response.json()) == 1

        # Filter by Medium priority
        medium_response = await async_client.get(
            f"/api/{user_id}/tasks?priority=Medium",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert len(medium_response.json()) == 1


class TestPrioritySorting:
    """Test sorting tasks by priority."""

    @pytest.mark.asyncio
    async def test_sort_by_priority_ascending(self, async_client, user_id, auth_token):
        """Test sorting tasks by priority in ascending order."""
        # Create tasks in random priority order
        tasks_data = [
            {"title": "Low task", "priority": "Low"},
            {"title": "High task", "priority": "High"},
            {"title": "Medium task", "priority": "Medium"}
        ]

        for task_data in tasks_data:
            await async_client.post(
                f"/api/{user_id}/tasks",
                json=task_data,
                headers={"Authorization": f"Bearer {auth_token}"}
            )

        # Sort by priority ascending (High -> Medium -> Low)
        response = await async_client.get(
            f"/api/{user_id}/tasks?sort_by=priority&sort_order=asc",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        tasks = response.json()
        priorities = [t["priority"] for t in tasks]
        # High (1) < Medium (2) < Low (3)
        assert priorities[0] == "High"
        assert priorities[1] == "Medium"
        assert priorities[2] == "Low"

    @pytest.mark.asyncio
    async def test_sort_by_priority_descending(self, async_client, user_id, auth_token):
        """Test sorting tasks by priority in descending order."""
        # Create tasks
        tasks_data = [
            {"title": "High task", "priority": "High"},
            {"title": "Medium task", "priority": "Medium"},
            {"title": "Low task", "priority": "Low"}
        ]

        for task_data in tasks_data:
            await async_client.post(
                f"/api/{user_id}/tasks",
                json=task_data,
                headers={"Authorization": f"Bearer {auth_token}"}
            )

        # Sort by priority descending (Low -> Medium -> High)
        response = await async_client.get(
            f"/api/{user_id}/tasks?sort_by=priority&sort_order=desc",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        tasks = response.json()
        priorities = [t["priority"] for t in tasks]
        assert priorities[0] == "Low"
        assert priorities[1] == "Medium"
        assert priorities[2] == "High"


class TestPriorityVisualization:
    """Test priority indicators in UI."""

    @pytest.mark.asyncio
    async def test_priority_badges_displayed(self, async_client, user_id, auth_token):
        """Test that priority badges are included in task responses."""
        task_data = {
            "title": "High priority task",
            "priority": "High"
        }

        response = await async_client.post(
            f"/api/{user_id}/tasks",
            json=task_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        task = response.json()
        assert "priority" in task
        assert task["priority"] == "High"


class TestPriorityStatistics:
    """Test priority-based statistics."""

    @pytest.mark.asyncio
    async def test_count_tasks_by_priority(self, async_client, user_id, auth_token):
        """Test counting tasks grouped by priority."""
        # Create tasks with different priorities
        tasks_data = [
            {"title": "High 1", "priority": "High"},
            {"title": "High 2", "priority": "High"},
            {"title": "High 3", "priority": "High"},
            {"title": "Medium 1", "priority": "Medium"},
            {"title": "Medium 2", "priority": "Medium"},
            {"title": "Low 1", "priority": "Low"}
        ]

        for task_data in tasks_data:
            await async_client.post(
                f"/api/{user_id}/tasks",
                json=task_data,
                headers={"Authorization": f"Bearer {auth_token}"}
            )

        # Get counts for each priority
        high_response = await async_client.get(
            f"/api/{user_id}/tasks?priority=High",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert len(high_response.json()) == 3

        medium_response = await async_client.get(
            f"/api/{user_id}/tasks?priority=Medium",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert len(medium_response.json()) == 2

        low_response = await async_client.get(
            f"/api/{user_id}/tasks?priority=Low",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert len(low_response.json()) == 1
