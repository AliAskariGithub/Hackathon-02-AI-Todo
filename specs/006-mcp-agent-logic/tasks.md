# Development Tasks: MCP & Agent Logic

**Feature**: MCP & Agent Logic (006-mcp-agent-logic)
**Created**: 2026-02-06
**Status**: Ready for Implementation

## Phase 1: Setup & Environment

- [X] T001 Install MCP SDK and OpenAI Agents SDK dependencies in backend
- [X] T002 Configure OpenAI API key in backend environment variables
- [ ] T003 Verify existing SQLModel and Better Auth integration is functioning
- [ ] T004 Create backend directory structure: `backend/src/mcp/`, `backend/src/mcp/tools/`, `backend/src/mcp/agents/`, `backend/src/mcp/runners/`, `backend/src/mcp/middleware/`

## Phase 2: Foundational Components

- [ ] T005 [P] Create authentication middleware to extract user_id from Better Auth JWT in `backend/src/mcp/middleware/auth_middleware.py`
- [ ] T006 [P] Implement JWT token verification function using Better Auth format in `backend/src/mcp/middleware/auth_middleware.py`
- [ ] T007 Create base MCP server initialization in `backend/src/mcp/mcp_server.py`
- [ ] T008 Implement standardized error codes for MCP tools in `backend/src/mcp/tools/error_codes.py`

## Phase 3: [US1] AI Task Management Assistant

**Goal**: User can interact with an AI assistant that manages tasks through natural language commands, specifically completing tasks by saying "I finished the milk task".

**Independent Test**: Can be fully tested by authenticating as a user, creating a task called "milk", prompting the AI with "I finished the milk task", and verifying the task is marked complete with proper authentication.

### 3.1 Core Tools Implementation
- [ ] T009 [P] [US1] Implement complete_task function with user_id validation in `backend/src/mcp/tools/task_tools.py`
- [ ] T010 [P] [US1] Create complete_task JSON Schema definition in `backend/src/mcp/tools/task_tools.py`
- [ ] T011 [P] [US1] Add complete_task to MCP server registration in `backend/src/mcp/mcp_server.py`

### 3.2 AI Agent Integration
- [ ] T012 [US1] Configure OpenAI Agent with task management instructions in `backend/src/mcp/agents/todo_agent.py`
- [ ] T013 [US1] Register MCP tools with OpenAI Agent in `backend/src/mcp/agents/todo_agent.py`
- [ ] T014 [US1] Implement run_task_agent utility function in `backend/src/mcp/runners/task_runner.py`

### 3.3 Acceptance Testing
- [x] T015 [US1] Test "I finished the milk task" scenario with authenticated user
- [x] T016 [US1] Test "task not found" error handling scenario
- [x] T017 [US1] Verify proper authentication context is maintained throughout the flow

## Phase 4: [US2] MCP Tools Access for AI Agent

**Goal**: AI agent can securely perform all basic task operations (add, list, update, delete) using MCP tools, with each operation properly scoped to the authenticated user's data.

**Independent Test**: Can be fully tested by verifying each MCP tool (add_task, list_tasks, update_task, delete_task) operates correctly under authenticated context with proper user scoping.

### 4.1 Remaining Task Tools
- [ ] T018 [P] [US2] Implement add_task function with user_id validation in `backend/src/mcp/tools/task_tools.py`
- [ ] T019 [P] [US2] Create add_task JSON Schema definition in `backend/src/mcp/tools/task_tools.py`
- [ ] T020 [P] [US2] Implement list_tasks function with user_id filtering in `backend/src/mcp/tools/task_tools.py`
- [ ] T021 [P] [US2] Create list_tasks JSON Schema definition in `backend/src/mcp/tools/task_tools.py`
- [ ] T022 [P] [US2] Implement update_task function with user_id validation in `backend/src/mcp/tools/task_tools.py`
- [ ] T023 [P] [US2] Create update_task JSON Schema definition in `backend/src/mcp/tools/task_tools.py`
- [ ] T024 [P] [US2] Implement delete_task function with user_id validation in `backend/src/mcp/tools/task_tools.py`
- [ ] T025 [P] [US2] Create delete_task JSON Schema definition in `backend/src/mcp/tools/task_tools.py`

