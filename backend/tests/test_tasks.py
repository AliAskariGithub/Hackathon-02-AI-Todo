import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from src.models import Task, User
from src.services.task_service import TaskService


def test_models_structure():
    """Test that the models have the correct structure"""
    # Test that Task model has required fields
    assert hasattr(Task, 'id')
    assert hasattr(Task, 'title')
    assert hasattr(Task, 'description')
    assert hasattr(Task, 'completed')
    assert hasattr(Task, 'user_id')
    assert hasattr(Task, 'created_at')
    assert hasattr(Task, 'updated_at')

    # Test that User model has required fields
    assert hasattr(User, 'id')
    assert hasattr(User, 'email')
    assert hasattr(User, 'created_at')
    assert hasattr(User, 'updated_at')


@pytest.mark.asyncio
async def test_task_service_create_task():
    """Test creating a task"""
    session_mock = AsyncMock()
    user_id = uuid4()
    task_data = MagicMock()
    task_data.model_dump.return_value = {
        "title": "Test Task",
        "description": "Test Description",
        "completed": False
    }

    # Create a mock task object
    mock_task = MagicMock(spec=Task)
    mock_task.id = uuid4()
    mock_task.title = "Test Task"
    mock_task.description = "Test Description"
    mock_task.completed = False
    mock_task.user_id = user_id

    session_mock.add = MagicMock()
    session_mock.commit = AsyncMock()
    session_mock.refresh = AsyncMock()

    # Mock the refresh to set the id
    async def mock_refresh(obj):
        if obj == mock_task:
            obj.id = uuid4()

    session_mock.refresh.side_effect = mock_refresh

    # Call the service method
    result = await TaskService.create_task(session_mock, user_id, task_data)

    # Assertions
    assert result is not None
    session_mock.add.assert_called_once()
    session_mock.commit.assert_awaited_once()
    session_mock.refresh.assert_awaited_once()


@pytest.mark.asyncio
async def test_task_service_get_user_tasks():
    """Test getting user tasks"""
    session_mock = AsyncMock()
    user_id = uuid4()

    # Create mock tasks
    mock_task1 = MagicMock(spec=Task)
    mock_task1.id = uuid4()
    mock_task1.title = "Task 1"
    mock_task1.description = "Description 1"
    mock_task1.completed = False
    mock_task1.user_id = user_id

    mock_task2 = MagicMock(spec=Task)
    mock_task2.id = uuid4()
    mock_task2.title = "Task 2"
    mock_task2.description = "Description 2"
    mock_task2.completed = True
    mock_task2.user_id = user_id

    mock_result = MagicMock()
    mock_result.all.return_value = [mock_task1, mock_task2]
    session_mock.exec = AsyncMock(return_value=mock_result)

    # Call the service method
    result = await TaskService.get_user_tasks(session_mock, user_id)

    # Assertions
    assert len(result) == 2
    assert result[0].title == "Task 1"
    assert result[1].title == "Task 2"
    session_mock.exec.assert_awaited_once()


@pytest.mark.asyncio
async def test_task_service_get_task_by_id():
    """Test getting a specific task by ID"""
    session_mock = AsyncMock()
    user_id = uuid4()
    task_id = uuid4()

    # Create mock task
    mock_task = MagicMock(spec=Task)
    mock_task.id = task_id
    mock_task.title = "Specific Task"
    mock_task.description = "Specific Description"
    mock_task.completed = False
    mock_task.user_id = user_id

    mock_result = MagicMock()
    mock_result.first.return_value = mock_task
    session_mock.exec = AsyncMock(return_value=mock_result)

    # Call the service method
    result = await TaskService.get_task_by_id(session_mock, user_id, task_id)

    # Assertions
    assert result is not None
    assert result.title == "Specific Task"
    session_mock.exec.assert_awaited_once()


@pytest.mark.asyncio
async def test_task_service_update_task():
    """Test updating a task"""
    session_mock = AsyncMock()
    user_id = uuid4()
    task_id = uuid4()

    # Create mock task
    mock_task = MagicMock(spec=Task)
    mock_task.id = task_id
    mock_task.title = "Original Task"
    mock_task.description = "Original Description"
    mock_task.completed = False
    mock_task.user_id = user_id

    mock_result = MagicMock()
    mock_result.first.return_value = mock_task
    session_mock.exec = AsyncMock(return_value=mock_result)

    # Create mock update data
    task_update_data = MagicMock()
    task_update_data.model_dump.return_value = {"title": "Updated Task", "completed": True}

    # Call the service method
    result = await TaskService.update_task(session_mock, user_id, task_id, task_update_data)

    # Assertions
    assert result is not None
    assert result.title == "Updated Task"
    session_mock.exec.assert_awaited()
    session_mock.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_task_service_delete_task():
    """Test deleting a task"""
    session_mock = AsyncMock()
    user_id = uuid4()
    task_id = uuid4()

    # Create mock task
    mock_task = MagicMock(spec=Task)
    mock_task.id = task_id
    mock_task.user_id = user_id

    mock_result = MagicMock()
    mock_result.first.return_value = mock_task
    session_mock.exec = AsyncMock(return_value=mock_result)

    # Call the service method
    result = await TaskService.delete_task(session_mock, user_id, task_id)

    # Assertions
    assert result is True
    session_mock.delete.assert_called_once_with(mock_task)
    session_mock.commit.assert_awaited_once()