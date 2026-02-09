# Implementation Plan: AI Chatbot & Persistence

**Branch**: `001-ai-chatbot-persistence` | **Date**: 2026-02-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-ai-chatbot-persistence/spec.md`

## Summary

Implement a conversational AI interface that allows users to manage their tasks through natural language commands. The system integrates OpenAI Agents SDK with OpenRouter for AI processing, uses MCP (Model Context Protocol) Server for task CRUD operations, persists conversations and messages in PostgreSQL via SQLModel, and provides a streaming chat UI using OpenAI ChatKit with Next.js 16.1.2 App Router.

**Core Value**: Enable hands-free task management through natural conversation, maintaining context across sessions while ensuring user data isolation and cost control through rate limiting.

## Technical Context

**Language/Version**:
- Backend: Python 3.11+ (FastAPI)
- Frontend: TypeScript with Next.js 16.1.2

**Primary Dependencies**:
- Backend: FastAPI, SQLModel, AsyncOpenAI (configured for OpenRouter), python-requests, python-dotenv
- Frontend: Next.js 16.1.2, React 18+, OpenAI ChatKit, Shadcn UI, Tailwind CSS
- Database: PostgreSQL (Neon Serverless)
- AI Service: OpenRouter API (model: openai/gpt-oss-120b:free)
- Authentication: Better Auth JWT (existing)

**Storage**:
- PostgreSQL (Neon Serverless) with SQLModel ORM
- New tables: `conversations`, `messages`
- Existing tables: `users`, `tasks`

**Testing**:
- Backend: pytest for unit and integration tests
- Frontend: Jest + React Testing Library
- E2E: Playwright for critical user flows
- Specific tests: OpenRouter connection, user isolation, streaming behavior, AI logic validation

**Target Platform**:
- Backend: Linux server (production), Windows (development - known DNS resolution issues with async)
- Frontend: Modern web browsers (Chrome, Firefox, Safari, Edge)
- Deployment: Vercel (frontend), Hugging Face Spaces (backend)

**Project Type**: Web application (separate frontend and backend services)

**Performance Goals**:
- Message send to AI response start: <1 second (SC-005)
- Task creation via chat: <10 seconds end-to-end (SC-001)
- Conversation history load: <2 seconds (SC-004)
- Concurrent users: 100 without degradation (SC-006)
- AI interpretation accuracy: 95% for common commands (SC-003)

**Constraints**:
- Rate limiting: 20 messages/minute, 200 messages/hour per user (FR-021)
- Message length: 2,000 characters maximum (FR-001)
- AI timeout: 30 seconds (FR-022)
- Context window: Last 15 messages (FR-010)
- Data retention: Indefinite with user-initiated deletion (FR-006)
- No offline support (assumption)
- Text-only conversations (assumption)

**Scale/Scope**:
- Expected users: 100 concurrent, ~1,000 total
- Conversations per user: Up to 10 actively managed (SC-008)
- Messages per conversation: Unlimited (with pagination for display)
- Context maintenance: 20+ consecutive messages (SC-002)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Agentic Autonomy
**Status**: PASS
- All code will be generated via Claude Code and Spec-Kit Plus workflow
- No manual code edits during development process

### ✅ Live Documentation
**Status**: PASS
- Will use Context7 MCP Server for Next.js 16.1.2 proxy.ts streaming patterns
- Will verify OpenAI ChatKit integration patterns
- Will confirm AsyncOpenAI client configuration for custom base URLs

### ✅ Secure by Default
**Status**: PASS
- User isolation enforced: All conversations and messages scoped to authenticated user (FR-004, FR-005, FR-018)
- JWT authentication required for all chat endpoints
- Rate limiting prevents abuse (FR-021)
- User ID hard-coded into MCP tool calls by backend (not provided by AI)

### ✅ Modernity
**Status**: PASS
- Uses Next.js 16.1.2 App Router (latest)
- Uses OpenAI ChatKit for modern chat UI
- Uses Shadcn UI components
- Uses AsyncOpenAI client with streaming support

### ✅ Tech Stack Compliance
**Status**: PASS
- Next.js 16.1.2 ✓
- FastAPI ✓
- SQLModel ✓
- Neon Serverless PostgreSQL ✓
- Better Auth JWT (existing, will reuse) ✓

### ✅ Auth Protocol
**Status**: PASS
- Reuses existing Better Auth JWT implementation
- JWT middleware validates all chat endpoint requests
- User ID extracted from JWT for conversation/message scoping

### ✅ API Design Standards
**Status**: PASS
- RESTful endpoints: `/api/{user_id}/conversations`, `/api/{user_id}/chat`
- User ID path parameter validation
- JWT middleware filtering
- Consistent error responses

### ✅ UI/UX Standards
**Status**: PASS
- Responsive design using Shadcn UI components
- Mobile-first approach with OpenAI ChatKit
- Streaming responses for better perceived performance
- Loading indicators and error states

### ✅ Data Integrity Requirements
**Status**: PASS
- SQLModel transactions for conversation/message operations
- Neon-specific connection pooling (existing configuration)
- Foreign key constraints for data relationships

### ✅ Version Control Policy
**Status**: PASS
- Next.js pinned to 16.1.2
- All dependencies version-locked in package.json and requirements.txt

### ✅ Security Enforcement
**Status**: PASS
- All chat endpoints return 401 if JWT missing/invalid
- Rate limiting enforced at API level
- User data isolation at database query level

### ✅ Architecture Boundaries
**Status**: PASS
- Frontend (Next.js) and Backend (FastAPI) remain separate services
- Communication over HTTPS/REST
- Clear API contracts between services

### ✅ Environment Management
**Status**: PASS
- Secrets in .env files: GROQ_API_KEY, GROQ_MODEL, DATABASE_URL, BETTER_AUTH_SECRET
- No hardcoded credentials

**Constitution Check Result**: ✅ ALL GATES PASSED - Proceed to Phase 0

## Project Structure

### Documentation (this feature)

```text
specs/001-ai-chatbot-persistence/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (in progress)
├── research.md          # Phase 0 output (to be created)
├── data-model.md        # Phase 1 output (to be created)
├── quickstart.md        # Phase 1 output (to be created)
├── contracts/           # Phase 1 output (to be created)
│   ├── chat-api.yaml   # OpenAPI spec for chat endpoints
│   └── mcp-tools.md    # MCP tool function signatures
├── checklists/
│   └── requirements.md  # Specification quality checklist (completed)
└── tasks.md             # Phase 2 output (created by /sp.tasks command)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── user.py              # Existing
│   │   ├── task.py              # Existing
│   │   ├── conversation.py      # NEW: Conversation model
│   │   └── message.py           # NEW: Message model
│   ├── services/
│   │   ├── user_service.py      # Existing
│   │   ├── task_service.py      # Existing
│   │   ├── chat_service.py      # NEW: Conversation/message CRUD
│   │   └── rate_limit_service.py # NEW: Rate limiting logic
│   ├── api/
│   │   └── routers/
│   │       ├── users.py         # Existing
│   │       ├── tasks.py         # Existing
│   │       └── chat.py          # NEW: Chat endpoints
│   ├── mcp/
│   │   ├── server.py            # Existing MCP server
│   │   ├── tools/
│   │   │   └── task_tools.py    # Existing task CRUD tools
│   │   ├── agents/
│   │   │   └── todo_agent.py    # NEW: Agent configuration
│   │   └── runners/
│   │       └── task_runner.py   # NEW: Agent execution logic
│   └── utils/
│       ├── openrouter_client.py # NEW: AsyncOpenAI client setup
│       └── context_builder.py   # NEW: Build context from messages
├── tests/
│   ├── test_chat_api.py         # NEW: Chat endpoint tests
│   ├── test_rate_limiting.py    # NEW: Rate limit tests
│   ├── test_user_isolation.py   # NEW: Security tests
│   └── test_agent_logic.py      # NEW: AI behavior tests
└── .env                          # Add GROQ_API_KEY, GROQ_MODEL

