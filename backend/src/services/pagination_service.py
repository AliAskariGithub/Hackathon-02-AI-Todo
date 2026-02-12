"""
Pagination service for task lists.

Implements limit/offset pagination with metadata.
"""

from typing import List, TypeVar, Generic
from pydantic import BaseModel


T = TypeVar('T')


class PaginationMetadata(BaseModel):
    """Metadata for paginated results."""
    total: int
    limit: int
    offset: int
    has_next: bool
    has_previous: bool


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response."""
    items: List[T]
    metadata: PaginationMetadata


class PaginationService:
    """Service for paginating results."""

    @staticmethod
    def paginate(
        items: List[T],
        total: int,
        limit: int = 50,
        offset: int = 0
    ) -> PaginatedResponse[T]:
        """
        Create a paginated response from items.

        Args:
            items: List of items for current page
            total: Total count of items across all pages
            limit: Maximum items per page
            offset: Current offset

        Returns:
            Paginated response with metadata
        """
        has_next = (offset + limit) < total
        has_previous = offset > 0

        metadata = PaginationMetadata(
            total=total,
            limit=limit,
            offset=offset,
            has_next=has_next,
            has_previous=has_previous
        )

        return PaginatedResponse(
            items=items,
            metadata=metadata
        )

    @staticmethod
    def calculate_page_info(
        total: int,
        limit: int = 50,
        offset: int = 0
    ) -> dict:
        """
        Calculate pagination information.

        Args:
            total: Total count of items
            limit: Items per page
            offset: Current offset

        Returns:
            Dictionary with page information
        """
        current_page = (offset // limit) + 1
        total_pages = (total + limit - 1) // limit  # Ceiling division

        return {
            'current_page': current_page,
            'total_pages': total_pages,
            'page_size': limit,
            'total_items': total,
            'has_next': (offset + limit) < total,
            'has_previous': offset > 0,
            'next_offset': offset + limit if (offset + limit) < total else None,
            'previous_offset': max(0, offset - limit) if offset > 0 else None
        }


def create_paginated_response(
    items: List[T],
    total: int,
    limit: int = 50,
    offset: int = 0
) -> PaginatedResponse[T]:
    """
    Convenience function to create paginated response.

    Args:
        items: List of items
        total: Total count
        limit: Page size
        offset: Current offset

    Returns:
        Paginated response
    """
    return PaginationService.paginate(items, total, limit, offset)
