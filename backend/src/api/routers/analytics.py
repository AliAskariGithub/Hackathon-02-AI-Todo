from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Dict, Any
from ...models import User, Task
from ...utils.database import get_async_session
from ...utils.logging_config import get_logger
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

@router.get("/stats", response_model=Dict[str, Any])
async def get_app_stats(
    session: AsyncSession = Depends(get_async_session)
) -> Dict[str, Any]:
    """
    Get application-wide statistics including:
    - Total active users
    - Total tasks created
    - System uptime (placeholder)
    - Other relevant metrics
    """
    try:
        logger.info("Fetching application statistics")

        # Count total users
        user_count_statement = select(func.count(User.id))
        user_result = await session.execute(user_count_statement)
        total_users = user_result.scalar_one_or_none() or 0

        # Count total tasks
        task_count_statement = select(func.count(Task.id))
        task_result = await session.execute(task_count_statement)
        total_tasks = task_result.scalar_one_or_none() or 0

        # Count completed tasks
        completed_task_statement = select(func.count(Task.id)).where(Task.completed == True)
        completed_result = await session.execute(completed_task_statement)
        completed_tasks = completed_result.scalar_one_or_none() or 0

        # Count all users (active or not)
        stats = {
            "all_users": total_users,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "uptime_hours": 24,  # Placeholder - in a real app, this would track actual uptime
            "server_status": "online"
        }

        logger.info(f"Returning stats: {stats}")
        return stats

    except Exception as e:
        logger.error(f"Error fetching application statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching application statistics"
        )