# Implementation Plan: MCP & Agent Logic

**Feature**: 006-mcp-agent-logic
**Created**: 2026-02-06
**Status**: Draft
**Author**: Claude

## Technical Context

### Current State
The system currently has a full-stack todo application with user authentication, task management, and testimonial systems. The backend is built with FastAPI and SQLModel, with Better Auth for authentication and Neon for PostgreSQL hosting.

### Target State
- MCP server with 5 tools registered: `add_task`, `list_tasks`, `complete_task`, `delete_task`, `update_task`
- OpenAI Agent integrated with proper instructions for task management
- Secure context ensuring all tool calls use the authenticated user's ID
- Runner utility function for processing user queries with proper authentication context

### Unknowns/Dependencies

- **MCP SDK Integration**: [NEEDS CLARIFICATION] How exactly to integrate the Official Python MCP SDK with FastAPI
- **OpenAI Agent Configuration**: [NEEDS CLARIFICATION] Specific configuration parameters for the Agent initialization
- **User Context Injection**: [NEEDS CLARIFICATION] Mechanism to inject user_id into MCP tools consistently
- **JWT Token Processing**: [NEEDS CLARIFICATION] How to extract user_id from Better Auth JWT tokens in the backend
- **SQLModel Integration**: [NEEDS CLARIFICATION] How MCP tools will interact with existing SQLModel database operations

### Architecture Decision Points

- **Tool Authentication Method**: Whether to pass `user_id` as a hidden tool argument vs. a global context variable
- **Error Mapping Strategy**: Standardizing MCP error codes so the Agent can explain why operations fail
- **MCP Server Location**: Where to initialize and register the MCP server within the FastAPI application

## Constitution Check

Based on the project constitution, this implementation must:
- ✅ Follow the **Secure by Default** principle by ensuring user data isolation via proper authentication context
- ✅ Maintain **Tech Stack Compliance** by using the specified stack (FastAPI, SQLModel, Better Auth, Neon)
- ✅ Implement **Auth Protocol** with JWT-based verification and user ID validation
- ✅ Ensure **Security Enforcement** with 401 Unauthorized responses for invalid requests
- ✅ Adhere to **Data Integrity Requirements** through SQLModel transaction management

## Gates

### Gate 1: Architectural Feasibility
- [ ] Verify MCP SDK compatibility with current FastAPI version
- [ ] Confirm SQLModel integration with MCP tools for database operations
- [ ] Ensure JWT token extraction works with Better Auth format

### Gate 2: Security Validation
- [ ] Validate that all MCP tools enforce user_id scoping
- [ ] Confirm authentication context is preserved across tool calls
- [ ] Verify no cross-user data access is possible through MCP tools

### Gate 3: Testing Readiness
- [ ] Establish MCP Inspector testing procedures
- [ ] Define mock LLM testing approach
- [ ] Plan for tool-specific unit tests

## Phase 0: Research & Resolution of Unknowns

### Research Task 0.1: MCP SDK Integration Patterns
**Objective**: Research how to properly integrate the Official Python MCP SDK with FastAPI application

**Approach**:
- Investigate FastMCP initialization patterns
- Understand how to register tools with JSON Schema validation
- Study existing examples of MCP SDK integration with FastAPI

**Expected Outcome**: Clear understanding of MCP server initialization and tool registration process

### Research Task 0.2: OpenAI Agent Configuration
**Objective**: Determine the correct configuration for the todo_agent with proper task management instructions

**Approach**:
- Research OpenAI Agents SDK documentation
- Understand Agent initialization parameters
- Define appropriate system instructions for task management
- Plan for error handling instructions

**Expected Outcome**: Agent configuration that properly handles task operations with clear instructions

### Research Task 0.3: JWT Token Processing with Better Auth
**Objective**: Understand how to extract user_id from Better Auth JWT tokens in FastAPI backend

**Approach**:
- Examine Better Auth JWT structure
- Research token validation methods in FastAPI
- Understand how to decode and verify JWT tokens
- Plan for secure context establishment

**Expected Outcome**: Reliable method to extract and validate user_id from JWT tokens

### Research Task 0.4: SQLModel Integration with MCP Tools
**Objective**: Determine how MCP tools will interact with existing SQLModel database operations

**Approach**:
- Study existing SQLModel models and operations
- Research MCP tool patterns for database interactions
- Plan for atomic operations within tools
- Ensure transaction consistency

**Expected Outcome**: Clear pattern for using SQLModel within MCP tools

## Phase 1: Design & Architecture

### 1.1 Data Model Updates
**Objective**: Extend the current data model to support MCP-driven operations

**Tasks**:
- Define any additional fields needed for agent-driven operations
- Ensure existing Task model supports all required operations (add, list, update, complete, delete)
- Review relationships and constraints for MCP tool compatibility

**Deliverables**: Updated data-model.md with any necessary changes

### 1.2 API Contract Design
**Objective**: Define the MCP tool interfaces with strict JSON Schema definitions

**Tool Specifications**:

#### `add_task`
- **Description**: Add a new task for the authenticated user
- **Parameters**:
  - `title` (string, required): Task title
  - `description` (string, optional): Task description
  - `due_date` (string, optional): Due date in ISO format
