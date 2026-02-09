# Feature Specification: MCP & Agent Logic

**Feature Branch**: `006-mcp-agent-logic`
**Created**: 2026-02-06
**Status**: Draft
**Input**: User description: "Todo Full-Stack Web Application - Spec 6: MCP & Agent Logic

Target functionality:
- **Official MCP Server:** Build a stateless MCP server (using the Official Python MCP SDK) that exposes 5 tools: `add_task`, `list_tasks`, `complete_task`, `delete_task`, and `update_task`.
- **AI Agent Orchestration:** Integrate the OpenAI Agents SDK into the FastAPI backend.
- **Tool-User Binding:** Implement a "Secure Context" where every MCP tool call is forced to use the `user_id` extracted from the verified Better Auth JWT.

Focus:
- **Tool Precision:** Strict JSON Schema definitions for tools to minimize LLM "hallucinations."
- **Stateless Tooling:** Tools must perform atomic DB operations (via SQLModel) and return immediate success/fail results.
- **Agent Behavior:** System prompt configuration to ensure the agent always confirms actions and handles "task not found" errors gracefully.

Success criteria:
- All 5 MCP tools pass individual unit tests using the MCP Inspector.
- The OpenAI Agent correctly selects the `complete_task` tool when prompted with "I finished the milk task."
- API returns a 401 if a chat request is made without a valid JWT.

Constraints:
- **Stack:** Official MCP SDK (Python), OpenAI Agents SDK, SQLModel.
- **Logic:** The agent must not "guess" a user_id; it must be injected from the backend session.

Not building:
- The ChatKit UI components (handled in Spec 7).
- Persistent conversation history (handled in Spec 7)."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - AI Task Management Assistant (Priority: P1)

A user interacts with an AI assistant that can manage their tasks through natural language commands. The user says "I finished the milk task" and the AI agent automatically identifies the correct task and marks it as complete using their authenticated session.

**Why this priority**: This core functionality provides immediate value by allowing users to manage tasks through intuitive conversation rather than manual interface interaction.

**Independent Test**: Can be fully tested by authenticating as a user, creating a task called "milk", prompting the AI with "I finished the milk task", and verifying the task is marked complete with proper authentication.

**Acceptance Scenarios**:

1. **Given** a user is logged in and has a task named "buy milk", **When** they tell the AI "I finished the milk task", **Then** the AI agent correctly selects the `complete_task` tool and marks the task as completed for that specific user
2. **Given** a user is logged in and has no matching tasks, **When** they tell the AI "I finished the milk task", **Then** the AI gracefully handles the "task not found" error and provides appropriate feedback

---

### User Story 2 - MCP Tools Access for AI Agent (Priority: P2)

An AI agent integrated with the system can securely perform all basic task operations (add, list, update, delete) using MCP tools, with each operation properly scoped to the authenticated user's data.

**Why this priority**: Enables comprehensive task management capabilities for AI assistants while maintaining security and proper data isolation.

**Independent Test**: Can be fully tested by verifying each MCP tool (add_task, list_tasks, update_task, delete_task) operates correctly under authenticated context with proper user scoping.

**Acceptance Scenarios**:

1. **Given** a user is logged in, **When** the AI agent uses the `add_task` tool, **Then** the task is created and associated with the authenticated user's account
2. **Given** a user is logged in with multiple tasks, **When** the AI agent uses the `list_tasks` tool, **Then** only the user's tasks are returned
3. **Given** a user is not authenticated, **When** any MCP tool is called, **Then** the system returns a 401 Unauthorized error

---

### User Story 3 - Secure Context and Authentication (Priority: P3)

All MCP tool calls automatically use the user context extracted from the verified JWT, ensuring no unauthorized access to other users' data occurs.

**Why this priority**: Critical for maintaining data privacy and security across all AI-assisted operations.

**Independent Test**: Can be fully tested by attempting MCP tool calls with different authentication states and verifying proper user scoping and authentication enforcement.

**Acceptance Scenarios**:

1. **Given** a valid JWT is present, **When** any MCP tool is invoked, **Then** the operation is executed within the context of the authenticated user
2. **Given** an invalid or expired JWT, **When** an MCP tool is invoked, **Then** the system returns a 401 Unauthorized error

---

### Edge Cases

- What happens when the JWT token is malformed or tampered with?
- How does the system handle race conditions when multiple MCP tools are called simultaneously for the same user?
- What occurs when an AI agent tries to access a task that belongs to a different user?
- How does the system handle cases where the user ID in the JWT doesn't correspond to an existing user in the database?
- What happens when the AI agent makes a tool call with invalid parameters that don't match the JSON Schema?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST expose 5 MCP tools: `add_task`, `list_tasks`, `complete_task`, `delete_task`, and `update_task` with strict JSON Schema definitions
- **FR-002**: System MUST integrate the OpenAI Agents SDK into the FastAPI backend to enable AI orchestration
- **FR-003**: System MUST enforce secure context by binding all MCP tool calls to the `user_id` extracted from the verified JWT
- **FR-004**: System MUST perform atomic database operations via SQLModel for all MCP tools and return immediate success/fail results
- **FR-005**: System MUST configure the agent's system prompt to ensure it confirms actions and handles "task not found" errors gracefully
- **FR-006**: System MUST return a 401 status code when a chat request is made without a valid JWT
- **FR-007**: System MUST validate all tool parameters against predefined JSON Schemas to minimize LLM hallucinations
- **FR-008**: System MUST ensure the AI agent does not guess or fabricate a user_id but uses only the one injected from the backend session
- **FR-009**: System MUST implement stateless tooling that performs discrete operations without maintaining conversation state

### Key Entities *(include if feature involves data)*

- **MCP Tool Context**: Represents the authenticated user context that binds all tool operations, containing validated user_id from JWT
- **AI Agent Session**: Represents a single interaction session with the AI, including authentication context and tool availability
- **Task Operation Request**: Represents a tool call with parameters and authentication context, following predefined JSON Schema

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All 5 MCP tools pass individual unit tests using the MCP Inspector with 100% success rate
- **SC-002**: The OpenAI Agent correctly selects the `complete_task` tool when prompted with "I finished the milk task" with at least 95% accuracy in controlled tests
- **SC-003**: API returns a 401 status code when a chat request is made without a valid JWT, with 100% reliability
- **SC-004**: System enforces proper user data isolation, ensuring zero cross-user data access through MCP tools in security testing