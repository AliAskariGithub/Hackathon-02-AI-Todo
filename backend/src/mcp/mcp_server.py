"""
MCP Server for the Todo Application
Initializes the Model Context Protocol server with all task management tools.
"""
import asyncio
from typing import Dict, Any, Callable

# Simplified MCP-like server implementation that handles async functions
class MCPServer:
    def __init__(self, name):
        self.name = name
        self.tools = {}

    def add_tool(self, name: str, func: Callable, schema=None):
        """
        Add a tool to the MCP server.

        Args:
            name: Name of the tool
            func: Function to execute when tool is called (can be async)
            schema: JSON Schema definition for the tool
        """
        self.tools[name] = {'function': func, 'schema': schema}

    async def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a specific tool with the given parameters.

        Args:
            tool_name: Name of the tool to execute
            params: Parameters to pass to the tool

        Returns:
            Result from the tool execution
        """
        if tool_name not in self.tools:
            return {
                "success": False,
                "error_code": "TOOL_NOT_FOUND",
                "message": f"Tool '{tool_name}' not found"
            }

        tool_func = self.tools[tool_name]['function']

        # Execute the function (it might be async)
        try:
            if asyncio.iscoroutinefunction(tool_func):
                result = await tool_func(params)
            else:
                result = tool_func(params)
            return result
        except Exception as e:
            return {
                "success": False,
                "error_code": "EXECUTION_ERROR",
                "message": f"Error executing tool '{tool_name}': {str(e)}"
            }

FastMCP = MCPServer  # Map to the simplified implementation

# Import the tool functions after class definition to avoid circular imports
from src.mcp.tools.task_tools import (
    add_task_wrapper,
    get_add_task_schema,
    list_tasks_wrapper,
    get_list_tasks_schema,
    complete_task_wrapper,
    get_complete_task_schema,
    update_task_wrapper,
    get_update_task_schema,
    delete_task_wrapper,
    get_delete_task_schema
)

# Initialize the MCP server
mcp = FastMCP("TodoServer")

# Register all task management tools with their schemas
mcp.add_tool("add_task", add_task_wrapper, get_add_task_schema())
mcp.add_tool("list_tasks", list_tasks_wrapper, get_list_tasks_schema())
mcp.add_tool("complete_task", complete_task_wrapper, get_complete_task_schema())
mcp.add_tool("update_task", update_task_wrapper, get_update_task_schema())
mcp.add_tool("delete_task", delete_task_wrapper, get_delete_task_schema())

def get_mcp_server():
    """
    Returns the initialized MCP server instance.

    Returns:
        FastMCP: The initialized MCP server with all task tools registered
    """
    return mcp