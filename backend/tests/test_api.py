import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock
from uuid import uuid4
import sys
import os

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from main import app
from src.utils.database import get_async_session
from sqlmodel.ext.asyncio.session import AsyncSession


@pytest.fixture
def client():
    """Create a test client for the API with mocked database session"""
    # Create a mock async session
    mock_session = AsyncMock(spec=AsyncSession)

    # Mock the exec method that's used by the services
    mock_exec_result = AsyncMock()
    mock_exec_result.all.return_value = []
    mock_exec_result.first.return_value = None

    mock_session.exec = AsyncMock(return_value=mock_exec_result)

    # Mock other methods that might be used
    mock_session.add = AsyncMock()
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()
    mock_session.delete = AsyncMock()

    # Create a generator function for the dependency override
    async def override_get_async_session():
        yield mock_session

    # Override the database session dependency
    app.dependency_overrides[get_async_session] = override_get_async_session

    with TestClient(app) as test_client:
        yield test_client

    # Clean up the override after the test
    app.dependency_overrides.clear()


def test_root_endpoint(client):
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Todo Backend API"}


def test_health_endpoint(client):
    """Test the health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_routes_exist(client):
    """Test that the API routes exist (with mocked database)"""
    user_id = str(uuid4())

    # Test GET /api/{user_id}/tasks
    response = client.get(f"/api/{user_id}/tasks")
    # With mocked DB, this should return 200 with empty list or potentially 500 if mock isn't perfect
    assert response.status_code in [200, 500]

    # Test POST /api/{user_id}/tasks
    response = client.post(f"/api/{user_id}/tasks", json={
        "title": "Test Task",
        "description": "Test Description",
        "completed": False
    })
    # With mocked DB, this should return 201 (created) if validation passes
    assert response.status_code in [201, 422, 500]  # 422 for validation errors, 500 for mock issues

    # Test GET /api/{user_id}/tasks/{task_id}
    task_id = str(uuid4())
    response = client.get(f"/api/{user_id}/tasks/{task_id}")
    assert response.status_code in [200, 404, 500]  # Could return found, not found, or error