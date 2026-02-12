"""
Filter service for multi-criteria task filtering.

Implements filtering by status, priority, tags, due_date, and recurrence.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID
from sqlmodel import Session, select, and_, or_

from backend.src.models import Task


class FilterService:
    """Service for filtering tasks by multiple criteria."""

    def __init__(self, db: Session):
        self.db = db

    def filter_tasks(
        self,
        user_id: UUID,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        tags: Optional[List[str]] = None,
        has_recurrence: Optional[bool] = None,
        due_before: Optional[datetime] = None,
        due_after: Optional[datetime] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Task]:
        """
        Filter tasks by multiple criteria.

        Args:
            user_id: The user ID
            status: Filter by status (pending/in_progress/completed/deleted)
            priority: Filter by priority (High/Medium/Low)
            tags: Filter by tags (task must have at least one)
            has_recurrence: Filter by recurrence presence
            due_before: Filter tasks due before this date
            due_after: Filter tasks due after this date
            limit: Maximum number of results
            offset: Pagination offset

        Returns:
            List of filtered tasks
        """
        conditions = [Task.user_id == user_id]

        # Status filter
        if status:
            conditions.append(Task.status == status)

        # Priority filter
        if priority:
            conditions.append(Task.priority == priority)

        # Tags filter (at least one tag matches)
        if tags:
            tag_conditions = [Task.tags.contains([tag]) for tag in tags]
            conditions.append(or_(*tag_conditions))

        # Recurrence filter
        if has_recurrence is not None:
            if has_recurrence:
                conditions.append(Task.recurrence.is_not(None))
            else:
                conditions.append(Task.recurrence.is_(None))

        # Due date filters
        if due_before:
            conditions.append(Task.due_date < due_before)

        if due_after:
            conditions.append(Task.due_date > due_after)

        # Build and execute query
        statement = (
            select(Task)
            .where(and_(*conditions))
            .order_by(Task.updated_at.desc())
            .limit(limit)
            .offset(offset)
        )

        results = self.db.exec(statement).all()
        return list(results)

    def count_filtered_tasks(
        self,
        user_id: UUID,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        tags: Optional[List[str]] = None,
        has_recurrence: Optional[bool] = None,
        due_before: Optional[datetime] = None,
        due_after: Optional[datetime] = None
    ) -> int:
        """
        Count tasks matching filter criteria.

        Args:
            Same as filter_tasks (without limit/offset)

        Returns:
            Count of matching tasks
        """
        conditions = [Task.user_id == user_id]

        if status:
            conditions.append(Task.status == status)

        if priority:
            conditions.append(Task.priority == priority)

        if tags:
            tag_conditions = [Task.tags.contains([tag]) for tag in tags]
            conditions.append(or_(*tag_conditions))

        if has_recurrence is not None:
            if has_recurrence:
                conditions.append(Task.recurrence.is_not(None))
            else:
                conditions.append(Task.recurrence.is_(None))

        if due_before:
            conditions.append(Task.due_date < due_before)

        if due_after:
            conditions.append(Task.due_date > due_after)

        statement = select(Task).where(and_(*conditions))
        results = self.db.exec(statement).all()
        return len(results)


def apply_filters(
    db: Session,
    user_id: UUID,
    filters: dict,
    limit: int = 50,
    offset: int = 0
) -> List[Task]:
    """
    Convenience function to apply filters from a dictionary.

    Args:
        db: Database session
        user_id: The user ID
        filters: Dictionary of filter criteria
        limit: Maximum results
        offset: Pagination offset

    Returns:
        List of filtered tasks
    """
    service = FilterService(db)
    return service.filter_tasks(
        user_id=user_id,
        status=filters.get('status'),
        priority=filters.get('priority'),
        tags=filters.get('tags'),
        has_recurrence=filters.get('has_recurrence'),
        due_before=filters.get('due_before'),
        due_after=filters.get('due_after'),
        limit=limit,
        offset=offset
    )
