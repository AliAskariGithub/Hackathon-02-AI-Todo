"""
Task management tools for the Model Context Protocol (MCP) server.
Each tool implements the required functionality with user authentication context.
"""
import json
import asyncio
from typing import Dict, Any, Optional, List
from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from src.models import Task, TaskUpdate, TaskCreate
from src.services.task_service import TaskService
from src.utils.database import get_async_session_factory
from .error_codes import (
    TASK_NOT_FOUND,
    UNAUTHORIZED_ACCESS,
    INVALID_INPUT,
    DATABASE_ERROR,
    AUTHENTICATION_ERROR,
    ERROR_MESSAGES
)


# Core task management functions

async def add_task(user_id: str, title: str, description: Optional[str] = None,
                  priority: Optional[str] = None, due_date: Optional[str] = None,
                  recurrence: Optional[str] = None, recurrence_day_of_week: Optional[int] = None,
                  recurrence_day_of_month: Optional[int] = None, tags: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Add a new task for the authenticated user with full feature support.

    Args:
        user_id: The authenticated user's ID (from JWT token)
        title: Task title
        description: Optional task description
        priority: Optional priority (High, Medium, Low)
        due_date: Optional due date in ISO format
        recurrence: Optional recurrence pattern (Daily, Weekly, Monthly)
        recurrence_day_of_week: Day of week for weekly recurrence (0-6)
        recurrence_day_of_month: Day of month for monthly recurrence (1-31)
        tags: Optional list of tags

    Returns:
        Dict with success status and task_id
    """
    try:
        user_uuid = UUID(user_id)
        session_factory = get_async_session_factory()

        async with session_factory() as session:
            task_create = TaskCreate(
                title=title,
                description=description or "",
                priority=priority or "Medium",
                status="pending",
                due_date=due_date,
                recurrence=recurrence,
                recurrence_day_of_week=recurrence_day_of_week,
                recurrence_day_of_month=recurrence_day_of_month,
                tags=tags or []
            )

            created_task = await TaskService.create_task(session, user_uuid, task_create)

            return {
                "success": True,
                "task_id": str(created_task.id),
                "message": f"Task '{created_task.title}' has been created",
                "task": {
                    "id": str(created_task.id),
                    "title": created_task.title,
                    "priority": created_task.priority,
                    "status": created_task.status,
                    "recurrence": created_task.recurrence,
                    "tags": created_task.tags
                }
            }
    except ValueError:
        return {
            "success": False,
            "error_code": INVALID_INPUT,
            "message": ERROR_MESSAGES[INVALID_INPUT]
        }
    except SQLAlchemyError:
        return {
            "success": False,
            "error_code": DATABASE_ERROR,
            "message": ERROR_MESSAGES[DATABASE_ERROR]
        }
    except Exception as e:
        return {
            "success": False,
            "error_code": "UNKNOWN_ERROR",
            "message": f"An unexpected error occurred: {str(e)}"
        }


async def list_tasks(user_id: str, status: str = "all", priority: Optional[str] = None,
                    has_recurrence: Optional[bool] = None, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
    """
    List all tasks for the authenticated user with advanced filtering.

    Args:
        user_id: The authenticated user's ID (from JWT token)
        status: Filter by status ('all', 'pending', 'in_progress', 'completed')
        priority: Filter by priority (High, Medium, Low)
        has_recurrence: Filter tasks with/without recurrence
        limit: Maximum number of tasks to return
        offset: Offset for pagination

    Returns:
        Dict with success status and list of tasks
    """
    try:
        user_uuid = UUID(user_id)
        session_factory = get_async_session_factory()

        async with session_factory() as session:
            # Use the service's filter method
            tasks = await TaskService.get_user_tasks_with_filters(
                session=session,
                user_id=user_uuid,
                status=status if status != "all" else None,
                priority=priority,
                has_recurrence=has_recurrence
            )

            # Apply pagination
            paginated_tasks = tasks[offset:offset + limit]

            # Convert tasks to dictionaries
            task_list = []
            for task in paginated_tasks:
                task_dict = {
                    "id": str(task.id),
                    "title": task.title,
                    "description": task.description or "",
                    "status": task.status,
                    "priority": task.priority,
                    "completed": task.status == "completed",
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "recurrence": task.recurrence,
                    "recurrence_day_of_week": task.recurrence_day_of_week,
                    "recurrence_day_of_month": task.recurrence_day_of_month,
                    "tags": task.tags or [],
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat() if task.updated_at else task.created_at.isoformat(),
                    "user_id": str(task.user_id)
                }
                task_list.append(task_dict)

            return {
                "success": True,
                "tasks": task_list,
                "total_count": len(tasks),
                "returned_count": len(task_list),
                "message": f"Retrieved {len(task_list)} tasks for user"
            }
    except ValueError:
        return {
            "success": False,
            "error_code": INVALID_INPUT,
            "message": ERROR_MESSAGES[INVALID_INPUT]
        }
    except SQLAlchemyError:
        return {
            "success": False,
            "error_code": DATABASE_ERROR,
            "message": ERROR_MESSAGES[DATABASE_ERROR]
        }
    except Exception as e:
        return {
            "success": False,
            "error_code": "UNKNOWN_ERROR",
            "message": f"An unexpected error occurred: {str(e)}"
        }


async def complete_task(user_id: str, task_id: str) -> Dict[str, Any]:
    """
    Mark a task as completed for the authenticated user.

    Args:
        user_id: The authenticated user's ID (from JWT token)
        task_id: The ID of the task to complete

    Returns:
        Dict with success status and completion details
    """
    try:
        user_uuid = UUID(user_id)
        task_uuid = UUID(task_id)
        session_factory = get_async_session_factory()

        async with session_factory() as session:
            task_update = TaskUpdate(status="completed")
            updated_task = await TaskService.update_task(session, user_uuid, task_uuid, task_update)

            if not updated_task:
                return {
                    "success": False,
                    "error_code": TASK_NOT_FOUND,
                    "message": ERROR_MESSAGES[TASK_NOT_FOUND]
                }

            return {
                "success": True,
                "message": f"Task '{updated_task.title}' has been marked as completed",
                "task": {
                    "id": str(updated_task.id),
                    "title": updated_task.title,
                    "status": updated_task.status
                }
            }
    except ValueError:
        return {
            "success": False,
            "error_code": INVALID_INPUT,
            "message": ERROR_MESSAGES[INVALID_INPUT]
        }
    except SQLAlchemyError:
        return {
            "success": False,
            "error_code": DATABASE_ERROR,
            "message": ERROR_MESSAGES[DATABASE_ERROR]
        }
    except Exception as e:
        return {
            "success": False,
            "error_code": "UNKNOWN_ERROR",
            "message": f"An unexpected error occurred: {str(e)}"
        }


async def update_task(user_id: str, task_id: str, title: Optional[str] = None,
                     description: Optional[str] = None, priority: Optional[str] = None,
                     status: Optional[str] = None, due_date: Optional[str] = None,
                     tags: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Update task properties for the authenticated user.

    Args:
        user_id: The authenticated user's ID (from JWT token)
        task_id: The ID of the task to update
        title: New title for the task (optional)
        description: New description for the task (optional)
        priority: New priority for the task (optional)
        status: New status for the task (optional)
        due_date: New due date for the task (optional)
        tags: New tags for the task (optional)

    Returns:
        Dict with success status and update details
    """
    try:
        user_uuid = UUID(user_id)
        task_uuid = UUID(task_id)

        # Prepare update data
        update_data = {}
        if title is not None:
            update_data["title"] = title
        if description is not None:
            update_data["description"] = description
        if priority is not None:
            update_data["priority"] = priority
        if status is not None:
            update_data["status"] = status
        if due_date is not None:
            update_data["due_date"] = due_date
        if tags is not None:
            update_data["tags"] = tags

        task_update = TaskUpdate(**update_data)
        session_factory = get_async_session_factory()

        async with session_factory() as session:
            updated_task = await TaskService.update_task(session, user_uuid, task_uuid, task_update)

            if not updated_task:
                return {
                    "success": False,
                    "error_code": TASK_NOT_FOUND,
                    "message": ERROR_MESSAGES[TASK_NOT_FOUND]
                }

            return {
                "success": True,
                "message": f"Task '{updated_task.title}' has been updated",
                "task": {
                    "id": str(updated_task.id),
                    "title": updated_task.title,
                    "priority": updated_task.priority,
                    "status": updated_task.status,
                    "tags": updated_task.tags
                }
            }
    except ValueError:
        return {
            "success": False,
            "error_code": INVALID_INPUT,
            "message": ERROR_MESSAGES[INVALID_INPUT]
        }
    except SQLAlchemyError:
        return {
            "success": False,
            "error_code": DATABASE_ERROR,
            "message": ERROR_MESSAGES[DATABASE_ERROR]
        }
    except Exception as e:
        return {
            "success": False,
            "error_code": "UNKNOWN_ERROR",
            "message": f"An unexpected error occurred: {str(e)}"
        }


async def delete_task(user_id: str, task_id: str) -> Dict[str, Any]:
    """
    Delete a task for the authenticated user.

    Args:
        user_id: The authenticated user's ID (from JWT token)
        task_id: The ID of the task to delete

    Returns:
        Dict with success status
    """
    try:
        user_uuid = UUID(user_id)
        task_uuid = UUID(task_id)
        session_factory = get_async_session_factory()

        async with session_factory() as session:
            success = await TaskService.delete_task(session, user_uuid, task_uuid)

            if not success:
                return {
                    "success": False,
                    "error_code": TASK_NOT_FOUND,
                    "message": ERROR_MESSAGES[TASK_NOT_FOUND]
                }

            return {
                "success": True,
                "message": "Task has been deleted"
            }
    except ValueError:
        return {
            "success": False,
            "error_code": INVALID_INPUT,
            "message": ERROR_MESSAGES[INVALID_INPUT]
        }
    except SQLAlchemyError:
        return {
            "success": False,
            "error_code": DATABASE_ERROR,
            "message": ERROR_MESSAGES[DATABASE_ERROR]
        }
    except Exception as e:
        return {
            "success": False,
            "error_code": "UNKNOWN_ERROR",
            "message": f"An unexpected error occurred: {str(e)}"
        }


# JSON Schema definitions for MCP tools

ADD_TASK_SCHEMA = {
    "name": "add_task",
    "description": "Add a new task with support for priority, recurrence, and tags",
    "parameters": {
        "type": "object",
        "properties": {
            "user_id": {
                "type": "string",
                "description": "Authenticated user's ID (automatically injected)"
            },
            "title": {
                "type": "string",
                "description": "Task title"
            },
            "description": {
                "type": "string",
                "description": "Optional task description"
            },
            "priority": {
                "type": "string",
                "enum": ["High", "Medium", "Low"],
                "description": "Task priority (default: Medium)"
            },
            "due_date": {
                "type": "string",
                "format": "date-time",
                "description": "Optional due date in ISO format"
            },
            "recurrence": {
                "type": "string",
                "enum": ["Daily", "Weekly", "Monthly"],
                "description": "Optional recurrence pattern"
            },
            "recurrence_day_of_week": {
                "type": "integer",
                "minimum": 0,
                "maximum": 6,
                "description": "Day of week for weekly recurrence (0=Monday, 6=Sunday)"
            },
            "recurrence_day_of_month": {
                "type": "integer",
                "minimum": 1,
                "maximum": 31,
                "description": "Day of month for monthly recurrence"
            },
            "tags": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Optional list of tags"
            }
        },
        "required": ["user_id", "title"]
    }
}

