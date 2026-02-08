# Implementation Plan: ChatKit UI & Persistence

**Feature**: 007-todo-chatkit-persistence
**Created**: 2026-02-06
**Status**: Draft
**Author**: Claude

## Technical Context

### Current State
The system currently has a full-stack todo application with user authentication, task management, and testimonial systems. The backend is built with FastAPI and SQLModel, with Better Auth for authentication and Neon for PostgreSQL hosting. The MCP & Agent Logic (Spec 6) has been implemented with task tools.

### Target State
- **Session Bridge**: A `ChatKitServer` in FastAPI using `OpenAIConversationsSession` to map `conversation_id` to Neon DB records
- **Frontend Integration**: Mount the `@openai/chatkit-react` component in new `/dashboard/chat` route with `useChatKit` hook
- **Stateless Persistence**: Logic to fetch/store `Message` and `Conversation` models using SQLModel before/after Agent run
- **Proxy Configuration**: Updated `proxy.ts` for Next.js 16.1.2 to handle network boundary and streaming headers

### Dependencies

- **Better Auth Integration**: Using existing `BETTER_AUTH_SECRET` for session security
- **SQLModel & Neon**: Existing database infrastructure for conversation/message persistence
- **MCP & Agent Logic**: Reuse existing agent from Spec 6 for processing
- **Shadcn UI Components**: For visual polish and theme consistency

### Unknowns/Dependencies
- **[NEEDS CLARIFICATION]**: Exact API export syntax for Next.js 16.1.2 proxy configuration
- **[NEEDS CLARIFICATION]**: How to properly handle streaming responses with OpenAI ChatKit sessions
- **[NEEDS CLARIFICATION]**: Proper integration pattern between existing MCP tools and ChatKit interface
- **[NEEDS CLARIFICATION]**: How to authenticate ChatKit sessions with Better Auth JWT

## Constitution Check

Based on the project constitution, this implementation must:
- ✅ Follow the **Secure by Default** principle by ensuring user data isolation in conversations
- ✅ Maintain **Tech Stack Compliance** by using the specified stack (Next.js 16.1.2, FastAPI, SQLModel, Neon)
- ✅ Implement **Auth Protocol** with JWT-based verification and proper user_id validation
- ✅ Ensure **Security Enforcement** with 403 Forbidden for cross-user access attempts
- ✅ Adhere to **Data Integrity Requirements** through SQLModel transaction management
- ✅ Preserve the **Agentic Autonomy** approach by allowing Claude to generate the implementation

## Gates

### Gate 1: Architecture Feasibility
- [ ] Verify OpenAI ChatKit compatibility with existing authentication system
- [ ] Confirm SQLModel models can properly represent conversations/messages with tool calls
- [ ] Validate streaming response patterns work with FastAPI and Next.js proxy

### Gate 2: Security Validation
- [ ] Confirm user isolation between conversations (no cross-access)
- [ ] Validate JWT token verification for ChatKit sessions
- [ ] Verify authentication context properly propagates to MCP tools