frontend/
├── src/
│   ├── app/
│   │   ├── chat/
│   │   │   ├── page.tsx         # NEW: Chat page
│   │   │   └── [conversationId]/
│   │   │       └── page.tsx     # NEW: Specific conversation view
│   │   └── api/
│   │       └── chat/
│   │           └── route.ts     # NEW: Proxy to backend with streaming
│   ├── components/
│   │   ├── chat/
│   │   │   ├── ChatInterface.tsx      # NEW: Main chat UI (ChatKit)
│   │   │   ├── ConversationList.tsx   # NEW: Conversation sidebar
│   │   │   ├── MessageList.tsx        # NEW: Message display
│   │   │   └── MessageInput.tsx       # NEW: Input with char limit
│   │   └── ui/                  # Existing Shadcn components
│   ├── lib/
│   │   └── chat-api.ts          # NEW: Frontend API client for chat
│   └── hooks/
│       ├── useChat.ts           # NEW: Chat state management
│       └── useConversations.ts  # NEW: Conversation list management
└── tests/
    └── chat/
        ├── ChatInterface.test.tsx
        └── streaming.test.ts
```

**Structure Decision**: Web application structure (Option 2) with separate backend and frontend services. This aligns with the existing project architecture and maintains clear separation of concerns. The backend handles AI integration, MCP tools, and data persistence, while the frontend provides the chat UI with streaming support.

## Complexity Tracking

> No constitution violations detected. All requirements align with established principles.

---

## Phase 0: Research & Discovery

### Research Tasks

#### R1: OpenRouter AsyncOpenAI Client Configuration
**Question**: How to configure AsyncOpenAI client to point to OpenRouter's base URL and handle streaming responses?

**Research Approach**:
- Review AsyncOpenAI documentation for custom base_url configuration
- Verify streaming support with OpenRouter API
- Test connection with openai/gpt-oss-120b:free model
- Document authentication header requirements

**Expected Output**: Code pattern for initializing AsyncOpenAI client with OpenRouter configuration

#### R2: Next.js 16.1.2 Streaming Proxy Pattern
**Question**: What are the correct Response headers and streaming patterns for Next.js 16.1.2 App Router to proxy streaming AI responses?

**Research Approach**:
- Use Context7 MCP to fetch Next.js 16.1.2 Route Handler documentation
- Verify text/event-stream vs application/x-ndjson content types
- Test streaming with ReadableStream and TransformStream
- Document any Next.js 16-specific changes from previous versions

**Expected Output**: Working proxy.ts pattern for streaming OpenRouter responses through Next.js

#### R3: OpenAI ChatKit Integration
**Question**: How to integrate OpenAI ChatKit with custom backend API and streaming responses?

**Research Approach**:
- Review ChatKit documentation for custom API integration
- Verify compatibility with Next.js 16.1.2 App Router
- Test message rendering and streaming display
- Document configuration options for Shadcn UI styling

**Expected Output**: ChatKit setup pattern with custom API adapter

#### R4: MCP Tool Function Signatures
**Question**: What is the optimal function signature and docstring format for MCP tools to ensure the AI understands when and how to use them?

**Research Approach**:
- Review existing MCP tool implementations in backend/src/mcp/tools/
- Document best practices for tool descriptions
- Test AI tool selection with different docstring formats
- Verify JSON return format for task data

**Expected Output**: MCP tool template with clear docstrings and type hints

#### R5: Rate Limiting Implementation Strategy
**Question**: How to implement per-user rate limiting (20/min, 200/hour) in FastAPI with minimal performance overhead?

**Research Approach**:
- Evaluate in-memory vs Redis-based rate limiting
- Consider slowapi library vs custom implementation
- Test performance impact with 100 concurrent users
- Document cleanup strategy for expired rate limit data

**Expected Output**: Rate limiting middleware pattern for FastAPI

#### R6: Windows DNS Resolution Workaround
**Question**: How to resolve the Windows asyncio DNS resolution issue when calling OpenRouter from FastAPI?

**Research Approach**:
- Document the current issue (works in standalone script, fails in FastAPI)
- Test synchronous requests library with asyncio.to_thread()
- Verify if issue persists in Linux deployment environment
- Document workaround or deployment recommendation

**Expected Output**: Working solution or documented deployment constraint

### Research Deliverable

All research findings will be consolidated in `research.md` with:
- Decision made for each research task
- Rationale for the chosen approach
- Alternatives considered and why they were rejected
- Code examples or patterns to be used in implementation

---

## Phase 1: Design & Contracts

### Data Model Design

**File**: `data-model.md`

#### New Entities

**Conversation**
- `id`: UUID (primary key)
- `user_id`: UUID (foreign key to users table, indexed)
- `title`: String (max 200 characters, default "New Conversation")
- `created_at`: DateTime (auto-generated)
- `updated_at`: DateTime (auto-updated on message add)
- **Relationships**:
  - Belongs to one User
  - Has many Messages (cascade delete)
- **Indexes**: user_id, updated_at (for sorting conversation list)
- **Constraints**: user_id must exist in users table

**Message**
- `id`: UUID (primary key)
- `conversation_id`: UUID (foreign key to conversations table, indexed)
- `role`: Enum('user', 'assistant')
- `content`: Text (max 2,000 characters for user messages, unlimited for assistant)
- `created_at`: DateTime (auto-generated)
- `tool_calls`: JSONB (nullable, stores MCP tool invocations)
- **Relationships**:
  - Belongs to one Conversation
- **Indexes**: conversation_id, created_at (for chronological ordering)
- **Constraints**: conversation_id must exist in conversations table

#### Existing Entities (Reference)

**User** (no changes)
- `id`: UUID
- `user_name`: String
- `email`: String
- `password`: String (hashed)
- `created_at`: DateTime
- `updated_at`: DateTime

**Task** (no changes)
- `id`: UUID
- `user_id`: UUID (foreign key)
- `description`: String
- `is_completed`: Boolean
- `created_at`: DateTime
- `updated_at`: DateTime

#### Entity Relationships

```
User (1) ──< (many) Conversation
Conversation (1) ──< (many) Message
User (1) ──< (many) Task
```

### API Contracts

**File**: `contracts/chat-api.yaml` (OpenAPI 3.0 specification)

#### Endpoints

**POST /api/{user_id}/conversations**
- **Purpose**: Create a new conversation
- **Auth**: JWT required
- **Request Body**: `{ "title": "Optional title" }`
- **Response**: Conversation object with id
- **Status Codes**: 201 Created, 401 Unauthorized, 403 Forbidden (user_id mismatch)

**GET /api/{user_id}/conversations**
- **Purpose**: List all conversations for user
- **Auth**: JWT required
- **Query Params**: `limit` (default 50), `offset` (default 0)
- **Response**: Array of conversation objects sorted by updated_at desc
- **Status Codes**: 200 OK, 401 Unauthorized

**PATCH /api/{user_id}/conversations/{conversation_id}**
- **Purpose**: Update conversation title
- **Auth**: JWT required
- **Request Body**: `{ "title": "New title" }`
- **Response**: Updated conversation object
- **Status Codes**: 200 OK, 401 Unauthorized, 404 Not Found

**GET /api/{user_id}/conversations/{conversation_id}/messages**
- **Purpose**: Get messages for a conversation
- **Auth**: JWT required
- **Query Params**: `limit` (default 50), `offset` (default 0)
- **Response**: Array of message objects sorted by created_at asc
- **Status Codes**: 200 OK, 401 Unauthorized, 404 Not Found

**POST /api/{user_id}/chat**
- **Purpose**: Send a message and get AI response (streaming)
- **Auth**: JWT required
- **Request Body**: `{ "conversation_id": "uuid", "content": "message text" }`
- **Response**: Server-Sent Events stream with AI response chunks
- **Headers**: `Content-Type: text/event-stream`, `Cache-Control: no-cache`
- **Rate Limiting**: 429 Too Many Requests if limits exceeded
- **Status Codes**: 200 OK (streaming), 401 Unauthorized, 429 Too Many Requests, 504 Gateway Timeout (AI timeout)

**File**: `contracts/mcp-tools.md` (MCP Tool Signatures)

#### MCP Tool Functions

**list_tasks(user_id: str) -> List[Dict]**
- **Purpose**: Retrieve all tasks for the authenticated user
- **Docstring**: "Get all tasks for the current user. Use this when the user asks to see their tasks, show their todo list, or list what they need to do. Returns a list of tasks with id, description, is_completed, and created_at fields."
- **Returns**: JSON array of task objects
- **Example**: `[{"id": "uuid", "description": "Buy milk", "is_completed": false, "created_at": "2026-02-07T10:00:00"}]`

**create_task(user_id: str, description: str) -> Dict**
- **Purpose**: Create a new task for the authenticated user
- **Docstring**: "Create a new task for the current user. Use this when the user asks to add a task, create a todo, or remember something. Requires a description of what needs to be done. Returns the created task object."
- **Parameters**: description (required, max 500 characters)
- **Returns**: JSON object of created task
- **Example**: `{"id": "uuid", "description": "Buy milk", "is_completed": false, "created_at": "2026-02-07T10:00:00"}`

**update_task(user_id: str, task_id: str, description: str = None, is_completed: bool = None) -> Dict**
- **Purpose**: Update an existing task
- **Docstring**: "Update a task's description or completion status. Use this when the user asks to change a task, edit a todo, or mark something as done/undone. IMPORTANT: Always call list_tasks first to get the correct task_id before using this function. Returns the updated task object."
- **Parameters**: task_id (required), description (optional), is_completed (optional)
- **Returns**: JSON object of updated task
- **Example**: `{"id": "uuid", "description": "Buy milk", "is_completed": true, "updated_at": "2026-02-07T11:00:00"}`

**delete_task(user_id: str, task_id: str) -> Dict**
- **Purpose**: Delete a task
- **Docstring**: "Delete a task permanently. Use this when the user explicitly asks to delete or remove a task. IMPORTANT: Always call list_tasks first to get the correct task_id. Returns confirmation of deletion."
- **Parameters**: task_id (required)
- **Returns**: JSON object with success status
- **Example**: `{"success": true, "message": "Task deleted successfully"}`

### Quickstart Guide

**File**: `quickstart.md`

#### For Developers

**Prerequisites**:
- Python 3.11+ and Node.js 18+
- PostgreSQL database (Neon account)
- OpenRouter API key

**Backend Setup**:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Add to .env
GROQ_API_KEY=your_key_here
GROQ_MODEL=openai/gpt-oss-120b:free

python main.py  # Starts on port 8001
```

