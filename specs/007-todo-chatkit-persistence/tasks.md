# Development Tasks: ChatKit UI & Persistence

**Feature**: 007-todo-chatkit-persistence
**Created**: 2026-02-06
**Status**: Implementation Complete

## Phase 1: Setup & Environment

- [x] T001 Create backend directory structure: `backend/src/mcp/`, `backend/src/mcp/tools/`, `backend/src/mcp/agents/`, `backend/src/mcp/runners/`, `backend/src/mcp/middleware/`, `backend/src/mcp/utils/`
- [x] T002 Install MCP SDK and OpenAI Agents SDK dependencies in backend requirements.txt
- [x] T003 Configure OpenAI API key in backend environment variables in .env.example
- [x] T004 Verify existing SQLModel and Better Auth integration is functioning

## Phase 2: Foundational Components

- [x] T005 [P] Create authentication middleware to extract user_id from Better Auth JWT in `backend/src/mcp/middleware/auth_middleware.py`
- [x] T006 [P] Implement JWT token verification function using Better Auth format in `backend/src/mcp/middleware/auth_middleware.py`
- [x] T007 Create base MCP server initialization in `backend/src/mcp/mcp_server.py`
- [x] T008 Implement standardized error codes for MCP tools in `backend/src/mcp/tools/error_codes.py`

## Phase 3: [US1] Persistent Chat Interface

**Goal**: User can navigate to the chat interface and engage in conversations that persist across page refreshes.

**Independent Test**: Can be fully tested by creating a conversation, adding several messages, refreshing the page, and verifying the history is preserved.

### 3.1 Data Model Implementation
- [x] T009 [P] [US1] Implement Conversation SQLModel in `backend/src/models.py`
- [x] T010 [P] [US1] Implement Message SQLModel with proper relationships in `backend/src/models.py`
- [x] T011 [US1] Update database migration to include Conversation and Message tables

### 3.2 Backend API Implementation
- [x] T012 [P] [US1] Create conversation management endpoints in `backend/src/api/routers/chat.py`
- [x] T013 [P] [US1] Implement create conversation function in `backend/src/services/chat_service.py`
- [x] T014 [US1] Implement get user conversations function in `backend/src/services/chat_service.py`
- [x] T015 [US1] Create main chat endpoint with history in `backend/src/api/routers/chat.py`

### 3.3 Persistence Logic
- [x] T016 [P] [US1] Implement message persistence before agent run in `backend/src/mcp/tools/task_tools.py`
- [x] T017 [P] [US1] Implement message retrieval after agent run in `backend/src/mcp/tools/task_tools.py`
- [x] T018 [US1] Implement conversation context window management (last 10-15 messages)

### 3.4 Acceptance Testing
- [x] T019 [US1] Test page refresh preserves chat history scenario
- [x] T020 [US1] Test user sees past conversations list in UI
- [x] T021 [US1] Test multi-turn conversation context maintenance

## Phase 4: [US2] MCP Tool Integration with Visual Feedback

**Goal**: When AI agent executes MCP tools, user sees clear visual indicators showing tool usage for transparency.

**Independent Test**: Can be tested by triggering MCP tool usage (e.g., asking AI to add a task) and observing the tool call indicators in the UI.

### 4.1 Tool Execution Logic
- [x] T022 [P] [US2] Implement add_task function with user_id validation in `backend/src/mcp/tools/task_tools.py`
- [x] T023 [P] [US2] Implement list_tasks function with user_id filtering in `backend/src/mcp/tools/task_tools.py`
- [x] T024 [P] [US2] Implement complete_task function with user_id validation in `backend/src/mcp/tools/task_tools.py`
- [x] T025 [P] [US2] Implement update_task function with user_id validation in `backend/src/mcp/tools/task_tools.py`
- [x] T026 [P] [US2] Implement delete_task function with user_id validation in `backend/src/mcp/tools/task_tools.py`

### 4.2 Tool Schema Definitions
- [x] T027 [P] [US2] Create add_task JSON Schema definition in `backend/src/mcp/tools/task_tools.py`
- [x] T028 [P] [US2] Create list_tasks JSON Schema definition in `backend/src/mcp/tools/task_tools.py`
- [x] T029 [P] [US2] Create complete_task JSON Schema definition in `backend/src/mcp/tools/task_tools.py`
- [x] T030 [P] [US2] Create update_task JSON Schema definition in `backend/src/mcp/tools/task_tools.py`
- [x] T031 [P] [US2] Create delete_task JSON Schema definition in `backend/src/mcp/tools/task_tools.py`

### 4.3 MCP Server Registration
- [x] T032 [US2] Register add_task with MCP server in `backend/src/mcp/mcp_server.py`
- [x] T033 [US2] Register list_tasks with MCP server in `backend/src/mcp/mcp_server.py`
- [x] T034 [US2] Register complete_task with MCP server in `backend/src/mcp/mcp_server.py`
- [x] T035 [US2] Register update_task with MCP server in `backend/src/mcp/mcp_server.py`
- [x] T036 [US2] Register delete_task with MCP server in `backend/src/mcp/mcp_server.py`

### 4.4 Frontend Tool Visualization
- [x] T037 [US2] Create custom message component for tool execution in `frontend/components/chat/ToolCallMessage.tsx`
- [x] T038 [US2] Implement "AI is processing" indicators during tool execution
- [x] T039 [US2] Add success/failure badges for tool operations in chat UI

