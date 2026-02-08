from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import List
from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession
from ...models import (
    Task, TaskCreate, TaskUpdate, TaskPublic,
    User
)
from ...services.task_service import TaskService
from ...utils.database import get_async_session
from ...utils.logging_config import get_logger
from ...api.deps import get_current_user, verify_user_owns_resource

router = APIRouter(prefix="/api/{user_id}", tags=["tasks"])
logger = get_logger(__name__)


@router.post("/tasks", response_model=TaskPublic, status_code=status.HTTP_201_CREATED)
async def create_task(
    request: Request,
    user_id: UUID,
    task_data: TaskCreate,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
) -> TaskPublic:
    """
    Create a new task for a user.

    Args:
        request: The incoming request object
        user_id: The ID of the user creating the task
        task_data: The task data to create
        current_user: The authenticated user from JWT token
        session: Database session

    Returns:
        The created task
    """
    # Verify that the user_id in the token matches the user_id in the URL path
    await verify_user_owns_resource(request, str(user_id))

    try:
        logger.info(f"Received request to create task for user {user_id}")
        task = await TaskService.create_task(session, user_id, task_data)
        logger.info(f"Successfully created task {task.id} for user {user_id}")
        return task
    except Exception as e:
        logger.error(f"Error creating task for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating task"
        )


@router.get("/tasks", response_model=List[TaskPublic])
async def get_user_tasks(
    request: Request,
    user_id: UUID,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
) -> List[TaskPublic]:
    """
    Get all tasks for a specific user.

    Args:
        request: The incoming request object
        user_id: The ID of the user whose tasks to retrieve
        current_user: The authenticated user from JWT token
        session: Database session

    Returns:
        A list of tasks for the user
    """
    # Verify that the user_id in the token matches the user_id in the URL path
    await verify_user_owns_resource(request, str(user_id))

    try:
        logger.info(f"Received request to get tasks for user {user_id}")
        tasks = await TaskService.get_user_tasks(session, user_id)
        logger.info(f"Returning {len(tasks)} tasks for user {user_id}")
        return tasks
    except Exception as e:
        logger.error(f"Error retrieving tasks for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving tasks"
        )


@router.get("/tasks/{task_id}", response_model=TaskPublic)
async def get_task(
    request: Request,
    user_id: UUID,
    task_id: UUID,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
) -> TaskPublic:
    """
    Get a specific task by ID for a user.

    Args:
        request: The incoming request object
        user_id: The ID of the user
        task_id: The ID of the task to retrieve
        current_user: The authenticated user from JWT token
        session: Database session

    Returns:
        The requested task
    """
    # Verify that the user_id in the token matches the user_id in the URL path
    await verify_user_owns_resource(request, str(user_id))

    try:
        logger.info(f"Received request to get task {task_id} for user {user_id}")
        task = await TaskService.get_task_by_id(session, user_id, task_id)

        if not task:
            logger.warning(f"Task {task_id} not found for user {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        logger.info(f"Successfully retrieved task {task_id} for user {user_id}")
        return task
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving task {task_id} for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving task"
        )


@router.put("/tasks/{task_id}", response_model=TaskPublic)
async def update_task(
    request: Request,
    user_id: UUID,
    task_id: UUID,
    task_data: TaskUpdate,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
) -> TaskPublic:
    """
    Update a specific task for a user.

    Args:
        request: The incoming request object
        user_id: The ID of the user
        task_id: The ID of the task to update
        task_data: The updated task data
        current_user: The authenticated user from JWT token
        session: Database session

    Returns:
        The updated task
    """
    # Verify that the user_id in the token matches the user_id in the URL path
    await verify_user_owns_resource(request, str(user_id))

    try:
        logger.info(f"Received request to update task {task_id} for user {user_id}")
        updated_task = await TaskService.update_task(session, user_id, task_id, task_data)

        if not updated_task:
            logger.warning(f"Task {task_id} not found for user {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        logger.info(f"Successfully updated task {task_id} for user {user_id}")
        return updated_task
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating task {task_id} for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating task"
        )


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    request: Request,
    user_id: UUID,
    task_id: UUID,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
) -> None:
    """
    Delete a specific task for a user.

    Args:
        request: The incoming request object
        user_id: The ID of the user
        task_id: The ID of the task to delete
        current_user: The authenticated user from JWT token
        session: Database session
    """
    # Verify that the user_id in the token matches the user_id in the URL path
    await verify_user_owns_resource(request, str(user_id))

    try:
        logger.info(f"Received request to delete task {task_id} for user {user_id}")
        success = await TaskService.delete_task(session, user_id, task_id)

        if not success:
            logger.warning(f"Task {task_id} not found for user {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        logger.info(f"Successfully deleted task {task_id} for user {user_id}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting task {task_id} for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting task"
        )