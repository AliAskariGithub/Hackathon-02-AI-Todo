# MCP Tool Function Signatures

**Feature**: AI Chatbot & Persistence | **Branch**: `001-ai-chatbot-persistence` | **Date**: 2026-02-07

## Overview

This document defines the MCP (Model Context Protocol) tool functions that the AI assistant can invoke to perform task management operations. These tools are exposed by the backend MCP server and are automatically registered with the OpenAI Agents SDK.

**Key Principles**:
- All tools receive `user_id` as the first parameter (hard-coded by backend, not provided by AI)
- All tools return structured JSON for reliable parsing
- Tool docstrings must clearly explain when and how to use each tool
- Tools enforce user data isolation at the implementation level

---

## Tool Functions

### list_tasks

**Purpose**: Retrieve all tasks for the authenticated user

**Function Signature**:
```python
def list_tasks(user_id: str) -> List[Dict[str, Any]]:
    """
    Get all tasks for the current user.

    Use this when the user asks to:
    - See their tasks
    - Show their todo list
    - List what they need to do
    - Check what's on their plate
    - Review their tasks

    Returns a list of tasks with id, description, is_completed, and created_at fields.
    Each task object includes all information needed to reference or modify the task.

    Args:
        user_id: UUID of the authenticated user (automatically provided by backend)

    Returns:
        List of task objects in JSON format

    Example return value:
    [
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "description": "Buy milk",
            "is_completed": false,
            "created_at": "2026-02-07T10:00:00Z",
            "updated_at": "2026-02-07T10:00:00Z"
        },
        {
            "id": "550e8400-e29b-41d4-a716-446655440001",
            "description": "Call dentist",
            "is_completed": true,
            "created_at": "2026-02-06T14:30:00Z",
            "updated_at": "2026-02-07T09:15:00Z"
        }
    ]
    """
```

**Implementation Notes**:
- Query database filtered by `user_id`
- Order by `created_at` descending (newest first)
- Return empty array if user has no tasks
- Never return tasks from other users

**Error Handling**:
- Database connection error: Return `{"error": "database_error", "message": "Unable to retrieve tasks"}`
- Invalid user_id: Return `{"error": "invalid_user", "message": "User not found"}`

---

### create_task

**Purpose**: Create a new task for the authenticated user

**Function Signature**:
```python
def create_task(user_id: str, description: str) -> Dict[str, Any]:
    """
    Create a new task for the current user.

    Use this when the user asks to:
    - Add a task
    - Create a todo
    - Remember something
    - Add to their list
    - Make a note to do something

    Requires a description of what needs to be done. The description should be
    clear and actionable. Extract the core task from the user's message.

    Args:
        user_id: UUID of the authenticated user (automatically provided by backend)
        description: What needs to be done (max 500 characters)

    Returns:
        The created task object in JSON format

    Example return value:
    {
        "id": "550e8400-e29b-41d4-a716-446655440002",
        "description": "Buy milk",
        "is_completed": false,
        "created_at": "2026-02-07T10:30:00Z",
        "updated_at": "2026-02-07T10:30:00Z"
    }
    """
```

**Implementation Notes**:
- Validate description is not empty and <= 500 characters
- Set `is_completed` to `false` by default
- Set `created_at` and `updated_at` to current timestamp
- Associate task with `user_id`

**Error Handling**:
- Empty description: Return `{"error": "validation_error", "message": "Task description cannot be empty"}`
- Description too long: Return `{"error": "validation_error", "message": "Task description exceeds 500 characters"}`
- Database error: Return `{"error": "database_error", "message": "Unable to create task"}`

---

### update_task

**Purpose**: Update an existing task's description or completion status

**Function Signature**:
```python
def update_task(
    user_id: str,
    task_id: str,
    description: Optional[str] = None,
    is_completed: Optional[bool] = None
) -> Dict[str, Any]:
    """
    Update a task's description or completion status.

    Use this when the user asks to:
    - Change a task
    - Edit a todo
    - Mark something as done/undone
    - Complete a task
    - Update task details
    - Modify a task

    IMPORTANT: Always call list_tasks first to get the correct task_id before
    using this function. Never guess or make up task IDs. If you're not sure
    which task the user is referring to, ask them to clarify or show them the
    list of tasks.

    At least one of description or is_completed must be provided.

    Args:
        user_id: UUID of the authenticated user (automatically provided by backend)
        task_id: UUID of the task to update (get from list_tasks)
        description: New description for the task (optional)
        is_completed: New completion status (optional)

    Returns:
        The updated task object in JSON format

    Example return value:
    {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "description": "Buy milk and eggs",
        "is_completed": true,
        "created_at": "2026-02-07T10:00:00Z",
        "updated_at": "2026-02-07T11:00:00Z"
    }
    """
```

**Implementation Notes**:
- Verify task exists and belongs to `user_id`
- Update only provided fields (description and/or is_completed)
- Update `updated_at` timestamp
- Return 404 if task not found or belongs to different user

**Error Handling**:
- Task not found: Return `{"error": "not_found", "message": "Task not found or you don't have permission to update it"}`
- No fields provided: Return `{"error": "validation_error", "message": "At least one field (description or is_completed) must be provided"}`
- Invalid task_id format: Return `{"error": "validation_error", "message": "Invalid task ID format"}`
- Description too long: Return `{"error": "validation_error", "message": "Task description exceeds 500 characters"}`

