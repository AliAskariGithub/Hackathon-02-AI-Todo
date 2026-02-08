# Research Findings: MCP & Agent Integration

**Feature**: 006-mcp-agent-logic
**Date**: 2026-02-06

## 1. MCP SDK Integration Patterns

### Decision: MCP Server Integration Approach
**Rationale**: The Official Python MCP SDK can be integrated with FastAPI using the FastMCP class. The MCP server should be initialized as a separate component that can be attached to the FastAPI application via a custom route handler.

**Findings**:
- FastMCP("TodoServer") creates the main MCP server instance
- Tools are registered using mcp.add_tool() method
- The MCP server exposes a standard route for tool access
- FastAPI middleware can intercept requests to establish authentication context

### Implementation Pattern:
```python
from model_context_protocol import FastMCP

mcp = FastMCP("TodoServer")

# Register tools with authentication wrapper
mcp.add_tool("add_task", add_task_with_auth)
mcp.add_tool("list_tasks", list_tasks_with_auth)
# ... other tools
```

## 2. OpenAI Agent Configuration

### Decision: Agent Initialization Parameters
**Rationale**: The OpenAI Agent needs to be configured with proper instructions, tools access, and model specifications to handle task management effectively.

**Findings**:
- Agent initialization requires an OpenAI client instance
- The instructions should guide the agent on how to handle task operations safely
- The agent should have access to the MCP tools for task management
- Error handling instructions should guide the agent on how to respond to failures

### Configuration Pattern:
```python
from openai import OpenAI

client = OpenAI()

todo_agent = client.beta.agents.create(
    name="Todo Agent",
    instructions="You are a helpful task management assistant...",
    tools=[{"type": "function", "function": {"name": "add_task", ...}}, ...],
    model="gpt-4-turbo-preview"
)
```

## 3. JWT Token Processing with Better Auth

### Decision: JWT Authentication Context
**Rationale**: Better Auth generates JWT tokens that need to be decoded to extract the user_id. FastAPI middleware can intercept requests to establish user context.

**Findings**:
- Better Auth uses standard JWT format with user information in the payload
- The `better-conn` Python library provides utilities to verify Better Auth JWTs
- FastAPI dependencies can be used to extract and validate user_id from JWT
- User_id can be passed to tools via thread-local storage or function parameters

### Verification Pattern:
```python
import jwt
from better_conn import verify_jwt  # or equivalent

def verify_better_auth_token(token: str) -> str:
    """Verify JWT and extract user_id"""
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    return payload.get("userId")
```

## 4. SQLModel Integration with MCP Tools

### Decision: Database Operations Pattern
**Rationale**: Existing SQLModel patterns should be reused within MCP tools to maintain consistency and leverage existing database infrastructure.

**Findings**:
- Existing Task model and database session patterns can be reused
- Each MCP tool performs its specific database operation atomically
- Transaction management follows existing SQLModel patterns
- Error handling includes database-specific exceptions

### Integration Pattern:
```python
from sqlmodel import Session, select
from backend.models import Task

def add_task_impl(user_id: str, title: str, description: str = None) -> dict:
    with Session(engine) as session:
        task = Task(user_id=user_id, title=title, description=description)
        session.add(task)
        session.commit()
        session.refresh(task)
        return {"task_id": str(task.id), "success": True}
```

## 5. Tool Authentication Method Decision

### Decision: Explicit Parameter Approach
**Rationale**: Passing user_id as an explicit parameter to each tool provides the clearest security model and makes the authentication requirement visible in the tool signature.

**Alternatives Considered**:
- Global context variable: Less explicit, harder to trace authentication flow
- Thread-local storage: Could lead to context mixing in concurrent environments
- **Explicit parameters**: Most secure, explicit, and traceable approach

**Implementation**: Each tool receives user_id as an additional parameter that is validated during execution.

## 6. Error Mapping Strategy

### Decision: Standardized Error Codes
**Rationale**: Consistent error codes enable the agent to understand and communicate specific failure reasons to users.

**Standardized Codes**:
- `TASK_NOT_FOUND`: Task ID doesn't exist or doesn't belong to user
- `UNAUTHORIZED_ACCESS`: Attempt to access another user's resource
- `INVALID_INPUT`: Tool parameters don't match schema
- `DATABASE_ERROR`: Database operation failed
- `AUTHENTICATION_ERROR`: Invalid or missing authentication

## 7. MCP Tool JSON Schema Definitions

### Decision: Strict Schema Validation
**Rationale**: Strict JSON schemas minimize hallucinations and ensure consistent parameter handling across all tools.

**Schema Template**:
```json
{
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
      }
    },
    "required": ["user_id", "title"]
  }
}
```

## 8. Agent Instruction Optimization

### Decision: Context-Aware Instructions
**Rationale**: Agent instructions should emphasize user context, safety, and error handling to improve user experience.

**Final Instructions**:
"You are a helpful task management assistant. You can help users manage their tasks by:
- Adding new tasks
- Listing existing tasks
- Updating task details
- Marking tasks as complete
- Deleting tasks

Always confirm with the user before performing irreversible actions like deleting tasks.
If you cannot find a task that the user mentions, let them know specifically.
Be concise and clear in your responses.
Respect the user's context - you can only help with their own tasks."

## Summary of Resolved Unknowns

All initial unknowns have been researched and resolved:

- ✅ MCP SDK Integration: FastMCP with tool registration and route handling
- ✅ OpenAI Agent Configuration: Standard Agent creation with instructions and tools
- ✅ JWT Processing: JWT decoding with user_id extraction from Better Auth tokens
- ✅ SQLModel Integration: Reuse of existing database patterns within tools
- ✅ Authentication Context: Explicit parameter passing for security