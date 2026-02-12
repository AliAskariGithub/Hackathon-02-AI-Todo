"""
Sort service for task sorting.

Implements sorting by due_date, priority, created_at, updated_at.
"""

from typing import List, Literal
from uuid import UUID
from sqlmodel import Session, select

from backend.src.models import Task


SortField = Literal['due_date', 'priority', 'created_at', 'updated_at', 'title']
SortOrder = Literal['asc', 'desc']


class SortService:
    """Service for sorting tasks."""

    # Priority order mapping for sorting
    PRIORITY_ORDER = {
        'High': 1,
        'Medium': 2,
        'Low': 3
    }

    def __init__(self, db: Session):
        self.db = db

    def sort_tasks(
        self,
        tasks: List[Task],
        sort_by: SortField = 'updated_at',
        sort_order: SortOrder = 'desc'
    ) -> List[Task]:
        """
        Sort tasks by specified field and order.

        Args:
            tasks: List of tasks to sort
            sort_by: Field to sort by
            sort_order: Sort order (asc/desc)

        Returns:
            Sorted list of tasks
        """
        reverse = (sort_order == 'desc')

        if sort_by == 'priority':
            # Sort by priority using custom order
            return sorted(
                tasks,
                key=lambda t: self.PRIORITY_ORDER.get(t.priority or 'Medium', 2),
                reverse=reverse
            )
        elif sort_by == 'due_date':
            # Sort by due date, handling None values
            return sorted(
                tasks,
                key=lambda t: t.due_date or datetime.max if not reverse else datetime.min,
                reverse=reverse
            )
        elif sort_by == 'title':
            # Sort alphabetically by title
            return sorted(
                tasks,
                key=lambda t: t.title.lower(),
                reverse=reverse
            )
        elif sort_by == 'created_at':
            return sorted(
                tasks,
                key=lambda t: t.created_at,
                reverse=reverse
            )
        else:  # updated_at (default)
            return sorted(
                tasks,
                key=lambda t: t.updated_at,
                reverse=reverse
            )

    def get_sorted_tasks_query(
        self,
        user_id: UUID,
        sort_by: SortField = 'updated_at',
        sort_order: SortOrder = 'desc',
        limit: int = 50,
        offset: int = 0
    ):
        """
        Build a query for sorted tasks (more efficient for large datasets).

        Args:
            user_id: The user ID
            sort_by: Field to sort by
            sort_order: Sort order (asc/desc)
            limit: Maximum results
            offset: Pagination offset

        Returns:
            SQLModel query statement
        """
        statement = select(Task).where(Task.user_id == user_id)

        # Apply sorting
        if sort_by == 'due_date':
            order_col = Task.due_date
        elif sort_by == 'created_at':
            order_col = Task.created_at
        elif sort_by == 'title':
            order_col = Task.title
        elif sort_by == 'priority':
            # For priority, we'll need to sort in memory or use CASE statement
            # For now, default to updated_at and sort in memory
            order_col = Task.updated_at
        else:  # updated_at
            order_col = Task.updated_at

        if sort_order == 'desc':
            statement = statement.order_by(order_col.desc())
        else:
            statement = statement.order_by(order_col.asc())

        statement = statement.limit(limit).offset(offset)

        return statement


def sort_task_list(
    tasks: List[Task],
    sort_by: SortField = 'updated_at',
    sort_order: SortOrder = 'desc'
) -> List[Task]:
    """
    Convenience function to sort a list of tasks.

    Args:
        tasks: List of tasks
        sort_by: Field to sort by
        sort_order: Sort order

    Returns:
        Sorted list of tasks
    """
    service = SortService(None)
    return service.sort_tasks(tasks, sort_by, sort_order)
