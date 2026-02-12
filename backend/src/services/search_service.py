"""
Search service for keyword-based task search.

Implements server-side keyword search across task title and description.
"""

from typing import List, Optional
from uuid import UUID
from sqlmodel import Session, select, or_, col

from ..models import Task


class SearchService:
    """Service for searching tasks by keyword."""

    def __init__(self, db: Session):
        self.db = db

    def search_tasks(
        self,
        user_id: UUID,
        query: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Task]:
        """
        Search tasks by keyword in title and description.

        Args:
            user_id: The user ID
            query: Search query string
            limit: Maximum number of results
            offset: Pagination offset

        Returns:
            List of matching tasks
        """
        # Build search query
        search_pattern = f"%{query}%"

        statement = (
            select(Task)
            .where(Task.user_id == user_id)
            .where(
                or_(
                    col(Task.title).ilike(search_pattern),
                    col(Task.description).ilike(search_pattern)
                )
            )
            .order_by(Task.updated_at.desc())
            .limit(limit)
            .offset(offset)
        )

        results = self.db.exec(statement).all()
        return list(results)

    def search_tasks_by_tags(
        self,
        user_id: UUID,
        tags: List[str],
        match_all: bool = False,
        limit: int = 50,
        offset: int = 0
    ) -> List[Task]:
        """
        Search tasks by tags.

        Args:
            user_id: The user ID
            tags: List of tags to search for
            match_all: If True, task must have all tags; if False, any tag matches
            limit: Maximum number of results
            offset: Pagination offset

        Returns:
            List of matching tasks
        """
        statement = select(Task).where(Task.user_id == user_id)

        if match_all:
            # Task must have all specified tags
            for tag in tags:
                statement = statement.where(Task.tags.contains([tag]))
        else:
            # Task must have at least one of the specified tags
            conditions = [Task.tags.contains([tag]) for tag in tags]
            statement = statement.where(or_(*conditions))

        statement = statement.order_by(Task.updated_at.desc()).limit(limit).offset(offset)

        results = self.db.exec(statement).all()
        return list(results)

    def get_unique_tags(self, user_id: UUID) -> List[str]:
        """
        Get all unique tags used by a user.

        Args:
            user_id: The user ID

        Returns:
            List of unique tag strings
        """
        statement = select(Task.tags).where(
            Task.user_id == user_id,
            Task.tags.is_not(None)
        )

        results = self.db.exec(statement).all()

        # Flatten and deduplicate tags
        all_tags = set()
        for tag_list in results:
            if tag_list:
                all_tags.update(tag_list)

        return sorted(list(all_tags))


def search_tasks_by_keyword(
    db: Session,
    user_id: UUID,
    query: str,
    limit: int = 50,
    offset: int = 0
) -> List[Task]:
    """
    Convenience function to search tasks by keyword.

    Args:
        db: Database session
        user_id: The user ID
        query: Search query
        limit: Maximum results
        offset: Pagination offset

    Returns:
        List of matching tasks
    """
    service = SearchService(db)
    return service.search_tasks(user_id, query, limit, offset)