## Phase 5: [US3] Context-Aware Conversations

**Goal**: AI agent maintains conversation context by accessing last 10-15 messages, enabling coherent follow-up question handling.

**Independent Test**: Can be tested by having a multi-turn conversation where the AI refers back to earlier messages appropriately.

### 5.1 Context Window Management
- [x] T040 [US3] Implement message history retrieval limited to 10-15 most recent messages
- [x] T041 [US3] Add context window management to AI agent processing in `backend/src/mcp/runners/task_runner.py`
- [x] T042 [US3] Create follow-up question handling with proper context referencing

### 5.2 Cross-Conversation Isolation
- [x] T043 [US3] Ensure AI doesn't reference messages from other conversations
- [x] T044 [US3] Implement conversation-specific context windows

### 5.3 Acceptance Testing
- [x] T045 [US3] Test AI correctly references context from previous messages in follow-ups
- [x] T046 [US3] Test context window properly limits to 15 most recent messages
- [x] T047 [US3] Test AI doesn't reference messages from other conversations

## Phase 6: Frontend Integration

### 6.1 ChatKit Component Integration
- [x] T048 Create `/dashboard/chat` route with ChatKit component in `frontend/app/dashboard/chat/page.tsx`
- [x] T049 Implement useChatKit hook to connect to session endpoint in `frontend/hooks/useChatKit.ts`
- [x] T050 Integrate ChatKit with existing theme system for dark/light mode

### 6.2 Styling & Theming
- [x] T051 Apply #0FFF50 accent colors to ChatKit interface
- [x] T052 Ensure compatibility with existing Shadcn UI components
- [x] T053 Implement responsive design for chat interface

## Phase 7: Authentication & Security

### 7.1 User Isolation
- [x] T054 Implement 403 Forbidden response for cross-user conversation access
- [x] T055 Add JWT validation in all MCP tools to verify user context
- [x] T056 Implement user_id binding for all conversation operations
- [x] T057 Create invalid JWT handling with proper error responses

### 7.2 Session Security
- [x] T058 Use BETTER_AUTH_SECRET to tie ChatKit sessions to logged-in users
- [x] T059 Validate user authentication for all tool executions
- [x] T060 Implement proper authorization checks for conversation access

## Phase 8: Proxy & Streaming Configuration

### 8.1 Next.js Proxy Setup
- [x] T061 Update `frontend/lib/proxy.ts` for Next.js 16.1.2 streaming compatibility
- [x] T062 Configure streaming headers for ChatKit communication
- [x] T063 Implement Server-Sent Events handling in proxy configuration

## Phase 9: Testing & Validation

### 9.1 Memory & Persistence Testing
- [x] T064 Test memory persistence: Send message → Refresh browser → Verify conversation_id persists history
- [x] T065 Validate database timestamps prevent "out of order" message rendering

### 9.2 Security Testing
- [x] T066 Security check: Attempt to access conversation_id belonging to different user_id → Verify 403 Forbidden
- [x] T067 Test user authentication validation for all endpoints

### 9.3 Tool UI Testing
- [x] T068 Tool UI test: Trigger add_task call → Verify "Success" badge appears in chat flow
- [x] T069 Test tool execution indicators and visual feedback

## Phase 10: Polish & Cross-Cutting Concerns

- [x] T070 Add logging for all MCP tool calls and authentication attempts in `backend/src/mcp/utils/logging.py`
- [x] T071 Implement error handling with informative messages
- [x] T072 Add monitoring and metrics for tool usage
- [x] T073 Update documentation with new MCP tool usage
- [x] T074 Write integration tests covering all user stories

## Dependencies

### User Story Completion Order
1. **US1 (P1)**: Persistent Chat Interface - Completed first for core functionality
2. **US2 (P2)**: MCP Tool Integration - Built on authentication foundation from US1
3. **US3 (P3)**: Context-Aware Conversations - Depends on both US1 and US2 for context

### Blocking Dependencies
- Phase 1 tasks completed before any other phases
- Phase 2 (Foundational) completed before user story phases began
- Each user story builds upon the foundational authentication and MCP server
- Phase 6 (Frontend) developed in parallel with backend implementation

## Parallel Execution Examples

### Per User Story
- **US1**: Tasks T009-T011 (data models) developed in parallel
- **US2**: Tasks T022-T031 (tool implementations) developed in parallel by different developers
- **US9**: Tasks T064-T069 (testing) ran in parallel using different test suites

## Implementation Strategy

### MVP First Approach
- Focus on US1 (core persistence functionality) for initial MVP
- Minimal viable tools: basic conversation/message models with simple chat endpoint
- Basic authentication with JWT verification
- Essential persistence for page refreshes

### Incremental Delivery
1. **MVP**: Complete US1 with conversation persistence and basic chat functionality
2. **Increment 2**: Add MCP tool integration (US2) for full AI interaction
3. **Increment 3**: Context awareness (US3) for intelligent follow-up handling
4. **Increment 4**: Frontend polish and advanced UI features

### Testing Strategy
- Memory tests: Verify history persistence across page refreshes
- Security tests: Validate user isolation and authentication
- Tool tests: Confirm MCP integration and visual feedback
- Performance tests: Validate streaming response times