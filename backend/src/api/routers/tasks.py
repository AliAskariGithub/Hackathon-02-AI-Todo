from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlmodel.ext.asyncio.session import AsyncSession
from ...models import (
    Task, TaskCreate, TaskUpdate, TaskPublic,
    User
)
from ...services.task_service import TaskService
from ...utils.database import get_async_session
from ...utils.logging_config import get_logger
from ...api.deps import get_current_user, verify_user_owns_resource
from ...dapr_sdk_utils.pubsub import DaprPubSub
from ...middleware.correlation import get_correlation_id_uuid

router = APIRouter(prefix="/api/{user_id}", tags=["tasks"])
logger = get_logger(__name__)
pubsub = DaprPubSub()


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

        # Publish task.created event
        correlation_id = get_correlation_id_uuid(request)
        task_data_dict = {
            "task_id": str(task.id),
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "priority": task.priority,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "recurrence": task.recurrence,
            "recurrence_day_of_week": task.recurrence_day_of_week,
            "recurrence_day_of_month": task.recurrence_day_of_month,
            "tags": task.tags,
            "user_id": str(task.user_id),
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat(),
            "completed": task.completed
        }

        # Dapr pubsub is handled gracefully
        logger.info(f"Task created event logged for {task.id}")

        return TaskPublic.from_orm(task)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating task for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating task"
        )


