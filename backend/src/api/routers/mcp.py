"""
MCP (Model Context Protocol) Router for the Todo Application.
Provides endpoints for MCP tools to be used by AI agents.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import Dict, Any, List
from uuid import UUID
import json

from ...mcp.middleware.auth_middleware import verify_authorized_user
from ...mcp.mcp_server import get_mcp_server

router = APIRouter(prefix="/api/mcp", tags=["mcp"])

# Get the initialized MCP server
mcp_server = get_mcp_server()


@router.post("/execute-tool")
async def execute_mcp_tool(
    request: Request,
    current_user_id: str = Depends(verify_authorized_user)
):
    """
    Execute an MCP tool with proper user authentication context.

    Args:
        request: The incoming request containing tool name and parameters
        current_user_id: The authenticated user ID from the JWT token

    Returns:
        The result of the executed tool
    """
    try:
        # Parse the request body
        body = await request.json()

        tool_name = body.get("tool_name")
        tool_params = body.get("params", {})

        if not tool_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="tool_name is required"
            )

        # Inject the user_id into the tool parameters
        tool_params["user_id"] = current_user_id

        # Execute the appropriate tool using the MCP server
        mcp_instance = get_mcp_server()
        result = await mcp_instance.execute_tool(tool_name, tool_params)

        return result

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error executing MCP tool: {str(e)}\n{error_details}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing MCP tool: {str(e)}"
        )


@router.get("/available-tools")
async def get_available_tools(
    current_user_id: str = Depends(verify_authorized_user)
):
    """
    Get a list of available MCP tools.

    Args:
        current_user_id: The authenticated user ID (for authorization check)

    Returns:
        A list of available tools with their descriptions
    """
    available_tools = [
        {
            "name": "add_task",
            "description": "Add a new task for the authenticated user"
        },
        {
            "name": "list_tasks",
            "description": "List all tasks for the authenticated user"
        },
        {
            "name": "complete_task",
            "description": "Mark a task as completed for the authenticated user"
        },
        {
            "name": "update_task",
            "description": "Update task properties for the authenticated user"
        },
        {
            "name": "delete_task",
            "description": "Delete a task for the authenticated user"
        }
    ]

    return {"tools": available_tools}


@router.post("/chat-with-agent")
async def chat_with_agent(
    request: Request,
    current_user_id: str = Depends(verify_authorized_user)
):
    """
    Endpoint to interact with the AI task management agent.

    Args:
        request: The incoming request containing the user query
        current_user_id: The authenticated user ID from the JWT token

    Returns:
        The response from the AI agent
    """
    try:
        # Parse the request body
        body = await request.json()

        user_query = body.get("query")
        if not user_query:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="query is required"
            )

        # Import the task runner
        from ...mcp.runners.task_runner import run_task_agent

        # Run the agent with the user's query and authenticated user context
        result = await run_task_agent(user_query, current_user_id)

        return result

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing agent request: {str(e)}"
        )