**Frontend Setup**:
```bash
cd frontend
npm install
npm run dev  # Starts on port 3000
```

**Testing the Chat**:
1. Sign up/login at http://localhost:3000
2. Navigate to /chat
3. Send message: "Add a task to buy milk"
4. Verify task is created and AI responds with confirmation

#### For Users

**Accessing the Chat**:
1. Log in to your account
2. Click "Chat" in the navigation
3. Start typing your message in the input box

**Example Commands**:
- "Add a task to buy groceries"
- "Show me all my tasks"
- "Mark the milk task as complete"
- "Delete the grocery task"

**Tips**:
- You can create multiple conversations to organize different topics
- The AI remembers context within each conversation
- Messages are limited to 2,000 characters
- Rate limit: 20 messages per minute

---

## Phase 2: Task Breakdown

**Note**: Task breakdown is performed by the `/sp.tasks` command, not `/sp.plan`. This plan provides the foundation for task generation.

**Expected Task Categories**:
1. **Database**: Add Conversation and Message models, migrations
2. **Backend API**: Implement chat endpoints, rate limiting, streaming
3. **MCP Integration**: Configure AsyncOpenAI client, register tools
4. **Frontend UI**: Implement ChatKit interface, conversation list, streaming display
5. **Proxy Layer**: Implement Next.js streaming proxy
6. **Testing**: Connection tests, isolation tests, streaming tests, AI logic tests
7. **Documentation**: Update API docs, user guide

