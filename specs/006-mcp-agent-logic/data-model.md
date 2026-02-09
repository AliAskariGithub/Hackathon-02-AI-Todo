# Data Model: MCP & Agent Logic

**Feature**: 006-mcp-agent-logic
**Date**: 2026-02-06

## Entities

### Task
**Current Model** (from existing application):
- `id` (UUID/int, primary key): Unique identifier for the task
- `title` (string): Task title/description
- `description` (string, nullable): Detailed task description
- `completed` (boolean): Completion status
- `created_at` (datetime): Timestamp of creation
- `updated_at` (datetime): Timestamp of last update
- `user_id` (string/UUID): Foreign key linking to user who owns the task

**Relevant Properties for MCP Integration**:
- The `user_id` field is critical for authentication context enforcement
- The `title` field is important for natural language matching (e.g., "milk task")
- The `completed` field is essential for complete_task operations

### User Context
**MCP Tool Context Entity**:
- `user_id` (string): Verified user identifier from JWT
- `authentication_status` (enum): Valid/Invalid/Expired token status
- `session_id` (string, optional): Associated session identifier

**Purpose**: Ensures all MCP tool operations are executed within proper user context

### Task Operation Request
**MCP Tool Call Entity**:
- `tool_name` (string): Name of the MCP tool being invoked
- `parameters` (dict): Input parameters for the tool call
- `user_context` (dict): Authentication context with user_id
- `timestamp` (datetime): When the operation was initiated
- `result` (dict): Output from the tool execution
- `error_code` (string, nullable): Error code if operation failed

**Purpose**: Tracks tool invocations and maintains audit trail of operations

## Relationships

### Task to User Context
- **Relationship**: Many-to-One (Many tasks to One user)
- **Constraint**: All task operations must be associated with a verified user_id
- **Validation**: MCP tools must validate that user_id matches the authenticated session

### Task Operation Request to User Context
- **Relationship**: One-to-One (Each request has one user context)
- **Constraint**: The user_context must be validated before tool execution
- **Validation**: Authentication must be verified before processing any tool request

## State Transitions

### Task State Changes
1. **Creation**: New task with `completed = false`
2. **Update**: Task properties modified (title, description, etc.)
3. **Completion**: `completed = true` when complete_task tool is called
4. **Deletion**: Task record removed when delete_task tool is called

### Authentication State
1. **Unauthenticated**: No JWT token provided
2. **Validating**: JWT token being processed
3. **Authenticated**: Valid user_id extracted and verified
4. **Failed**: Invalid/expired token detected

## Validation Rules

### Task Entity
- `title` must be non-empty string (1-255 characters)
- `user_id` must match authenticated user context
- `completed` can only be changed via complete_task tool
- `user_id` is immutable after creation

### MCP Tool Parameters
- All required parameters must be present in tool call
- Parameters must conform to strict JSON Schema
- User_id must match the authenticated session
- Task identifiers must exist and belong to the user

## Constraints

### Security Constraints
- No cross-user data access allowed through MCP tools
- All operations must be validated against user context
- Failed authentication results in immediate termination

### Data Integrity Constraints
- Atomic operations within each MCP tool
- Consistent timestamp updates on all modifications
- Referential integrity maintained with user records

### Business Logic Constraints
- Users can only modify their own tasks
- Completed tasks can be uncompleted via update_task
- Task deletion is permanent