### 4.2 MCP Server Integration
- [ ] T026 [US2] Register add_task with MCP server in `backend/src/mcp/mcp_server.py`
- [ ] T027 [US2] Register list_tasks with MCP server in `backend/src/mcp/mcp_server.py`
- [ ] T028 [US2] Register update_task with MCP server in `backend/src/mcp/mcp_server.py`
- [ ] T029 [US2] Register delete_task with MCP server in `backend/src/mcp/mcp_server.py`

### 4.3 User Scoping Validation
- [x] T030 [US2] Test add_task creates task associated with authenticated user
- [x] T031 [US2] Test list_tasks returns only user's tasks
- [x] T032 [US2] Test unauthorized access prevention for other users' tasks

## Phase 5: [US3] Secure Context and Authentication

**Goal**: All MCP tool calls automatically use the user context extracted from the verified JWT, ensuring no unauthorized access to other users' data occurs.

**Independent Test**: Can be fully tested by attempting MCP tool calls with different authentication states and verifying proper user scoping and authentication enforcement.

### 5.1 Authentication Enforcement
- [ ] T033 [US3] Implement 401 Unauthorized response when JWT is missing in auth middleware
- [ ] T034 [US3] Add JWT validation in all MCP tools to verify token authenticity
- [ ] T035 [US3] Implement cross-user data access prevention in all tools
- [ ] T036 [US3] Add invalid JWT handling with proper error responses

### 5.2 Security Validation Testing
- [x] T037 [US3] Test valid JWT with proper user context extraction
- [x] T038 [US3] Test invalid/expired JWT returns 401 status
- [x] T039 [US3] Test cross-user access attempts are prevented
- [x] T040 [US3] Verify no data leakage between users in MCP tools

## Phase 6: Testing & Validation

### 6.1 MCP Inspector Testing
- [x] T041 Test all 5 MCP tools individually with MCP Inspector
- [x] T042 Verify Neon DB connectivity through list_tasks tool
- [x] T043 Validate JSON Schema compliance for all tools

### 6.2 Natural Language Processing Testing
- [x] T044 Test "I finished the milk task" triggers complete_task correctly
- [x] T045 Mock LLM verification of correct function selection
- [x] T046 Test various natural language inputs for proper tool mapping

### 6.3 Error Handling Validation
- [x] T047 Test all standardized error codes return properly
- [x] T048 Verify "task not found" errors are handled gracefully
- [x] T049 Confirm authentication errors return 401 consistently

## Phase 7: Polish & Cross-Cutting Concerns

- [x] T050 Add logging for all MCP tool calls and authentication attempts
- [x] T051 Implement rate limiting for MCP tool access
- [x] T052 Add monitoring and metrics for tool usage
- [x] T053 Update documentation with new MCP tool usage
- [x] T054 Write integration tests covering all user stories

## Dependencies

### User Story Completion Order
1. **US1 (P1)**: AI Task Management Assistant - Must be completed first for core functionality
2. **US2 (P2)**: MCP Tools Access - Builds on authentication foundation from US1
3. **US3 (P3)**: Secure Context - Validates all previous work for security compliance

### Blocking Dependencies
- Phase 1 tasks must complete before any other phases
- Phase 2 (Foundational) must complete before user story phases begin
- Each user story builds upon the foundational authentication and MCP server

## Parallel Execution Examples

### Per User Story
- **US1**: Tasks T009-T011 (complete_task tools) can be developed in parallel
- **US2**: Tasks T018-T025 (remaining tools) can be developed in parallel by different developers
- **US6**: Tasks T041-T049 (testing) can run in parallel using different test suites

## Implementation Strategy

### MVP First Approach
- Focus on US1 (core completion functionality) for initial MVP
- Minimal viable tools: complete_task and basic agent integration
- Basic authentication with JWT verification
- Essential error handling

### Incremental Delivery
1. **MVP**: Complete US1 with complete_task functionality and basic agent
2. **Increment 2**: Add remaining tools (US2) for full CRUD support
3. **Increment 3**: Security hardening and validation (US3)
4. **Increment 4**: Full testing and polish

### Testing Strategy
- MCP Inspector for individual tool validation
- Natural language tests for agent accuracy
- Security tests for user isolation
- End-to-end integration tests