---

## Architecture Decisions

### ADR-001: Use OpenRouter Instead of Direct OpenAI API

**Context**: Need AI capabilities for natural language task management

**Decision**: Use OpenRouter as a proxy to access AI models instead of direct OpenAI API

**Rationale**:
- Cost control: OpenRouter offers free tier models (openai/gpt-oss-120b:free)
- Flexibility: Can switch between different AI providers without code changes
- Existing setup: OpenRouter integration already partially implemented

**Consequences**:
- Positive: Zero AI service costs during development and testing
- Positive: Easy to upgrade to paid models later
- Negative: Dependency on OpenRouter service availability
- Negative: Windows DNS resolution issues (workaround: use synchronous requests with asyncio.to_thread)

**Alternatives Considered**:
- Direct OpenAI API: Higher cost, requires payment setup
- Local LLM: Insufficient quality for task interpretation, high resource requirements

### ADR-002: Stateless Agent with Full History Loading

**Context**: Need to maintain conversation context for AI responses

**Decision**: Load last 15 messages from database into agent context for every request (stateless agent)

**Rationale**:
- Simplicity: No need to maintain agent state between requests
- Reliability: Each request is independent, no state corruption issues
- Scalability: Easier to scale horizontally without session affinity
- Cost control: Limited context window (15 messages) controls token costs