LIST_TASKS_SCHEMA = {
    "name": "list_tasks",
    "description": "List all tasks with advanced filtering by status, priority, and recurrence",
    "parameters": {
        "type": "object",
        "properties": {
            "user_id": {
                "type": "string",
                "description": "Authenticated user's ID (automatically injected)"
            },
            "status": {
                "type": "string",
                "enum": ["all", "pending", "in_progress", "completed"],
                "description": "Filter tasks by status (default: all)"
            },
            "priority": {
                "type": "string",
                "enum": ["High", "Medium", "Low"],
                "description": "Filter tasks by priority"
            },
            "has_recurrence": {
                "type": "boolean",
                "description": "Filter tasks with/without recurrence"
            },
            "limit": {
                "type": "integer",
                "minimum": 1,
                "maximum": 100,
                "default": 20,
                "description": "Maximum number of tasks to return"
            },
            "offset": {
                "type": "integer",
                "minimum": 0,
                "default": 0,
                "description": "Offset for pagination"
            }
        },
        "required": ["user_id"]
    }
}

COMPLETE_TASK_SCHEMA = {
    "name": "complete_task",
    "description": "Mark a task as completed",
    "parameters": {
        "type": "object",
        "properties": {
            "user_id": {
                "type": "string",
                "description": "Authenticated user's ID (automatically injected)"
            },
            "task_id": {
                "type": "string",
                "description": "ID of the task to complete"
            }
        },
        "required": ["user_id", "task_id"]
    }
}

