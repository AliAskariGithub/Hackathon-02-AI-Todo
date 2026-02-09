# Quickstart Guide: MCP & Agent Integration

**Feature**: 006-mcp-agent-logic
**Date**: 2026-02-06

## Overview

This guide provides the essential information needed to start working with the MCP (Model Context Protocol) server and AI agent integration in the Todo application.

## Prerequisites

- Python 3.11+
- FastAPI backend running
- Better Auth authentication configured
- SQLModel database connection established
- OpenAI API key configured
- MCP SDK installed

## Architecture Components

### MCP Server (`mcp_server.py`)
The central hub that registers and manages all task-related tools. Initialize with:

```python
from model_context_protocol import FastMCP

mcp = FastMCP("TodoServer")
```

### Task Tools (`tools/task_tools.py`)
Contains the five core tools: `add_task`, `list_tasks`, `complete_task`, `delete_task`, and `update_task`. Each tool:
- Validates the user context against the authenticated user_id
- Performs atomic database operations using SQLModel
- Returns structured responses with success/error indicators

### AI Agent (`agents/todo_agent.py`)
The OpenAI Agent configured with:
- Task management instructions
- Access to MCP tools
- Error handling guidance

### Runner Utility (`runners/task_runner.py`)
The `run_task_agent(user_query, user_id)` function that:
- Processes user's natural language query
- Establishes authentication context
- Invokes the AI agent with proper tools access
- Returns structured response

## Running the System

### 1. Start the Backend Services
```bash
# Ensure database is running
# Start the FastAPI backend
uvicorn main:app --reload
```

### 2. Initialize the MCP Server
The MCP server integrates with the FastAPI application and makes tools available to the AI agent.

### 3. Test Individual Tools
Use the MCP Inspector to manually test each tool:
- Connect to the MCP server endpoint
- Test each tool individually with sample parameters
- Verify authentication context enforcement

### 4. Run Agent Queries
Call the runner function with user queries:
```python
response = run_task_agent("I finished the milk task", user_id="abc123")
```

## Key Patterns

### Secure Context Implementation
All tools receive the user_id as a parameter to enforce user isolation:

```python
def list_tasks(user_id: str, status: str = "all") -> dict:
    # Verify user_id matches authenticated session
    # Query database for tasks belonging to user_id only
    # Return results
```

### Error Handling Strategy
Standardized error codes help the agent understand specific failure reasons:

```python
# TASK_NOT_FOUND, UNAUTHORIZED_ACCESS, INVALID_INPUT, DATABASE_ERROR, AUTHENTICATION_ERROR
if not task or task.user_id != user_id:
    return {"success": False, "error_code": "TASK_NOT_FOUND"}
```

## Testing

### MCP Inspector Testing
- Manually trigger `list_tasks` to verify Neon DB connectivity
- Test each tool with valid and invalid parameters
- Verify user isolation between different user contexts

### Natural Language Testing
- Test queries like "I finished the milk task" to verify proper tool selection
- Test error conditions to ensure graceful handling
- Mock the LLM to verify correct function selection

## Troubleshooting

### Authentication Issues
- Ensure JWT token is properly formatted and contains valid user_id
- Verify BETTER_AUTH_SECRET is correctly configured
- Check that authentication middleware is properly intercepting requests

### Tool Registration Issues
- Verify all tools are properly registered with the MCP server
- Check JSON Schema definitions match expected parameters
- Confirm database connections are working

### Agent Selection Issues
- Verify agent has access to all required tools
- Check that system instructions guide proper tool selection
- Confirm user context is properly passed to tools