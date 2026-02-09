# Model Context Protocol (MCP) for Todo Application

This directory contains the MCP (Model Context Protocol) integration for the Todo application, enabling AI agents to interact with task management functionality.

## Overview

The MCP integration provides 5 core tools for AI agents to manage user tasks:
- `add_task`: Add new tasks
- `list_tasks`: Retrieve user's tasks
- `complete_task`: Mark tasks as completed
- `update_task`: Modify task properties
- `delete_task`: Remove tasks

## Architecture

```
MCP Server → Tools → Database Operations
     ↓
AI Agent Integration → User Authentication → Security Layer
     ↓
API Endpoints → FastAPI Integration
```

## Endpoints

### `/api/mcp/execute-tool`
Execute MCP tools with proper authentication context.

**Request Body:**
```json
{
  "tool_name": "complete_task",
  "params": {
    "task_id": "uuid-string"
  }
}
```

### `/api/mcp/chat-with-agent`
Interact with the AI task management agent.

**Request Body:**
```json
{
  "query": "I finished the milk task"
}
```

### `/api/mcp/available-tools`
Get a list of available MCP tools.

## Security Model

All MCP tools enforce user isolation by:
1. Extracting `user_id` from JWT tokens
2. Validating that all operations are performed for the authenticated user
3. Preventing cross-user data access

## Environment Variables

- `OPENAI_API_KEY`: API key for OpenAI integration

## Usage Examples

### Direct Tool Execution
```python
# Execute add_task
{
  "tool_name": "add_task",
  "params": {
    "title": "Buy groceries",
    "description": "Milk, bread, eggs"
  }
}
```

### AI Agent Interaction
```python
# Natural language query
{
  "query": "List all my tasks"
}
```

## Error Handling

Standardized error codes:
- `TASK_NOT_FOUND`: Task doesn't exist or doesn't belong to user
- `UNAUTHORIZED_ACCESS`: Attempt to access another user's resource
- `INVALID_INPUT`: Tool parameters don't match schema
- `DATABASE_ERROR`: Database operation failed
- `AUTHENTICATION_ERROR`: Invalid or missing authentication