UPDATE_TASK_SCHEMA = {
    "name": "update_task",
    "description": "Update task properties including priority, status, and tags",
    "parameters": {
        "type": "object",
        "properties": {
            "user_id": {
                "type": "string",
                "description": "Authenticated user's ID (automatically injected)"
            },
            "task_id": {
                "type": "string",
                "description": "ID of the task to update"
            },
            "title": {
                "type": "string",
                "description": "New title for the task"
            },
            "description": {
                "type": "string",
                "description": "New description for the task"
            },
            "priority": {
                "type": "string",
                "enum": ["High", "Medium", "Low"],
                "description": "New priority for the task"
            },
            "status": {
                "type": "string",
                "enum": ["pending", "in_progress", "completed"],
                "description": "New status for the task"
            },
            "due_date": {
                "type": "string",
                "format": "date-time",
                "description": "New due date for the task"
            },
            "tags": {
                "type": "array",
                "items": {"type": "string"},
                "description": "New tags for the task"
            }
        },
        "required": ["user_id", "task_id"]
    }
}

DELETE_TASK_SCHEMA = {
    "name": "delete_task",
    "description": "Delete a task",
    "parameters": {
        "type": "object",
        "properties": {
            "user_id": {
                "type": "string",
                "description": "Authenticated user's ID (automatically injected)"
            },
            "task_id": {
                "type": "string",
                "description": "ID of the task to delete"
            }
        },
        "required": ["user_id", "task_id"]
    }
}