@router.get("/tasks")
async def get_user_tasks(
    request: Request,
    user_id: UUID,
    status_filter: Optional[str] = Query(None, alias="status"),
    priority: Optional[str] = None,
    has_recurrence: Optional[bool] = None,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Get all tasks for a specific user with optional filtering.

    Args:
        request: The incoming request object
        user_id: The ID of the user whose tasks to retrieve
        status: Optional status filter (pending, in_progress, completed, deleted)
        priority: Optional priority filter (High, Medium, Low)
        has_recurrence: Optional filter for tasks with recurrence patterns
        current_user: The authenticated user from JWT token
        session: Database session

    Returns:
        A list of tasks for the user with completed field
    """
    # Verify that the user_id in the token matches the user_id in the URL path
    await verify_user_owns_resource(request, str(user_id))

    try:
        logger.info(f"Received request to get tasks for user {user_id} with filters: status={status_filter}, priority={priority}, has_recurrence={has_recurrence}")

        # Get tasks with filters
        tasks = await TaskService.get_user_tasks_with_filters(
            session=session,
            user_id=user_id,
            status=status_filter,
            priority=priority,
            has_recurrence=has_recurrence
        )

        # Add completed field for frontend compatibility
        tasks_with_completed = [
            {
                **TaskPublic.from_orm(task).dict(),
                "completed": task.status == "completed"
            }
            for task in tasks
        ]

        logger.info(f"Returning {len(tasks_with_completed)} tasks for user {user_id}")
        return tasks_with_completed
    except Exception as e:
        import traceback
        logger.error(f"Error retrieving tasks for user {user_id}: {str(e)}")
        logger.error(f"Full traceback:\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving tasks"
        )


@router.get("/tasks/{task_id}")
async def get_task(
    request: Request,
    user_id: UUID,
    task_id: UUID,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Get a specific task by ID for a user.

    Args:
        request: The incoming request object
        user_id: The ID of the user
        task_id: The ID of the task to retrieve
        current_user: The authenticated user from JWT token
        session: Database session

    Returns:
        The requested task with completed field
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

        # Add completed field for frontend compatibility
        return {
            **TaskPublic.from_orm(task).dict(),
            "completed": task.status == "completed"
        }
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

        # Publish task.updated event
        correlation_id = get_correlation_id_uuid(request)
        task_data_dict = {
            "task_id": str(updated_task.id),
            "title": updated_task.title,
            "description": updated_task.description,
            "status": updated_task.status,
            "priority": updated_task.priority,
            "due_date": updated_task.due_date.isoformat() if updated_task.due_date else None,
            "recurrence": updated_task.recurrence,
            "recurrence_day_of_week": updated_task.recurrence_day_of_week,
            "recurrence_day_of_month": updated_task.recurrence_day_of_month,
            "tags": updated_task.tags,
            "updated_at": updated_task.updated_at.isoformat() if updated_task.updated_at else None
        }

        try:
            pubsub.publish_task_updated(
                task_id=updated_task.id,
                user_id=user_id,
                task_data=task_data_dict,
                correlation_id=correlation_id
            )
            logger.info(f"Successfully published task.updated event for task {task_id}")
        except Exception as pubsub_error:
            # Log pubsub error but don't fail the request
            logger.warning(f"Failed to publish task.updated event: {str(pubsub_error)}")

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

        # Fetch task data before deletion for event publishing
        task = await TaskService.get_task_by_id(session, user_id, task_id)
        if not task:
            logger.warning(f"Task {task_id} not found for user {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        # Store task data for event publishing
        task_data_dict = {
            "task_id": str(task.id),
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "priority": task.priority,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "recurrence": task.recurrence,
            "recurrence_day_of_week": task.recurrence_day_of_week,
            "recurrence_day_of_month": task.recurrence_day_of_month,
            "tags": task.tags,
            "deleted_at": datetime.utcnow().isoformat()
        }

        # Delete the task
        success = await TaskService.delete_task(session, user_id, task_id)

        if not success:
            logger.warning(f"Failed to delete task {task_id} for user {user_id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error deleting task"
            )

        logger.info(f"Successfully deleted task {task_id} for user {user_id}")

        # Publish task.deleted event
        correlation_id = get_correlation_id_uuid(request)

        try:
            pubsub.publish_task_deleted(
                task_id=task.id,
                user_id=user_id,
                task_data=task_data_dict,
                correlation_id=correlation_id
            )
            logger.info(f"Successfully published task.deleted event for task {task_id}")
        except Exception as pubsub_error:
            # Log pubsub error but don't fail the request
            logger.warning(f"Failed to publish task.deleted event: {str(pubsub_error)}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting task {task_id} for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting task"
        )


@router.post("/tasks/{task_id}/complete", response_model=dict)
async def complete_task(
    request: Request,
    user_id: UUID,
    task_id: UUID,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
) -> dict:
    """
    Mark a task as completed and trigger recurring task generation if applicable.

    This endpoint:
    1. Marks the task as completed
    2. Sets completed_at timestamp
    3. Publishes task.completed event
    4. Event subscriber generates next recurring instance (if recurrence exists)

    Args:
        request: The incoming request object
        user_id: The ID of the user
        task_id: The ID of the task to complete
        current_user: The authenticated user from JWT token
        session: Database session

    Returns:
        Dictionary with completed task and next instance info
    """
    # Verify that the user_id in the token matches the user_id in the URL path
    await verify_user_owns_resource(request, str(user_id))

    try:
        logger.info(f"Received request to complete task {task_id} for user {user_id}")

        # Get the task
        task = await TaskService.get_task_by_id(session, user_id, task_id)
        if not task:
            logger.warning(f"Task {task_id} not found for user {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        # Mark task as completed
        task.status = "completed"
        task.completed_at = datetime.utcnow()
        task.updated_at = datetime.utcnow()

        # Save to database
        session.add(task)
        await session.commit()
        await session.refresh(task)

        # Get correlation ID from request
        correlation_id = get_correlation_id_uuid(request)

        # Cancel any scheduled reminders for this task
        try:
            from ...services.reminder_service import ReminderService
            reminder_service = ReminderService(session)
            cancelled_count = await reminder_service.cancel_task_reminders(
                session=session,
                task_id=task_id,
                user_id=user_id,
                correlation_id=correlation_id
            )
            if cancelled_count > 0:
                logger.info(f"Cancelled {cancelled_count} reminders for completed task {task_id}")
        except Exception as reminder_error:
            # Log error but don't fail the task completion
            logger.warning(f"Failed to cancel reminders for task {task_id}: {str(reminder_error)}")

        # Publish task.completed event
        # This will trigger the event subscriber to generate next recurring instance
        task_data = {
            "task_id": str(task.id),
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "priority": task.priority,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "recurrence": task.recurrence,
            "recurrence_day_of_week": task.recurrence_day_of_week,
            "recurrence_day_of_month": task.recurrence_day_of_month,
            "tags": task.tags,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "parent_task_id": str(task.parent_task_id) if task.parent_task_id else None
        }

        try:
            pubsub.publish_task_completed(
                task_id=task.id,
                user_id=user_id,
                task_data=task_data,
                correlation_id=correlation_id
            )
            logger.info(f"Successfully completed task {task_id} and published event")
        except Exception as pubsub_error:
            # Log pubsub error but don't fail the request
            logger.warning(f"Failed to publish task.completed event: {str(pubsub_error)}")

        # Return response with completed field for frontend compatibility
        response = {
            "task": {
                **TaskPublic.from_orm(task).dict(),
                "completed": task.status == "completed"
            },
            "message": "Task completed successfully",
            "has_recurrence": bool(task.recurrence),
            "next_instance_will_be_generated": bool(task.recurrence)
        }

        return response

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        logger.error(f"Error completing task {task_id} for user {user_id}: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error completing task"
        )


# Internal endpoint for service-to-service communication via Dapr
@router.post("/tasks/internal", response_model=TaskPublic, status_code=status.HTTP_201_CREATED)
async def create_task_internal(
    request: Request,
    user_id: UUID,
    task_data: TaskCreate,
    session: AsyncSession = Depends(get_async_session)
) -> TaskPublic:
    """
    Internal task creation endpoint for service-to-service communication.

    This endpoint is called by other microservices (e.g., recurring-service)
    via Dapr Service Invocation. It does not require JWT authentication
    as it's only accessible through Dapr's service mesh.

    Args:
        request: The incoming request object
        user_id: The ID of the user creating the task
        task_data: The task data to create
        session: Database session

    Returns:
        The created task
    """
    try:
        logger.info(f"Received internal request to create task for user {user_id}")

        # Validate recurring task properties if recurrence is specified
        if task_data.recurrence:
            recurrence = task_data.recurrence.lower()

            if recurrence not in ['daily', 'weekly', 'monthly']:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid recurrence pattern: {task_data.recurrence}. Must be 'Daily', 'Weekly', or 'Monthly'."
                )

            # Validate weekly recurrence has day_of_week
            if recurrence == 'weekly' and task_data.recurrence_day_of_week is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="recurrence_day_of_week is required for weekly recurrence (0=Monday, 6=Sunday)"
                )

            # Validate day_of_week range
            if task_data.recurrence_day_of_week is not None:
                if not 0 <= task_data.recurrence_day_of_week <= 6:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="recurrence_day_of_week must be between 0 (Monday) and 6 (Sunday)"
                    )

            # Validate monthly recurrence has day_of_month
            if recurrence == 'monthly' and task_data.recurrence_day_of_month is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="recurrence_day_of_month is required for monthly recurrence (1-31)"
                )

            # Validate day_of_month range
            if task_data.recurrence_day_of_month is not None:
                if not 1 <= task_data.recurrence_day_of_month <= 31:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="recurrence_day_of_month must be between 1 and 31"
                    )

        # Create the task
        task = await TaskService.create_task(session, user_id, task_data)
        logger.info(f"Successfully created task {task.id} for user {user_id} (internal)")

        # Publish task.created event
        correlation_id = get_correlation_id_uuid(request)
        task_data_dict = {
            "task_id": str(task.id),
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "priority": task.priority,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "recurrence": task.recurrence,
            "recurrence_day_of_week": task.recurrence_day_of_week,
            "recurrence_day_of_month": task.recurrence_day_of_month,
            "tags": task.tags,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "parent_task_id": str(task.parent_task_id) if task.parent_task_id else None
        }

        try:
            pubsub.publish_task_created(
                task_id=task.id,
                user_id=user_id,
                task_data=task_data_dict,
                correlation_id=correlation_id
            )
            logger.info(f"Successfully published task.created event for task {task.id} (internal)")
        except Exception as pubsub_error:
            # Log pubsub error but don't fail the request
            logger.warning(f"Failed to publish task.created event: {str(pubsub_error)}")

        return task
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating task for user {user_id} (internal): {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating task"
        )