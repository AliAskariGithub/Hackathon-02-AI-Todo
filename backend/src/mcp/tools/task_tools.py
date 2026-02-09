"""
Task management tools for the Model Context Protocol (MCP) server.
Each tool implements the required functionality with user authentication context.
"""
import json
import asyncio
import asyncio
from typing import Dict, Any, Optional, List
from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from src.models import Task, TaskUpdate, TaskCreateInternal
from src.services.task_service import TaskService
from src.utils.database import get_async_session
from .error_codes import (
    TASK_NOT_FOUND,
    UNAUTHORIZED_ACCESS,
    INVALID_INPUT,
    DATABASE_ERROR,
    AUTHENTICATION_ERROR,
    ERROR_MESSAGES
)


async def add_task(user_id: str, title: str, description: Optional[str] = None, due_date: Optional[str] = None) -> Dict[str, Any]:
    """
    Add a new task for the authenticated user.

    Args:
        user_id: The authenticated user's ID (from JWT token)
        title: Task title
        description: Optional task description
        due_date: Optional due date in ISO format

    Returns:
        Dict with success status and task_id
    """
    try:
        # Convert user_id to UUID
        user_uuid = UUID(user_id)

        # Get the async engine and session factory to create a session properly
        from src.utils.database import get_async_engine, get_async_session_factory

        # Create an async session using the proper session factory
        session_factory = get_async_session_factory()
        async with session_factory() as session:
            # Create a TaskCreate object (the standard model for creating tasks)
            # The TaskService.create_task method will handle associating with the user_id
            from src.models import TaskCreate as TaskCreateModel
            task_create = TaskCreateModel(
                title=title,
                description=description,
                completed=False  # New tasks are not completed by default
            )

            # Use TaskService to create the task - the service handles adding the user_id
            from src.services.task_service import TaskService
            created_task = await TaskService.create_task(
                session,
                user_uuid,
                task_create
            )

            return {
                "success": True,
                "task_id": str(created_task.id),
                "message": f"Task '{created_task.title}' has been created"
            }

    except ValueError:
        # UUID conversion failed
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
        # Convert user_id and task_id to UUIDs
        user_uuid = UUID(user_id)
        task_uuid = UUID(task_id)

        # Create async session using the session factory approach
        from src.utils.database import get_async_session_factory
        session_factory = get_async_session_factory()

        # Create a session instance using the factory
        async with session_factory() as session:
            # Update the task with completed status
            task_update = TaskUpdate(completed=True)
            updated_task = await TaskService.update_task(
                session,
                user_uuid,
                task_uuid,
                task_update
            )

            if not updated_task:
                return {
                    "success": False,
                    "error_code": TASK_NOT_FOUND,
                    "message": ERROR_MESSAGES[TASK_NOT_FOUND]
                }

            return {
                "success": True,
                "message": f"Task '{updated_task.title}' has been marked as completed"
            }

    except ValueError:
        # UUID conversion failed
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


