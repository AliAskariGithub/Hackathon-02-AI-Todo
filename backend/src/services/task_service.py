from typing import List, Optional
from sqlmodel import select, func
from uuid import UUID
from ..models import Task, TaskCreate, TaskUpdate
from ..utils.logging_config import get_logger
from sqlalchemy.exc import IntegrityError, DisconnectionError, OperationalError
from sqlalchemy.ext.asyncio import AsyncSession


logger = get_logger(__name__)


class TaskService:
    @staticmethod
    async def create_task(session: AsyncSession, user_id: UUID, task_data: TaskCreate) -> Task:
        """Create a new task for a user."""
        logger.info(f"Creating task for user {user_id}")

        # Create task with user_id from path parameter
        task = Task(
            title=task_data.title,
            description=task_data.description,
            completed=task_data.completed,
            user_id=user_id
        )
        session.add(task)
        await session.commit()
        await session.refresh(task)

        logger.info(f"Task {task.id} created successfully for user {user_id}")
        return task

    @staticmethod
    async def get_user_tasks(session: AsyncSession, user_id: UUID) -> List[Task]:
        """Get all tasks for a specific user."""
        logger.info(f"Retrieving tasks for user {user_id}")

        statement = select(Task).where(Task.user_id == user_id)
        result = await session.execute(statement)
        tasks = result.scalars().all()

        logger.info(f"Found {len(tasks)} tasks for user {user_id}")
        return tasks

    @staticmethod
    async def get_task_by_id(session: AsyncSession, user_id: UUID, task_id: UUID) -> Optional[Task]:
        """Get a specific task by ID for a user."""
        logger.info(f"Retrieving task {task_id} for user {user_id}")

        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        result = await session.execute(statement)
        task = result.scalar_one_or_none()

        if task:
            logger.info(f"Task {task_id} found for user {user_id}")
        else:
            logger.info(f"Task {task_id} not found for user {user_id}")

        return task

    @staticmethod
    async def update_task(session: AsyncSession, user_id: UUID, task_id: UUID, task_data: TaskUpdate) -> Optional[Task]:
        """Update a specific task for a user."""
        logger.info(f"Updating task {task_id} for user {user_id}")

        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        result = await session.execute(statement)
        task = result.scalar_one_or_none()

        if not task:
            logger.warning(f"Task {task_id} not found for user {user_id}")
            return None

        # Update the task with provided data
        update_data = task_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)

        task.updated_at = func.now()  # Update timestamp

        try:
            await session.commit()
            await session.refresh(task)
            logger.info(f"Task {task_id} updated successfully for user {user_id}")
            return task
        except IntegrityError as e:
            logger.error(f"Error updating task {task_id}: {str(e)}")
            await session.rollback()
            raise

    @staticmethod
    async def delete_task(session: AsyncSession, user_id: UUID, task_id: UUID) -> bool:
        """Delete a specific task for a user."""
        logger.info(f"Deleting task {task_id} for user {user_id}")

        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        result = await session.execute(statement)
        task = result.scalar_one_or_none()

        if not task:
            logger.warning(f"Task {task_id} not found for user {user_id}")
            return False

        await session.delete(task)
        await session.commit()

        logger.info(f"Task {task_id} deleted successfully for user {user_id}")
        return True