### Gate 3: UI/UX Validation
- [ ] Ensure ChatKit UI follows Spec 4 styling (#0FFF50 accents)
- [ ] Validate tool call indicators display properly in message UI
- [ ] Confirm dark/light theme integration works seamlessly

## Phase 0: Research & Resolution of Unknowns

### Research Task 0.1: Next.js 16.1.2 Proxy Configuration
**Objective**: Determine the correct export syntax and streaming header handling for Next.js 16.1.2 proxy

**Approach**:
- Research Next.js 16.1.2 documentation for proxy patterns
- Examine existing proxy configurations in the codebase
- Identify proper streaming header configuration for ChatKit integration

**Expected Outcome**: Clear understanding of Next.js proxy configuration for ChatKit streaming responses

### Research Task 0.2: OpenAI ChatKit Session Integration
**Objective**: Understand how to properly create and manage ChatKit sessions with SQLModel persistence

**Approach**:
- Review OpenAI ChatKit documentation and API patterns
- Study session creation with conversation mapping to database records
- Determine how to handle real-time tool invocation logs during streaming

**Expected Outcome**: Clear pattern for creating ChatKit sessions that map to SQLModel Conversation records

### Research Task 0.3: MCP Tool Integration with ChatKit UI
**Objective**: Determine how to properly display MCP tool execution in the ChatKit interface

**Approach**:
- Research ChatKit's ability to show custom components for tool results
- Identify patterns for displaying tool status (in-progress, success, error)
- Plan for proper message formatting with tool call information

**Expected Outcome**: Clear approach for integrating MCP tools with ChatKit UI for visual feedback

### Research Task 0.4: Better Auth JWT Integration with ChatKit
**Objective**: Understand how to secure ChatKit sessions with Better Auth JWT tokens

**Approach**:
- Review Better Auth token structure and validation patterns
- Identify how to tie ChatKit user parameter to logged-in user context
- Plan for cryptographic validation using BETTER_AUTH_SECRET

**Expected Outcome**: Secure authentication pattern for ChatKit sessions

## Phase 1: Data Model & API Design

### 1.1 Conversation & Message Models
**Objective**: Design SQLModel entities for persistent chat history with proper relationships

**Entities to Design**:
- **Conversation**: title, user_id (FK), created_at, updated_at
- **Message**: conversation_id (FK), role (user/assistant), content, tool_calls, created_at
- **Relationships**: User ↔ Conversation (1:M), Conversation ↔ Message (1:M)

**Validation Rules**:
- User can only access their own conversations
- Message role restricted to 'user' or 'assistant'
- Tool calls properly stored as JSON arrays

**Deliverables**:
- `data-model.md` with entity definitions and validation rules
- `contracts/conversation-openapi.yaml` with API specification

### 1.2 API Contract Design
**Objective**: Define API endpoints for ChatKit session management and persistence

**Endpoints to Design**:
- `POST /api/{user_id}/chatkit/session`: Create ChatKit session for authenticated user
- `GET /api/{user_id}/conversations`: List user's conversations
- `GET /api/{user_id}/conversations/{conv_id}/messages`: Get conversation messages
- `POST /api/{user_id}/chat`: Main chat endpoint with history management

**Patterns**: RESTful API following existing application patterns

**Deliverables**:
- OpenAPI specification for all endpoints
- Request/response schemas
- Authentication and authorization requirements

## Phase 2: Session Bridge Implementation

### 2.1 ChatKit Server Integration
**Objective**: Create the bridge between ChatKit sessions and SQLModel database

**Implementation Tasks**:
- Implement `ChatKitServer` class in FastAPI
- Create conversation-to-database mapping logic
- Implement message persistence before/after agent processing

**Key Considerations**:
- Proper streaming response handling
- Conversation context window management (last 10-15 messages)
- Tool call information persistence and retrieval

### 2.2 Authentication & Authorization
**Objective**: Secure ChatKit sessions with Better Auth JWT validation

**Implementation Tasks**:
- JWT token verification using existing middleware
- User context injection into ChatKit session
- Cross-user access prevention

## Phase 3: Frontend Integration

### 3.1 ChatKit Component Integration
**Objective**: Mount OpenAI ChatKit component with proper styling and functionality

**Implementation Tasks**:
- Create `/dashboard/chat` route with ChatKit component
- Implement `useChatKit` hook for API communication
- Style integration with #0FFF50 accents and Shadcn components

### 3.2 Tool Call Visualization
**Objective**: Display MCP tool execution with proper UI indicators

**Implementation Tasks**:
- Create custom message components for tool calls
- Implement "Thinking" state indicators during tool execution
- Add success/failure badges for tool operations

## Phase 4: Proxy & Streaming Configuration

### 4.1 Next.js Proxy Setup
**Objective**: Configure proxy to handle ChatKit streaming with proper headers

**Implementation Tasks**:
- Update `proxy.ts` for Next.js 16.1.2 compatibility
- Implement streaming response handling
- Configure appropriate headers for ChatKit communication

## Phase 5: Testing & Validation

### 5.1 Memory & Persistence Testing
**Test Scenario**: Send message → Refresh browser → Verify conversation history persists via ChatKit API

### 5.2 Security Testing
**Test Scenario**: Attempt to access another user's conversation_id → Verify 403 Forbidden response

### 5.3 Tool UI Testing
**Test Scenario**: Trigger `add_task` call → Verify "Success" badge appears in chat flow

## Revisited Constitution Check (Post-Design)

- ✅ **Secure by Default**: User isolation enforced at database and API layers
- ✅ **Tech Stack Compliance**: Uses Next.js 16.1.2, FastAPI, SQLModel, Neon as specified
- ✅ **Auth Protocol**: JWT-based authentication with Better Auth integration
- ✅ **Security Enforcement**: Proper authorization checks for conversation access
- ✅ **Data Integrity**: SQLModel-based transactions for conversation/message persistence
- ✅ **Agentic Autonomy**: Following Claude Code/SKP workflow for all implementation