**Consequences**:
- Positive: Simple implementation, no state management complexity
- Positive: Automatic recovery from errors (no corrupted state)
- Negative: Database query on every message (mitigated by indexing)
- Negative: Repeated context loading (acceptable for 15 messages)

**Alternatives Considered**:
- Stateful agent with in-memory context: Complex state management, scaling challenges
- Redis-cached context: Additional infrastructure, cache invalidation complexity

### ADR-003: JSON Format for MCP Tool Returns

**Context**: AI needs to parse task data from MCP tool responses

**Decision**: Return structured JSON objects from all MCP tools instead of plain text

**Rationale**:
- Parsing reliability: JSON is unambiguous and machine-readable
- Consistency: All tools return the same format
- Extensibility: Easy to add new fields without breaking parsing
- AI compatibility: Modern LLMs handle JSON well

**Consequences**:
- Positive: Reliable data extraction by AI
- Positive: Consistent error handling
- Positive: Easy to validate and test
- Negative: Slightly more verbose than plain text (acceptable tradeoff)

**Alternatives Considered**:
- Plain text responses: Ambiguous, parsing errors, hard to extend
- XML format: More verbose, less common in modern APIs

### ADR-004: Server-Sent Events for Streaming

**Context**: Need to stream AI responses to frontend in real-time