async def list_tasks(user_id: str, status: str = "all", limit: int = 20, offset: int = 0) -> Dict[str, Any]:
    """
    List all tasks for the authenticated user.

    Args:
        user_id: The authenticated user's ID (from JWT token)
        status: Filter by status ('all', 'pending', 'completed')
        limit: Maximum number of tasks to return
        offset: Offset for pagination

    Returns:
        Dict with success status and list of tasks
    """
    try:
        # Convert user_id to UUID
        user_uuid = UUID(user_id)

        # Create async session using the session factory approach
        from src.utils.database import get_async_session_factory
        session_factory = get_async_session_factory()

        # Create a session instance using the factory
        async with session_factory() as session:
            # Get all tasks for the user
            user_tasks = await TaskService.get_user_tasks(session, user_uuid)

            # Apply status filter if needed
            if status != "all":
                if status == "completed":
                    filtered_tasks = [task for task in user_tasks if task.completed]
                elif status == "pending":
                    filtered_tasks = [task for task in user_tasks if not task.completed]
                else:
                    # Invalid status, return error
                    return {
                        "success": False,
                        "error_code": INVALID_INPUT,
                        "message": "Invalid status parameter. Use 'all', 'pending', or 'completed'."
                    }
            else:
                filtered_tasks = user_tasks

            # Apply pagination
            paginated_tasks = filtered_tasks[offset:offset + limit]

            # Convert tasks to dictionaries
            task_list = []
            for task in paginated_tasks:
                task_dict = {
                    "id": str(task.id),
                    "title": task.title,
                    "description": task.description or "",
                    "completed": task.completed,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat() if task.updated_at else task.created_at.isoformat(),
                    "user_id": str(task.user_id)
                }
                task_list.append(task_dict)

            return {
                "success": True,
                "tasks": task_list,
                "total_count": len(filtered_tasks),
                "message": f"Retrieved {len(task_list)} tasks for user"
            }

    except ValueError:
        # UUID conversion failed
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
                     description: Optional[str] = None, due_date: Optional[str] = None,
                     status: Optional[str] = None) -> Dict[str, Any]:
    """
    Update task properties for the authenticated user.

    Args:
        user_id: The authenticated user's ID (from JWT token)
        task_id: The ID of the task to update
        title: New title for the task (optional)
        description: New description for the task (optional)
        due_date: New due date for the task (optional)
        status: New status for the task (optional)

    Returns:
        Dict with success status and update details
    """
    try:
        # Convert user_id and task_id to UUIDs
        user_uuid = UUID(user_id)
        task_uuid = UUID(task_id)

        # Prepare update data
        update_data = {}
        if title is not None:
            update_data["title"] = title
        if description is not None:
            update_data["description"] = description
        if status is not None:
            # Map status string to boolean for completed field
            if status == "completed":
                update_data["completed"] = True
            elif status == "pending":
                update_data["completed"] = False

        # Create TaskUpdate object with the data
        task_update = TaskUpdate(**update_data)

        # Create async session using the session factory approach
        from src.utils.database import get_async_session_factory
        session_factory = get_async_session_factory()

        # Create a session instance using the factory
        async with session_factory() as session:
            # Update the task
            updated_task = await TaskService.update_task(
                session,
                user_uuid,
                task_uuid,
                task_update
            )

            if not updated_task:
                return {
                    "success": False,
                    "error_code": TASK_NOT_FOUND,
                    "message": ERROR_MESSAGES[TASK_NOT_FOUND]
                }

            return {
                "success": True,
                "message": f"Task '{updated_task.title}' has been updated"
            }

    except ValueError:
        # UUID conversion failed
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
        # Convert user_id and task_id to UUIDs
        user_uuid = UUID(user_id)
        task_uuid = UUID(task_id)

        # Create async session using the session factory approach
        from src.utils.database import get_async_session_factory
        session_factory = get_async_session_factory()

        # Create a session instance using the factory
        async with session_factory() as session:
            # Delete the task
            success = await TaskService.delete_task(
                session,
                user_uuid,
                task_uuid
            )

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
        # UUID conversion failed
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
    "description": "Add a new task for the authenticated user",
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
            "due_date": {
                "type": "string",
                "format": "date-time",
                "description": "Optional due date for the task in ISO format"
            }
        },
        "required": ["user_id", "title"]
    }
}

LIST_TASKS_SCHEMA = {
    "name": "list_tasks",
    "description": "List all tasks for the authenticated user",
    "parameters": {
        "type": "object",
        "properties": {
            "user_id": {
                "type": "string",
                "description": "Authenticated user's ID (automatically injected)"
            },
            "status": {
                "type": "string",
                "enum": ["all", "pending", "completed"],
                "description": "Filter tasks by status (default: all)"
            },
            "limit": {
                "type": "integer",
                "minimum": 1,
                "maximum": 100,
                "default": 20,
                "description": "Maximum number of tasks to return (default: 20)"
            },
            "offset": {
                "type": "integer",
                "minimum": 0,
                "default": 0,
                "description": "Offset for pagination (default: 0)"
            }
        },
        "required": ["user_id"]
    }
}