SEARCH_TASKS_SCHEMA = {
    "name": "search_tasks",
    "description": "Search tasks by title (partial match, case-insensitive)",
    "parameters": {
        "type": "object",
        "properties": {
            "user_id": {
                "type": "string",
                "description": "Authenticated user's ID (automatically injected)"
            },
            "query": {
                "type": "string",
                "description": "Search query to match against task titles"
            },
            "limit": {
                "type": "integer",
                "minimum": 1,
                "maximum": 50,
                "default": 10,
                "description": "Maximum number of results to return (default: 10)"
            }
        },
        "required": ["user_id", "query"]
    }
}


# Authentication helper

def verify_tool_authentication(params: Dict[str, Any]) -> str:
    """
    Verify that the tool has proper authentication context.

    Args:
        params: Dictionary containing tool parameters including user_id

    Returns:
        str: The validated user_id

    Raises:
        ValueError: If authentication is missing or invalid
    """
    user_id = params.get("user_id")
    if not user_id:
        raise ValueError("Authentication context missing: user_id is required for all MCP tools")
    return user_id


# Wrapper functions for MCP tool execution

async def add_task_wrapper(params: Dict[str, Any]) -> Dict[str, Any]:
    """Wrapper function for the add_task MCP tool that validates parameters."""
    try:
        user_id = verify_tool_authentication(params)
        title = params.get("title")
        description = params.get("description", "")
        priority = params.get("priority")
        due_date = params.get("due_date")
        recurrence = params.get("recurrence")
        recurrence_day_of_week = params.get("recurrence_day_of_week")
        recurrence_day_of_month = params.get("recurrence_day_of_month")
        tags = params.get("tags")

        if not title:
            return {
                "success": False,
                "error_code": INVALID_INPUT,
                "message": "title is a required parameter"
            }

        result = await add_task(user_id, title, description, priority, due_date,
                               recurrence, recurrence_day_of_week, recurrence_day_of_month, tags)
        return result
    except ValueError as e:
        return {
            "success": False,
            "error_code": "AUTHENTICATION_ERROR",
            "message": f"Authentication error: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error_code": "EXECUTION_ERROR",
            "message": f"Error executing add_task: {str(e)}"
        }


async def list_tasks_wrapper(params: Dict[str, Any]) -> Dict[str, Any]:
    """Wrapper function for the list_tasks MCP tool that validates parameters."""
    try:
        user_id = verify_tool_authentication(params)
        status = params.get("status", "all")
        priority = params.get("priority")
        has_recurrence = params.get("has_recurrence")
        limit = params.get("limit", 20)
        offset = params.get("offset", 0)

        result = await list_tasks(user_id, status, priority, has_recurrence, limit, offset)
        return result
    except ValueError as e:
        return {
            "success": False,
            "error_code": "AUTHENTICATION_ERROR",
            "message": f"Authentication error: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error_code": "EXECUTION_ERROR",
            "message": f"Error executing list_tasks: {str(e)}"
        }


async def complete_task_wrapper(params: Dict[str, Any]) -> Dict[str, Any]:
    """Wrapper function for the complete_task MCP tool that validates parameters."""
    try:
        user_id = verify_tool_authentication(params)
        task_id = params.get("task_id")

        if not task_id:
            return {
                "success": False,
                "error_code": INVALID_INPUT,
                "message": "task_id is a required parameter"
            }

        result = await complete_task(user_id, task_id)
        return result
    except ValueError as e:
        return {
            "success": False,
            "error_code": "AUTHENTICATION_ERROR",
            "message": f"Authentication error: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error_code": "EXECUTION_ERROR",
            "message": f"Error executing complete_task: {str(e)}"
        }