**Decision**: Use Server-Sent Events (SSE) with text/event-stream content type

**Rationale**:
- Native browser support: No additional libraries needed
- Unidirectional: Matches our use case (server to client only)
- Simple protocol: Easy to implement and debug
- Next.js compatibility: Well-supported in App Router

**Consequences**:
- Positive: Simple implementation, native browser support
- Positive: Automatic reconnection handling
- Positive: Works with standard HTTP/HTTPS
- Negative: Unidirectional only (acceptable for our use case)

**Alternatives Considered**:
- WebSockets: Bidirectional (overkill), more complex setup
- Long polling: Inefficient, higher latency
- HTTP/2 Server Push: Limited browser support, being deprecated

---

## Risk Assessment

### High Priority Risks

**R1: Windows DNS Resolution Issue**
- **Impact**: High - Blocks local development on Windows
- **Probability**: High - Already observed
- **Mitigation**: Use synchronous requests with asyncio.to_thread(), document Linux deployment requirement
- **Contingency**: Deploy to Linux environment early, use Docker for local development

**R2: AI Hallucinating Task IDs**
- **Impact**: Medium - Could cause incorrect task operations
- **Probability**: Medium - Common LLM behavior
- **Mitigation**: Force AI to call list_tasks before update/delete operations via tool docstrings
- **Contingency**: Add validation layer to verify task_id exists before operations

**R3: Rate Limiting Bypass**
- **Impact**: High - Could lead to excessive costs
- **Probability**: Low - If implementation has bugs
- **Mitigation**: Thorough testing of rate limiting logic, monitoring in production
- **Contingency**: Add global rate limit as fallback, implement cost alerts

### Medium Priority Risks

**R4: Streaming Buffering Issues**
- **Impact**: Medium - Poor user experience
- **Probability**: Medium - Next.js 16.1.2 is new
- **Mitigation**: Use Context7 to verify correct headers, test thoroughly
- **Contingency**: Fall back to non-streaming responses if needed

**R5: Context Window Insufficient**
- **Impact**: Medium - AI loses important context
- **Probability**: Low - 15 messages should be sufficient
- **Mitigation**: Monitor user feedback, adjust if needed
- **Contingency**: Implement dynamic context window based on token count

### Low Priority Risks

**R6: OpenRouter Service Downtime**
- **Impact**: High - Feature completely unavailable
- **Probability**: Low - OpenRouter has good uptime
- **Mitigation**: Implement proper error handling, retry logic
- **Contingency**: Display clear error message, allow retry

---

## Success Metrics

### Implementation Success
- ✅ All constitution gates passed
- ✅ All functional requirements (FR-001 through FR-022) implemented
- ✅ All acceptance scenarios from user stories pass
- ✅ Zero manual code edits (agentic development)

### Performance Success
- ✅ Streaming starts within 1 second (SC-005)
- ✅ Task creation completes within 10 seconds (SC-001)
- ✅ Conversation history loads within 2 seconds (SC-004)
- ✅ 100 concurrent users supported (SC-006)

### Quality Success
- ✅ 95% AI interpretation accuracy (SC-003)
- ✅ 90% first-attempt success rate (SC-009)
- ✅ 99.9% data persistence reliability (SC-010)
- ✅ Zero user data leakage (SC-007)

### User Experience Success
- ✅ Context maintained across 20+ messages (SC-002)
- ✅ Multiple conversations manageable (SC-008)
- ✅ Clear error messages for all failure scenarios
- ✅ Responsive UI on desktop and mobile

---

## Next Steps

1. **Complete Phase 0**: Run research tasks to resolve all NEEDS CLARIFICATION items
2. **Complete Phase 1**: Generate data-model.md, contracts/, and quickstart.md
3. **Update Agent Context**: Run update-agent-context.ps1 to add new technologies
4. **Generate Tasks**: Run `/sp.tasks` to create detailed implementation tasks
5. **Begin Implementation**: Execute tasks in priority order (P1 → P2 → P3)

**Command to proceed**: `/sp.tasks` (after this plan is approved)