COMPLETE_TASK_SCHEMA = {
    "name": "complete_task",
    "description": "Mark a task as completed for the authenticated user",
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
    "description": "Update task properties for the authenticated user",
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
                "description": "New title for the task (optional)"
            },
            "description": {
                "type": "string",
                "description": "New description for the task (optional)"
            },
            "status": {
                "type": "string",
                "enum": ["pending", "completed"],
                "description": "New status for the task (optional)"
            }
        },
        "required": ["user_id", "task_id"]
    }
}

DELETE_TASK_SCHEMA = {
    "name": "delete_task",
    "description": "Delete a task for the authenticated user",
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


def validate_and_run_async(coro):
    """
    Helper function to run async functions with validation.
    In a real implementation, this would be handled by the MCP framework.
    """
    try:
        loop = asyncio.get_running_loop()
        # If we're already in a loop, we need to run the coroutine in the existing loop
        # We'll use asyncio.create_task to schedule the coroutine and await its result
        import asyncio
        import inspect

        # If called from sync context inside an async context, we need to await
        # However, since this is called from a FastAPI endpoint that is already async,
        # we should return the coroutine to be awaited by the caller
        return coro
    except RuntimeError:
        # No event loop running, safe to create one
        return asyncio.run(coro)


def verify_tool_authentication(params: Dict[str, Any]) -> str:
    """
    Verify that the tool has proper authentication context.

    Args:
        params: Dictionary containing tool parameters including user_id

    Returns:
        str: The validated user_id

    Raises:
        Exception: If authentication is missing or invalid
    """
    user_id = params.get("user_id")

    if not user_id:
        raise ValueError("Authentication context missing: user_id is required for all MCP tools")

    # Additional validation could happen here

    return user_id


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
        # Convert user_id to UUID
        user_uuid = UUID(user_id)
        task_uuid = UUID(task_id)

        # Create async session using the session factory approach
        from src.utils.database import get_async_session_factory
        session_factory = get_async_session_factory()

        # Create a session instance using the factory
        async with session_factory() as session:
            # Update the task with completed status
            task_update = TaskUpdate(completed=True)
            updated_task = await TaskService.update_task(
                session,
                user_uuid,
                task_uuid,
                task_update
            )

            if not updated_task:
                return {
                    "success": False,
                    "error_code": TASK_NOT_FOUND,
                    "message": ERROR_MESSAGES[TASK_NOT_FOUND]
                }

            return {
                "success": True,
                "message": f"Task '{updated_task.title}' has been marked as completed"
            }

    except ValueError:
        # UUID conversion failed
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
    except ValueError:
        # UUID conversion failed
        return {
            "success": False,
            "error_code": INVALID_INPUT,
            "message": ERROR_MESSAGES[INVALID_INPUT]
        }
    except Exception as e:
        return {
            "success": False,
            "error_code": "UNKNOWN_ERROR",
            "message": f"An unexpected error occurred: {str(e)}"
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


async def list_tasks(user_id: str, status: str = "all", limit: int = 20, offset: int = 0) -> Dict[str, Any]:
    """
    List all tasks for the authenticated user.

    Args:
        user_id: The authenticated user's ID (from JWT token)
        status: Filter by status ('all', 'pending', 'completed')
        limit: Maximum number of tasks to return
        offset: Offset for pagination

    Returns:
        Dict with success status and list of tasks
    """
    try:
        # Convert user_id to UUID
        user_uuid = UUID(user_id)

        # Create async session using the session factory approach
        from src.utils.database import get_async_session_factory
        session_factory = get_async_session_factory()

        # Create a session instance using the factory
        async with session_factory() as session:
            # Get all tasks for the user
            user_tasks = await TaskService.get_user_tasks(session, user_uuid)

            # Apply status filter if needed
            if status != "all":
                if status == "completed":
                    filtered_tasks = [task for task in user_tasks if task.completed]
                elif status == "pending":
                    filtered_tasks = [task for task in user_tasks if not task.completed]
                else:
                    # Invalid status, return error
                    return {
                        "success": False,
                        "error_code": INVALID_INPUT,
                        "message": "Invalid status parameter. Use 'all', 'pending', or 'completed'."
                    }
            else:
                filtered_tasks = user_tasks

            # Apply pagination
            paginated_tasks = filtered_tasks[offset:offset + limit]

            # Convert tasks to dictionaries
            task_list = []
            for task in paginated_tasks:
                task_dict = {
                    "id": str(task.id),
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat(),
                    "user_id": str(task.user_id)
                }
                task_list.append(task_dict)

            return {
                "success": True,
                "tasks": task_list,
                "total_count": len(filtered_tasks),
                "message": f"Retrieved {len(task_list)} tasks for user"
            }

    except ValueError:
        # UUID conversion failed
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
                     description: Optional[str] = None, due_date: Optional[str] = None,
                     status: Optional[str] = None) -> Dict[str, Any]:
    """
    Update task properties for the authenticated user.

    Args:
        user_id: The authenticated user's ID (from JWT token)
        task_id: The ID of the task to update
        title: New title for the task (optional)
        description: New description for the task (optional)
        due_date: New due date for the task (optional)
        status: New status for the task (optional)

    Returns:
        Dict with success status and updated task
    """
    try:
        # Convert user_id and task_id to UUIDs
        user_uuid = UUID(user_id)
        task_uuid = UUID(task_id)

        # Prepare update data
        update_data = {}
        if title is not None:
            update_data["title"] = title
        if description is not None:
            update_data["description"] = description
        if status is not None:
            # Map status string to boolean for completed field
            if status == "completed":
                update_data["completed"] = True
            elif status == "pending":
                update_data["completed"] = False

        # Create TaskUpdate object with the data
        task_update = TaskUpdate(**update_data)

        # Create async session using the session factory approach
        from src.utils.database import get_async_session_factory
        session_factory = get_async_session_factory()

        # Create a session instance using the factory
        async with session_factory() as session:
            # Update the task
            updated_task = await TaskService.update_task(
                session,
                user_uuid,
                task_uuid,
                task_update
            )

            if not updated_task:
                return {
                    "success": False,
                    "error_code": TASK_NOT_FOUND,
                    "message": ERROR_MESSAGES[TASK_NOT_FOUND]
                }

            return {
                "success": True,
                "message": f"Task '{updated_task.title}' has been updated"
            }

    except ValueError:
        # UUID conversion failed
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
        # Convert user_id and task_id to UUIDs
        user_uuid = UUID(user_id)
        task_uuid = UUID(task_id)

        # Create async session using the session factory approach
        from src.utils.database import get_async_session_factory
        session_factory = get_async_session_factory()

        # Create a session instance using the factory
        async with session_factory() as session:
            # Delete the task
            success = await TaskService.delete_task(
                session,
                user_uuid,
                task_uuid
            )

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
        # UUID conversion failed
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


async def complete_task_wrapper(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Wrapper function for the complete_task MCP tool that validates parameters.

    Args:
        params: Dictionary containing 'user_id' and 'task_id'

    Returns:
        Result from complete_task with proper error handling
    """
    try:
        user_id = verify_tool_authentication(params)
        task_id = params.get("task_id")

        if not task_id:
            return {
                "success": False,
                "error_code": INVALID_INPUT,
                "message": "task_id is a required parameter"
            }

        # Execute the async function and await the result
        result = await complete_task(user_id, task_id)
        return result
    except ValueError as e:  # Catch ValueError from verify_tool_authentication
        return {
            "success": False,
            "error_code": "AUTHENTICATION_ERROR",
            "message": f"Authentication error: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error_code": "AUTHENTICATION_ERROR",
            "message": f"Error executing complete_task: {str(e)}"
        }


async def add_task_wrapper(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Wrapper function for the add_task MCP tool that validates parameters.

    Args:
        params: Dictionary containing 'user_id', 'title', and optional 'description', 'due_date'

    Returns:
        Result from add_task with proper error handling
    """
    try:
        user_id = verify_tool_authentication(params)
        title = params.get("title")
        description = params.get("description", "")
        due_date = params.get("due_date")

        if not title:
            return {
                "success": False,
                "error_code": INVALID_INPUT,
                "message": "title is a required parameter"
            }

        # Execute the async function and await the result
        result = await add_task(user_id, title, description, due_date)
        return result
    except ValueError as e:  # Catch ValueError from verify_tool_authentication
        return {
            "success": False,
            "error_code": "AUTHENTICATION_ERROR",
            "message": f"Authentication error: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error_code": "AUTHENTICATION_ERROR",
            "message": f"Error executing add_task: {str(e)}"
        }


def get_add_task_schema() -> Dict[str, Any]:
    """
    Returns the JSON Schema definition for the add_task tool.

    Returns:
        Dict containing the JSON Schema for add_task
    """
    return ADD_TASK_SCHEMA


async def list_tasks_wrapper(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Wrapper function for the list_tasks MCP tool that validates parameters.

    Args:
        params: Dictionary containing 'user_id' and optional filters

    Returns:
        Result from list_tasks with proper error handling
    """
    try:
        user_id = verify_tool_authentication(params)
        status = params.get("status", "all")  # all, pending, completed
        limit = params.get("limit", 20)
        offset = params.get("offset", 0)

        # Execute the async function and await the result
        result = await list_tasks(user_id, status, limit, offset)
        return result
    except ValueError as e:  # Catch ValueError from verify_tool_authentication
        return {
            "success": False,
            "error_code": "AUTHENTICATION_ERROR",
            "message": f"Authentication error: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error_code": "AUTHENTICATION_ERROR",
            "message": f"Error executing list_tasks: {str(e)}"
        }


def get_list_tasks_schema() -> Dict[str, Any]:
    """
    Returns the JSON Schema definition for the list_tasks tool.

    Returns:
        Dict containing the JSON Schema for list_tasks
    """
    return LIST_TASKS_SCHEMA


async def update_task_wrapper(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Wrapper function for the update_task MCP tool that validates parameters.

    Args:
        params: Dictionary containing 'user_id', 'task_id', and optional update fields

    Returns:
        Result from update_task with proper error handling
    """
    try:
        user_id = verify_tool_authentication(params)
        task_id = params.get("task_id")

        # Extract optional update fields
        title = params.get("title")
        description = params.get("description")
        due_date = params.get("due_date")
        status = params.get("status")

        if not task_id:
            return {
                "success": False,
                "error_code": INVALID_INPUT,
                "message": "task_id is a required parameter"
            }

        # Execute the async function and await the result
        result = await update_task(user_id, task_id, title, description, due_date, status)
        return result
    except ValueError as e:  # Catch ValueError from verify_tool_authentication
        return {
            "success": False,
            "error_code": "AUTHENTICATION_ERROR",
            "message": f"Authentication error: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error_code": "AUTHENTICATION_ERROR",
            "message": f"Error executing update_task: {str(e)}"
        }


def get_update_task_schema() -> Dict[str, Any]:
    """
    Returns the JSON Schema definition for the update_task tool.

    Returns:
        Dict containing the JSON Schema for update_task
    """
    return UPDATE_TASK_SCHEMA


async def delete_task_wrapper(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Wrapper function for the delete_task MCP tool that validates parameters.

    Args:
        params: Dictionary containing 'user_id' and 'task_id'

    Returns:
        Result from delete_task with proper error handling
    """
    try:
        user_id = verify_tool_authentication(params)
        task_id = params.get("task_id")

        if not task_id:
            return {
                "success": False,
                "error_code": INVALID_INPUT,
                "message": "task_id is a required parameter"
            }

        # Execute the async function and await the result
        result = await delete_task(user_id, task_id)
        return result
    except ValueError as e:  # Catch ValueError from verify_tool_authentication
        return {
            "success": False,
            "error_code": "AUTHENTICATION_ERROR",
            "message": f"Authentication error: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error_code": "AUTHENTICATION_ERROR",
            "message": f"Error executing delete_task: {str(e)}"
        }


def get_delete_task_schema() -> Dict[str, Any]:
    """
    Returns the JSON Schema definition for the delete_task tool.

    Returns:
        Dict containing the JSON Schema for delete_task
    """
    return DELETE_TASK_SCHEMA


def get_complete_task_schema() -> Dict[str, Any]:
    """
    Returns the JSON Schema definition for the complete_task tool.

    Returns:
        Dict containing the JSON Schema for complete_task
    """
    return COMPLETE_TASK_SCHEMA