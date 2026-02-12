"""
API endpoints for advanced search and filtering.

Handles keyword search, multi-criteria filtering, sorting, and natural language queries.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session

from backend.src.database import get_session
from backend.src.models import Task
from backend.src.services.search_service import SearchService
from backend.src.services.filter_service import FilterService
from backend.src.services.sort_service import SortService, SortField, SortOrder
from backend.src.services.pagination_service import PaginationService, PaginatedResponse
from backend.src.services.nlp_query_service import NLPQueryService
from backend.src.deps import get_current_user


router = APIRouter(prefix="/api/search", tags=["search"])


@router.get("/tasks", response_model=PaginatedResponse[Task])
async def search_tasks(
    query: Optional[str] = Query(None, description="Search query for title/description"),
    status: Optional[str] = Query(None, description="Filter by status"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    has_recurrence: Optional[bool] = Query(None, description="Filter by recurrence presence"),
    due_before: Optional[datetime] = Query(None, description="Filter tasks due before date"),
    due_after: Optional[datetime] = Query(None, description="Filter tasks due after date"),
    sort_by: SortField = Query("updated_at", description="Field to sort by"),
    sort_order: SortOrder = Query("desc", description="Sort order"),
    limit: int = Query(50, ge=1, le=100, description="Maximum results per page"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    db: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """
    Search and filter tasks with pagination and sorting.

    Supports:
    - Keyword search in title/description
    - Multi-criteria filtering (status, priority, tags, recurrence, due dates)
    - Sorting by multiple fields
    - Pagination with limit/offset
    """
    user_id = UUID(current_user["id"])

    # Apply search if query provided
    if query:
        search_service = SearchService(db)
        tasks = search_service.search_tasks(user_id, query, limit=1000)  # Get all matches first
    else:
        # Apply filters
        filter_service = FilterService(db)
        tasks = filter_service.filter_tasks(
            user_id=user_id,
            status=status,
            priority=priority,
            tags=tags,
            has_recurrence=has_recurrence,
            due_before=due_before,
            due_after=due_after,
            limit=1000  # Get all matches first
        )

    # Apply sorting
    sort_service = SortService(db)
    sorted_tasks = sort_service.sort_tasks(tasks, sort_by, sort_order)

    # Apply pagination
    total = len(sorted_tasks)
    paginated_tasks = sorted_tasks[offset:offset + limit]

    # Create paginated response
    pagination_service = PaginationService()
    return pagination_service.paginate(paginated_tasks, total, limit, offset)


@router.post("/natural-language")
async def natural_language_search(
    query_data: dict,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """
    Search tasks using natural language query.

    Parses natural language into structured filters and executes search.

    Example queries:
    - "show me high priority tasks"
    - "find completed tasks from today"
    - "urgent tasks due this week"
    - "daily recurring tasks tagged with work"
    """
    user_id = UUID(current_user["id"])
    query = query_data.get("query", "")

    # Parse natural language query
    nlp_service = NLPQueryService()
    filters = nlp_service.parse_query(query)

    # Extract filters
    search_query = filters.get('search_query')
    status = filters.get('status')
    priority = filters.get('priority')
    tags = filters.get('tags')
    recurrence = filters.get('recurrence')
    due_before = filters.get('due_before')
    due_after = filters.get('due_after')

    # Apply search if keywords present
    if search_query:
        search_service = SearchService(db)
        tasks = search_service.search_tasks(user_id, search_query, limit=1000)
    else:
        # Apply filters
        filter_service = FilterService(db)
        tasks = filter_service.filter_tasks(
            user_id=user_id,
            status=status,
            priority=priority,
            tags=tags,
            has_recurrence=(recurrence is not None),
            due_before=due_before,
            due_after=due_after,
            limit=1000
        )

    # Filter by specific recurrence type if specified
    if recurrence:
        tasks = [t for t in tasks if t.recurrence == recurrence]

    # Sort by relevance (updated_at desc)
    sort_service = SortService(db)
    sorted_tasks = sort_service.sort_tasks(tasks, 'updated_at', 'desc')

    # Apply pagination
    total = len(sorted_tasks)
    paginated_tasks = sorted_tasks[offset:offset + limit]

    # Generate query description
    query_description = nlp_service.generate_query_description(filters)

    # Create response
    pagination_service = PaginationService()
    paginated_response = pagination_service.paginate(paginated_tasks, total, limit, offset)

    return {
        "query": query,
        "parsed_filters": filters,
        "description": query_description,
        "results": paginated_response
    }


@router.get("/tags", response_model=List[str])
async def get_user_tags(
    db: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """
    Get all unique tags used by the authenticated user.

    Returns a sorted list of tag strings for use in filter UI.
    """
    user_id = UUID(current_user["id"])
    search_service = SearchService(db)
    tags = search_service.get_unique_tags(user_id)
    return tags