---

### delete_task

**Purpose**: Permanently delete a task

**Function Signature**:
```python
def delete_task(user_id: str, task_id: str) -> Dict[str, Any]:
    """
    Delete a task permanently.

    Use this when the user explicitly asks to:
    - Delete a task
    - Remove a task
    - Get rid of a task
    - Erase a todo

    IMPORTANT: Always call list_tasks first to get the correct task_id before
    using this function. Never guess or make up task IDs. If you're not sure
    which task the user is referring to, ask them to clarify or show them the
    list of tasks.

    This operation cannot be undone. Consider asking for confirmation before
    deleting, especially if the task description is ambiguous.

    Args:
        user_id: UUID of the authenticated user (automatically provided by backend)
        task_id: UUID of the task to delete (get from list_tasks)

    Returns:
        Confirmation of deletion in JSON format

    Example return value:
    {
        "success": true,
        "message": "Task deleted successfully",
        "deleted_task_id": "550e8400-e29b-41d4-a716-446655440000"
    }
    """
```

**Implementation Notes**:
- Verify task exists and belongs to `user_id`
- Permanently delete from database
- Return success confirmation with deleted task ID

**Error Handling**:
- Task not found: Return `{"error": "not_found", "message": "Task not found or you don't have permission to delete it"}`
- Invalid task_id format: Return `{"error": "validation_error", "message": "Invalid task ID format"}`
- Database error: Return `{"error": "database_error", "message": "Unable to delete task"}`

---

## Tool Registration

**Backend Implementation Location**: `backend/src/mcp/tools/task_tools.py`

**Registration Process**:
1. Tools are defined as Python functions with proper type hints
2. Docstrings are parsed to generate tool descriptions for the AI
3. Tools are registered with the MCP server on startup
4. OpenAI Agents SDK automatically discovers and uses registered tools

**Example Registration Code**:
```python
from mcp.server import MCPServer

server = MCPServer()

@server.tool()
def list_tasks(user_id: str) -> List[Dict[str, Any]]:
    # Implementation here
    pass

@server.tool()
def create_task(user_id: str, description: str) -> Dict[str, Any]:
    # Implementation here
    pass

# ... register other tools
```

---

## Security Considerations

**User ID Injection**:
- The `user_id` parameter is NEVER provided by the AI
- Backend extracts `user_id` from JWT token
- Backend hard-codes `user_id` into all tool calls
- This prevents the AI from accessing other users' data

**Data Isolation**:
- All database queries MUST filter by `user_id`
- Tools MUST verify task ownership before update/delete operations
- Return 404 for tasks that don't exist OR belong to different user (don't leak existence)

**Input Validation**:
- Validate all string inputs for length and content
- Sanitize inputs to prevent SQL injection (use parameterized queries)
- Validate UUID formats for task_id parameters

---

## Testing Requirements

**Unit Tests** (`backend/tests/test_task_tools.py`):
- Test each tool with valid inputs
- Test error handling for invalid inputs
- Test user isolation (User A cannot access User B's tasks)
- Test edge cases (empty lists, long descriptions, invalid UUIDs)

**Integration Tests** (`backend/tests/test_agent_logic.py`):
- Test AI tool selection (does AI choose correct tool for user intent?)
- Test AI parameter extraction (does AI extract correct description from message?)
- Test AI error handling (does AI handle tool errors gracefully?)
- Test AI workflow (does AI call list_tasks before update/delete?)

**Example Test Cases**:
```python
def test_list_tasks_returns_only_user_tasks():
    # Create tasks for User A and User B
    # Call list_tasks with User A's ID
    # Verify only User A's tasks are returned

def test_create_task_validates_description_length():
    # Attempt to create task with 501 character description
    # Verify validation error is returned

def test_update_task_requires_list_tasks_first():
    # Send message "complete the milk task"
    # Verify AI calls list_tasks before update_task
    # Verify correct task_id is used

def test_delete_task_prevents_cross_user_access():
    # User A creates a task
    # User B attempts to delete User A's task
    # Verify 404 error (not 403, to avoid leaking existence)
```

---

## AI Behavior Guidelines

**Tool Selection**:
- The AI should select tools based on user intent, not exact keywords
- "I need to buy milk" → create_task
- "What do I have to do?" → list_tasks
- "I finished the milk task" → list_tasks + update_task

**Parameter Extraction**:
- Extract clean, actionable descriptions from user messages
- "I need to remember to buy milk tomorrow" → description: "Buy milk tomorrow"
- "Can you add a task for calling the dentist?" → description: "Call dentist"

**Error Recovery**:
- If a tool returns an error, explain the error to the user in natural language
- Suggest corrective actions when appropriate
- Never expose raw error messages or stack traces to users

**Confirmation Requests**:
- For destructive operations (delete), consider asking for confirmation
- "Are you sure you want to delete the 'Buy milk' task?"
- Wait for user confirmation before proceeding

---

## Future Enhancements

**Potential Additional Tools**:
- `search_tasks(query: str)` - Search tasks by keyword
- `filter_tasks(is_completed: bool)` - Filter by completion status
- `bulk_complete_tasks(task_ids: List[str])` - Complete multiple tasks at once
- `reorder_tasks(task_ids: List[str])` - Change task order/priority

**Note**: These are out of scope for the initial implementation but may be added in future iterations based on user feedback.
