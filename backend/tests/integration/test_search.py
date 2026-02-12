"""
Integration tests for advanced search and filtering.

Tests search, filtering, sorting, and natural language queries.
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
    return "test-token"


class TestKeywordSearch:
    """Test keyword-based search."""

    @pytest.mark.asyncio
    async def test_search_by_title(self, async_client, user_id, auth_token):
        """Test searching tasks by title keyword."""
        # Create tasks with different titles
        tasks_data = [
            {"title": "Team meeting", "description": "Weekly sync"},
            {"title": "Client meeting", "description": "Project review"},
            {"title": "Code review", "description": "Review PR"}
        ]

        for task_data in tasks_data:
            await async_client.post(
                f"/api/{user_id}/tasks",
                json=task_data,
                headers={"Authorization": f"Bearer {auth_token}"}
            )

        # Search for "meeting"
        response = await async_client.get(
            "/api/search/tasks?query=meeting",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 200
        results = response.json()
        assert results["metadata"]["total"] >= 2
        assert all("meeting" in item["title"].lower() for item in results["items"])

    @pytest.mark.asyncio
    async def test_search_by_description(self, async_client, user_id, auth_token):
        """Test searching tasks by description keyword."""
        task_data = {"title": "Fix bug", "description": "Urgent production issue"}

        await async_client.post(
            f"/api/{user_id}/tasks",
            json=task_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        response = await async_client.get(
            "/api/search/tasks?query=urgent",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 200
        results = response.json()
        assert results["metadata"]["total"] >= 1


class TestMultiCriteriaFiltering:
    """Test filtering by multiple criteria."""

    @pytest.mark.asyncio
    async def test_filter_by_status(self, async_client, user_id, auth_token):
        """Test filtering tasks by status."""
        # Create tasks with different statuses
        tasks_data = [
            {"title": "Pending task", "status": "pending"},
            {"title": "In progress task", "status": "in_progress"},
            {"title": "Completed task", "status": "completed"}
        ]

        for task_data in tasks_data:
            await async_client.post(
                f"/api/{user_id}/tasks",
                json=task_data,
                headers={"Authorization": f"Bearer {auth_token}"}
            )

        # Filter by completed status
        response = await async_client.get(
            "/api/search/tasks?status=completed",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        results = response.json()
        assert all(item["status"] == "completed" for item in results["items"])

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
            "/api/search/tasks?priority=High",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        results = response.json()
        assert all(item["priority"] == "High" for item in results["items"])

    @pytest.mark.asyncio
    async def test_filter_by_tags(self, async_client, user_id, auth_token):
        """Test filtering tasks by tags."""
        tasks_data = [
            {"title": "Work task", "tags": ["work", "urgent"]},
            {"title": "Personal task", "tags": ["personal"]},
            {"title": "Meeting task", "tags": ["work", "meeting"]}
        ]

        for task_data in tasks_data:
            await async_client.post(
                f"/api/{user_id}/tasks",
                json=task_data,
                headers={"Authorization": f"Bearer {auth_token}"}
            )

        response = await async_client.get(
            "/api/search/tasks?tags=work",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        results = response.json()
        assert all("work" in item.get("tags", []) for item in results["items"])

    @pytest.mark.asyncio
    async def test_filter_by_recurrence(self, async_client, user_id, auth_token):
        """Test filtering tasks by recurrence presence."""
        tasks_data = [
            {"title": "Daily task", "recurrence": "Daily"},
            {"title": "One-time task", "recurrence": None}
        ]

        for task_data in tasks_data:
            await async_client.post(
                f"/api/{user_id}/tasks",
                json=task_data,
                headers={"Authorization": f"Bearer {auth_token}"}
            )

        response = await async_client.get(
            "/api/search/tasks?has_recurrence=true",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        results = response.json()
        assert all(item.get("recurrence") is not None for item in results["items"])


class TestSorting:
    """Test task sorting."""

    @pytest.mark.asyncio
    async def test_sort_by_priority(self, async_client, user_id, auth_token):
        """Test sorting tasks by priority."""
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

        response = await async_client.get(
            "/api/search/tasks?sort_by=priority&sort_order=asc",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        results = response.json()
        priorities = [item["priority"] for item in results["items"]]
        # High (1) < Medium (2) < Low (3) in ascending order
        assert priorities[0] == "High"

    @pytest.mark.asyncio
    async def test_sort_by_due_date(self, async_client, user_id, auth_token):
        """Test sorting tasks by due date."""
        now = datetime.utcnow()
        tasks_data = [
            {"title": "Task 1", "due_date": (now + timedelta(days=3)).isoformat()},
            {"title": "Task 2", "due_date": (now + timedelta(days=1)).isoformat()},
            {"title": "Task 3", "due_date": (now + timedelta(days=2)).isoformat()}
        ]

        for task_data in tasks_data:
            await async_client.post(
                f"/api/{user_id}/tasks",
                json=task_data,
                headers={"Authorization": f"Bearer {auth_token}"}
            )

        response = await async_client.get(
            "/api/search/tasks?sort_by=due_date&sort_order=asc",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        results = response.json()
        # Verify tasks are sorted by due date ascending
        due_dates = [item.get("due_date") for item in results["items"] if item.get("due_date")]
        assert due_dates == sorted(due_dates)


class TestPagination:
    """Test pagination."""

    @pytest.mark.asyncio
    async def test_pagination_limit(self, async_client, user_id, auth_token):
        """Test pagination with limit."""
        # Create 15 tasks
        for i in range(15):
            await async_client.post(
                f"/api/{user_id}/tasks",
                json={"title": f"Task {i}"},
                headers={"Authorization": f"Bearer {auth_token}"}
            )

        response = await async_client.get(
            "/api/search/tasks?limit=10",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        results = response.json()
        assert len(results["items"]) == 10
        assert results["metadata"]["total"] >= 15
        assert results["metadata"]["has_next"] is True

    @pytest.mark.asyncio
    async def test_pagination_offset(self, async_client, user_id, auth_token):
        """Test pagination with offset."""
        response = await async_client.get(
            "/api/search/tasks?limit=5&offset=10",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        results = response.json()
        assert results["metadata"]["offset"] == 10
        assert results["metadata"]["has_previous"] is True


class TestNaturalLanguageSearch:
    """Test natural language query parsing."""

    @pytest.mark.asyncio
    async def test_natural_language_high_priority(self, async_client, user_id, auth_token):
        """Test natural language query for high priority tasks."""
        # Create tasks
        tasks_data = [
            {"title": "Urgent task", "priority": "High"},
            {"title": "Normal task", "priority": "Medium"}
        ]

        for task_data in tasks_data:
            await async_client.post(
                f"/api/{user_id}/tasks",
                json=task_data,
                headers={"Authorization": f"Bearer {auth_token}"}
            )

        response = await async_client.post(
            "/api/search/natural-language",
            json={"query": "show me high priority tasks"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 200
        result = response.json()
        assert result["parsed_filters"]["priority"] == "High"
        assert all(item["priority"] == "High" for item in result["results"]["items"])

    @pytest.mark.asyncio
    async def test_natural_language_completed_tasks(self, async_client, user_id, auth_token):
        """Test natural language query for completed tasks."""
        response = await async_client.post(
            "/api/search/natural-language",
            json={"query": "find completed tasks"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        result = response.json()
        assert result["parsed_filters"]["status"] == "completed"


class TestTagListing:
    """Test unique tag listing."""

    @pytest.mark.asyncio
    async def test_get_unique_tags(self, async_client, user_id, auth_token):
        """Test retrieving all unique tags for user."""
        tasks_data = [
            {"title": "Task 1", "tags": ["work", "urgent"]},
            {"title": "Task 2", "tags": ["personal", "urgent"]},
            {"title": "Task 3", "tags": ["work", "meeting"]}
        ]

        for task_data in tasks_data:
            await async_client.post(
                f"/api/{user_id}/tasks",
                json=task_data,
                headers={"Authorization": f"Bearer {auth_token}"}
            )

        response = await async_client.get(
            "/api/search/tags",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 200
        tags = response.json()
        assert "work" in tags
        assert "urgent" in tags
        assert "personal" in tags
        assert "meeting" in tags
        assert len(set(tags)) == len(tags)  # No duplicates