async def update_task_wrapper(params: Dict[str, Any]) -> Dict[str, Any]:
    """Wrapper function for the update_task MCP tool that validates parameters."""
    try:
        user_id = verify_tool_authentication(params)
        task_id = params.get("task_id")
        title = params.get("title")
        description = params.get("description")
        priority = params.get("priority")
        status = params.get("status")
        due_date = params.get("due_date")
        tags = params.get("tags")

        if not task_id:
            return {
                "success": False,
                "error_code": INVALID_INPUT,
                "message": "task_id is a required parameter"
            }

        result = await update_task(user_id, task_id, title, description, priority, status, due_date, tags)
        return result
    except ValueError as e:
        return {
            "success": False,
            "error_code": "AUTHENTICATION_ERROR",
            "message": f"Authentication error: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error_code": "EXECUTION_ERROR",
            "message": f"Error executing update_task: {str(e)}"
        }


async def delete_task_wrapper(params: Dict[str, Any]) -> Dict[str, Any]:
    """Wrapper function for the delete_task MCP tool that validates parameters."""
    try:
        user_id = verify_tool_authentication(params)
        task_id = params.get("task_id")

        if not task_id:
            return {
                "success": False,
                "error_code": INVALID_INPUT,
                "message": "task_id is a required parameter"
            }

        result = await delete_task(user_id, task_id)
        return result
    except ValueError as e:
        return {
            "success": False,
            "error_code": "AUTHENTICATION_ERROR",
            "message": f"Authentication error: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error_code": "EXECUTION_ERROR",
            "message": f"Error executing delete_task: {str(e)}"
        }


async def search_tasks(user_id: str, query: str, limit: int = 10) -> Dict[str, Any]:
    """
    Search tasks by title (partial match) for the authenticated user.

    Args:
        user_id: The authenticated user's ID (from JWT token)
        query: Search query to match against task titles
        limit: Maximum number of results to return

    Returns:
        Dict with success status and matching tasks
    """
    try:
        user_uuid = UUID(user_id)
        session_factory = get_async_session_factory()

        async with session_factory() as session:
            # Get all tasks for the user
            tasks = await TaskService.get_user_tasks(session, user_uuid)

            # Filter tasks by title (case-insensitive partial match)
            query_lower = query.lower()
            matching_tasks = [
                task for task in tasks
                if query_lower in task.title.lower()
            ]

            # Limit results
            matching_tasks = matching_tasks[:limit]

            # Convert tasks to dictionaries
            task_list = []
            for task in matching_tasks:
                task_dict = {
                    "id": str(task.id),
                    "title": task.title,
                    "description": task.description or "",
                    "status": task.status,
                    "priority": task.priority,
                    "completed": task.status == "completed",
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "recurrence": task.recurrence,
                    "tags": task.tags or [],
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat() if task.updated_at else task.created_at.isoformat()
                }
                task_list.append(task_dict)

            return {
                "success": True,
                "tasks": task_list,
                "count": len(task_list),
                "message": f"Found {len(task_list)} tasks matching '{query}'"
            }
    except ValueError:
        return {
            "success": False,
            "error_code": INVALID_INPUT,
            "message": ERROR_MESSAGES[INVALID_INPUT]
        }
    except SQLAlchemyError:
        return {
            "success": False,
            "error_code": DATABASE_ERROR,
            "message": ERROR_MESSAGES[DATABASE_ERROR]
        }
    except Exception as e:
        return {
            "success": False,
            "error_code": "UNKNOWN_ERROR",
            "message": f"An unexpected error occurred: {str(e)}"
        }


async def search_tasks_wrapper(params: Dict[str, Any]) -> Dict[str, Any]:
    """Wrapper function for the search_tasks MCP tool that validates parameters."""
    try:
        user_id = verify_tool_authentication(params)
        query = params.get("query")
        limit = params.get("limit", 10)

        if not query:
            return {
                "success": False,
                "error_code": INVALID_INPUT,
                "message": "query is a required parameter"
            }

        result = await search_tasks(user_id, query, limit)
        return result
    except ValueError as e:
        return {
            "success": False,
            "error_code": "AUTHENTICATION_ERROR",
            "message": f"Authentication error: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error_code": "EXECUTION_ERROR",
            "message": f"Error executing search_tasks: {str(e)}"
        }