- **Returns**: Object with `task_id` and `success` status
- **Security**: Enforces user_id context

#### `list_tasks`
- **Description**: List all tasks for the authenticated user
- **Parameters**:
  - `status` (string, optional): Filter by task status ('all', 'pending', 'completed')
  - `limit` (integer, optional): Maximum number of tasks to return
  - `offset` (integer, optional): Offset for pagination
- **Returns**: Array of task objects
- **Security**: Only returns tasks for authenticated user

#### `complete_task`
- **Description**: Mark a task as completed for the authenticated user
- **Parameters**:
  - `task_id` (string, required): ID of the task to complete
- **Returns**: Object with `success` status and completion details
- **Security**: Verifies task belongs to authenticated user

#### `delete_task`
- **Description**: Delete a task for the authenticated user
- **Parameters**:
  - `task_id` (string, required): ID of the task to delete
- **Returns**: Object with `success` status
- **Security**: Verifies task belongs to authenticated user

#### `update_task`
- **Description**: Update task properties for the authenticated user
- **Parameters**:
  - `task_id` (string, required): ID of the task to update
  - `title` (string, optional): New task title
  - `description` (string, optional): New task description
  - `due_date` (string, optional): New due date in ISO format
  - `status` (string, optional): New status ('pending', 'completed')
- **Returns**: Object with `success` status and updated task
- **Security**: Verifies task belongs to authenticated user

### 1.3 Error Handling Strategy
**Objective**: Design standardized error codes for consistent error mapping

**Error Categories**:
- `TASK_NOT_FOUND`: When a requested task doesn't exist
- `UNAUTHORIZED_ACCESS`: When a user attempts to access another user's task
- `INVALID_INPUT`: When tool parameters don't match schema
- `DATABASE_ERROR`: When database operations fail
- `AUTHENTICATION_ERROR`: When JWT token is invalid

### 1.4 Security Context Implementation
**Objective**: Implement secure context for enforcing user_id binding

**Options Considered**:
1. **Hidden Parameter Approach**: Pass user_id as an implicit parameter to each tool
2. **Global Context Variable**: Maintain user context in a thread-safe manner
3. **Tool Wrapper Approach**: Wrap each tool with authentication context

**Decision**: Hidden Parameter Approach
**Rationale**: Most explicit and secure approach that ensures each tool operation is tied to a verified user context. Makes security requirements visible in tool signatures.

### 1.5 Agent Configuration Design
**Objective**: Define the todo_agent configuration with proper system instructions

**System Instructions**:
```
You are a helpful task management assistant. You can help users manage their tasks by:
- Adding new tasks
- Listing existing tasks
- Updating task details
- Marking tasks as complete
- Deleting tasks

Always confirm with the user before performing irreversible actions like deleting tasks.
If you cannot find a task that the user mentions, let them know specifically.
Be concise and clear in your responses.
```

### 1.6 Runner Logic Design
**Utility Function**: `run_task_agent(user_query, user_id)`
- Takes user's natural language query and authenticated user_id
- Initializes OpenAI Runner with access to MCP tools
- Processes query and executes appropriate tools
- Returns structured response to user
- Handles authentication context throughout

## Phase 2: Implementation Approach

### 2.1 Development Sequence
1. **Setup MCP Infrastructure**: Initialize MCP server and basic tool registration
2. **Implement Database Operations**: Create SQLModel-based functions for each tool
3. **Integrate Authentication Context**: Ensure user_id enforcement in all tools
4. **Configure OpenAI Agent**: Set up agent with proper instructions
5. **Build Runner Utility**: Create the main execution function
6. **Testing & Validation**: Test each tool and the overall flow

### 2.2 File Structure Plan
- `backend/mcp_server.py`: Main MCP server initialization
- `backend/tools/task_tools.py`: Individual tool implementations
- `backend/agents/todo_agent.py`: Agent configuration and instructions
- `backend/runners/task_runner.py`: Runner utility functions
- `backend/middleware/auth_middleware.py`: JWT processing utilities

## Phase 3: Testing Strategy

### 3.1 Unit Testing
- Individual tool validation using MCP Inspector
- Database operation verification
- Authentication context enforcement tests
- Error handling validation

### 3.2 Integration Testing
- End-to-end query processing
- Natural language to tool selection verification
- Cross-user data isolation validation

### 3.3 Manual Testing
- MCP Inspector manual triggers for each tool
- Natural language test cases (e.g., "I finished the milk task")
- Mock LLM validation of correct function calls

## Revisited Constitution Check (Post-Design)

- ✅ **Secure by Default**: All tools enforce user_id context with explicit parameter passing
- ✅ **Tech Stack Compliance**: Using FastAPI, SQLModel, Better Auth as specified
- ✅ **Auth Protocol**: Proper JWT token processing and user ID validation
- ✅ **Security Enforcement**: 401 responses for invalid authentication, tool-level access control
- ✅ **Data Integrity Requirements**: SQLModel-based atomic operations in each tool
- ✅ **Agentic Autonomy**: Following Claude Code/SKP workflow for all implementation