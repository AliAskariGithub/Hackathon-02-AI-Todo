# Tasks: AI Chatbot & Persistence

**Input**: Design documents from `/specs/001-ai-chatbot-persistence/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `- [ ] [ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/src/` for source code, `backend/tests/` for tests
- **Frontend**: `frontend/src/` for source code, `frontend/tests/` for tests
- Web application structure with separate backend and frontend services

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and environment configuration

- [x] T001 Add GROQ_API_KEY and GROQ_MODEL to backend/.env file
- [x] T002 Add AsyncOpenAI dependency to backend/requirements.txt
- [x] T003 [P] Install OpenAI ChatKit dependency in frontend/package.json
- [x] T004 [P] Create backend/src/utils/ directory for utility modules
- [x] T005 [P] Create backend/src/mcp/agents/ directory for agent configuration
- [x] T006 [P] Create backend/src/mcp/runners/ directory for agent execution logic
- [x] T007 [P] Create frontend/src/app/chat/ directory for chat pages
- [x] T008 [P] Create frontend/src/components/chat/ directory for chat components
- [x] T009 [P] Create frontend/src/hooks/ directory for custom hooks
- [x] T010 [P] Create frontend/src/lib/chat-api.ts file for API client

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T011 [P] Create Conversation model with SQLModel in backend/src/models/conversation.py
- [x] T012 [P] Create Message model with SQLModel in backend/src/models/message.py
- [x] T013 Create Alembic migration for conversations and messages tables in backend/alembic/versions/
- [x] T014 Run Alembic migration to create database tables
- [x] T015 [P] Implement ChatService for conversation/message CRUD in backend/src/services/chat_service.py
- [x] T016 [P] Implement RateLimitService for per-user rate limiting in backend/src/services/rate_limit_service.py
- [x] T017 [P] Configure AsyncOpenAI client for OpenRouter in backend/src/utils/openrouter_client.py
- [x] T018 [P] Implement context builder to load last 15 messages in backend/src/utils/context_builder.py
- [x] T019 Create chat router with JWT middleware in backend/src/api/routers/chat.py
- [x] T020 Register chat router in backend main.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Natural Language Task Management (Priority: P1) 🎯 MVP

**Goal**: Enable users to manage tasks through natural language commands in a conversational interface

**Independent Test**: Send message "Add a task to buy milk" and verify task is created and AI responds with confirmation

### Implementation for User Story 1

- [x] T021 [P] [US1] Update MCP tool docstrings in backend/src/mcp/tools/task_tools.py to include clear usage instructions
- [x] T022 [P] [US1] Ensure MCP tools return JSON format in backend/src/mcp/tools/task_tools.py
- [x] T023 [US1] Configure todo agent with OpenRouter client in backend/src/mcp/agents/todo_agent.py
- [x] T024 [US1] Register MCP tools with agent in backend/src/mcp/agents/todo_agent.py
- [x] T025 [US1] Implement agent runner with user_id injection in backend/src/mcp/runners/task_runner.py
- [x] T026 [US1] Implement POST /api/{user_id}/chat endpoint with agent execution in backend/src/api/routers/chat.py
- [x] T027 [US1] Add rate limiting middleware to chat endpoint in backend/src/api/routers/chat.py
- [x] T028 [US1] Add 30-second timeout to AI service calls in backend/src/mcp/runners/task_runner.py
- [x] T029 [P] [US1] Create basic ChatInterface component in frontend/src/components/chat/ChatInterface.tsx
- [x] T030 [P] [US1] Create MessageInput component with 2000 char limit in frontend/src/components/chat/MessageInput.tsx
- [x] T031 [P] [US1] Create MessageList component for displaying messages in frontend/src/components/chat/MessageList.tsx
- [x] T032 [US1] Implement useChat hook for chat state management in frontend/src/hooks/useChat.ts
- [x] T033 [US1] Create chat API client functions in frontend/src/lib/chat-api.ts
- [x] T034 [US1] Create chat page at frontend/src/app/chat/page.tsx
- [x] T035 [US1] Add navigation link to chat page in frontend layout

**Checkpoint**: At this point, User Story 1 should be fully functional - users can manage tasks via natural language

---

## Phase 4: User Story 2 - Persistent Conversation History (Priority: P2)

**Goal**: Maintain ongoing conversations across sessions with context preservation

**Independent Test**: Start conversation, close browser, reopen, and verify conversation history is preserved

### Implementation for User Story 2

- [x] T036 [P] [US2] Implement POST /api/{user_id}/conversations endpoint in backend/src/api/routers/chat.py
- [x] T037 [P] [US2] Implement GET /api/{user_id}/conversations endpoint in backend/src/api/routers/chat.py
- [x] T038 [P] [US2] Implement GET /api/{user_id}/conversations/{conversation_id}/messages endpoint in backend/src/api/routers/chat.py
- [x] T039 [US2] Update chat endpoint to save user messages to database in backend/src/api/routers/chat.py
- [x] T040 [US2] Update chat endpoint to save assistant responses to database in backend/src/api/routers/chat.py
- [x] T041 [US2] Update agent runner to load last 15 messages as context in backend/src/mcp/runners/task_runner.py
- [x] T042 [US2] Update conversation updated_at timestamp when messages added in backend/src/services/chat_service.py
- [x] T043 [P] [US2] Implement useConversations hook for conversation list management in frontend/src/hooks/useConversations.ts
- [x] T044 [P] [US2] Update chat API client to fetch conversation history in frontend/src/lib/chat-api.ts
- [x] T045 [US2] Update ChatInterface to load and display conversation history in frontend/src/components/chat/ChatInterface.tsx
- [x] T046 [US2] Update MessageList to display messages in chronological order in frontend/src/components/chat/MessageList.tsx
- [x] T047 [US2] Add pagination support for message history in frontend/src/components/chat/MessageList.tsx

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - tasks manageable via chat with persistent history

---

## Phase 5: User Story 3 - Real-Time Streaming Responses (Priority: P2)

**Goal**: Stream AI responses in real-time for better user experience and perceived performance

**Independent Test**: Send message and observe response appearing progressively rather than all at once

### Implementation for User Story 3

- [x] T048 [US3] Update chat endpoint to return Server-Sent Events stream in backend/src/api/routers/chat.py
- [x] T049 [US3] Set correct SSE headers (Content-Type: text/event-stream) in backend/src/api/routers/chat.py
- [x] T050 [US3] Stream agent response chunks as SSE events in backend/src/mcp/runners/task_runner.py
- [x] T051 [US3] Handle streaming errors and timeouts gracefully in backend/src/mcp/runners/task_runner.py
- [x] T052 [US3] Create Next.js streaming proxy at frontend/src/app/api/chat/route.ts
- [x] T053 [US3] Configure proxy headers for SSE streaming in frontend/src/app/api/chat/route.ts
- [x] T054 [US3] Forward JWT token from frontend to backend in frontend/src/app/api/chat/route.ts
- [x] T055 [US3] Update useChat hook to handle streaming responses in frontend/src/hooks/useChat.ts
- [x] T056 [US3] Update MessageList to display streaming text progressively in frontend/src/components/chat/MessageList.tsx
- [x] T057 [US3] Add typing indicator while AI is responding in frontend/src/components/chat/MessageList.tsx
- [x] T058 [US3] Handle network interruptions during streaming in frontend/src/hooks/useChat.ts

**Checkpoint**: All core functionality complete - tasks manageable via chat with persistent history and streaming responses

---

## Phase 6: User Story 4 - Multi-Conversation Management (Priority: P3)

**Goal**: Allow users to create and manage multiple separate conversation threads

**Independent Test**: Create two conversations, add different tasks in each, verify independent context

### Implementation for User Story 4

- [x] T059 [P] [US4] Implement PATCH /api/{user_id}/conversations/{conversation_id} endpoint in backend/src/api/routers/chat.py
- [x] T060 [P] [US4] Create ConversationList component in frontend/src/components/chat/ConversationList.tsx
- [x] T061 [US4] Update useConversations hook to support create/rename operations in frontend/src/hooks/useConversations.ts
- [x] T062 [US4] Add "New Conversation" button to chat interface in frontend/src/components/chat/ChatInterface.tsx
- [x] T063 [US4] Add conversation list sidebar to chat page in frontend/src/app/chat/page.tsx
- [x] T064 [US4] Implement conversation switching logic in frontend/src/components/chat/ChatInterface.tsx
- [x] T065 [US4] Display conversation titles and last message timestamps in frontend/src/components/chat/ConversationList.tsx
- [x] T066 [US4] Add rename conversation functionality in frontend/src/components/chat/ConversationList.tsx
- [x] T067 [US4] Create specific conversation view at frontend/src/app/chat/[conversationId]/page.tsx
- [x] T068 [US4] Ensure context switches correctly between conversations in frontend/src/hooks/useChat.ts

**Checkpoint**: All user stories complete - full conversational task management with multi-conversation support

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and production readiness

- [x] T069 [P] Add comprehensive error messages for all failure scenarios in backend/src/api/routers/chat.py
- [x] T070 [P] Add loading states and skeleton screens in frontend/src/components/chat/ChatInterface.tsx
- [x] T071 [P] Apply Boldonse/Montserrat fonts and #0FFF50 accent color in frontend/src/app/chat/page.tsx
- [x] T072 [P] Ensure responsive design for mobile devices in frontend/src/components/chat/
- [x] T073 [P] Add confirmation dialog for destructive actions in frontend/src/components/chat/MessageList.tsx
- [x] T074 [P] Implement Windows DNS workaround with asyncio.to_thread() in backend/src/utils/openrouter_client.py
- [x] T075 [P] Add logging for all chat operations in backend/src/api/routers/chat.py
- [x] T076 [P] Add monitoring for rate limit violations in backend/src/services/rate_limit_service.py
- [x] T077 Update API documentation with chat endpoints in backend/docs/
- [ ] T078 Test all quickstart.md scenarios to ensure accuracy (Manual testing required - see TESTING_GUIDE.md)
- [ ] T079 Verify all acceptance scenarios from spec.md pass (Manual testing required - see TESTING_GUIDE.md)
- [ ] T080 Performance test with 100 concurrent users (Load testing infrastructure required - see TESTING_GUIDE.md)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P2 → P3)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Extends US1 but independently testable
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - Enhances US1/US2 but independently testable
- **User Story 4 (P3)**: Can start after Foundational (Phase 2) - Builds on US2 but independently testable

### Within Each User Story

- Models before services (T011-T012 before T015)
- Services before endpoints (T015-T016 before T019)
- Backend endpoints before frontend integration (T026 before T029-T035)
- Core implementation before enhancements (US1 before US3 streaming)

### Parallel Opportunities

**Setup Phase (Phase 1)**:
- All tasks marked [P] can run in parallel (T003-T010)

**Foundational Phase (Phase 2)**:
- Models can run in parallel (T011, T012)
- Services can run in parallel after models (T015, T016, T017, T018)

**User Story 1 (Phase 3)**:
- MCP tool updates and agent config can run in parallel (T021, T022)
- Frontend components can run in parallel (T029, T030, T031)

**User Story 2 (Phase 4)**:
- All GET endpoints can run in parallel (T036, T037, T038)
- Frontend hooks and API client can run in parallel (T043, T044)

**User Story 3 (Phase 5)**:
- Backend streaming and frontend proxy can be developed in parallel

**User Story 4 (Phase 6)**:
- Backend endpoint and frontend components can run in parallel (T059, T060)

**Polish Phase (Phase 7)**:
- All tasks marked [P] can run in parallel (T069-T076)

**Cross-Story Parallelization**:
- Once Foundational phase completes, different team members can work on different user stories simultaneously

---

## Parallel Example: User Story 1

```bash
# Launch MCP tool updates together:
Task T021: "Update MCP tool docstrings in backend/src/mcp/tools/task_tools.py"
Task T022: "Ensure MCP tools return JSON format in backend/src/mcp/tools/task_tools.py"

# Launch frontend components together:
Task T029: "Create basic ChatInterface component in frontend/src/components/chat/ChatInterface.tsx"
Task T030: "Create MessageInput component in frontend/src/components/chat/MessageInput.tsx"
Task T031: "Create MessageList component in frontend/src/components/chat/MessageList.tsx"
```

---

## Parallel Example: Foundational Phase

```bash
# Launch models together:
Task T011: "Create Conversation model in backend/src/models/conversation.py"
Task T012: "Create Message model in backend/src/models/message.py"

# After models complete, launch services together:
Task T015: "Implement ChatService in backend/src/services/chat_service.py"
Task T016: "Implement RateLimitService in backend/src/services/rate_limit_service.py"
Task T017: "Configure AsyncOpenAI client in backend/src/utils/openrouter_client.py"
Task T018: "Implement context builder in backend/src/utils/context_builder.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T010)
2. Complete Phase 2: Foundational (T011-T020) - CRITICAL
3. Complete Phase 3: User Story 1 (T021-T035)
4. **STOP and VALIDATE**: Test natural language task management independently
5. Deploy/demo if ready

**MVP Deliverable**: Users can manage tasks through natural language chat interface

---

### Incremental Delivery

1. **Foundation** (Phase 1-2): Setup + Core infrastructure → Database and services ready
2. **MVP** (Phase 3): User Story 1 → Test independently → Deploy/Demo
   - Value: Natural language task management
3. **Enhancement 1** (Phase 4): User Story 2 → Test independently → Deploy/Demo
   - Value: Persistent conversation history across sessions
4. **Enhancement 2** (Phase 5): User Story 3 → Test independently → Deploy/Demo
   - Value: Real-time streaming responses for better UX
5. **Enhancement 3** (Phase 6): User Story 4 → Test independently → Deploy/Demo
   - Value: Multi-conversation organization
6. **Production Ready** (Phase 7): Polish → Final testing → Production deployment

Each phase adds value without breaking previous functionality.

---

### Parallel Team Strategy

With multiple developers:

1. **Team completes Setup + Foundational together** (Phase 1-2)
2. **Once Foundational is done, parallelize user stories**:
   - Developer A: User Story 1 (T021-T035)
   - Developer B: User Story 2 (T036-T047)
   - Developer C: User Story 3 (T048-T058)
3. **Stories complete and integrate independently**
4. **Team completes User Story 4 together** (T059-T068)
5. **Team completes Polish together** (T069-T080)

---

## Notes

- **[P] tasks**: Different files, no dependencies - can run in parallel
- **[Story] label**: Maps task to specific user story for traceability
- **Each user story**: Independently completable and testable
- **Commit strategy**: Commit after each task or logical group
- **Validation checkpoints**: Stop at any checkpoint to validate story independently
- **No tests included**: Tests not explicitly requested in specification
- **Windows DNS issue**: Addressed in T074 with asyncio.to_thread() workaround
- **Rate limiting**: Enforced at API level (T027) with monitoring (T076)
- **Security**: User ID injection in agent runner (T025) prevents cross-user access
- **Context window**: Limited to 15 messages (T041) for cost control
- **Streaming**: SSE implementation (T048-T058) for real-time responses

---

## Total Task Count

- **Phase 1 (Setup)**: 10 tasks
- **Phase 2 (Foundational)**: 10 tasks (BLOCKING)
- **Phase 3 (US1 - MVP)**: 15 tasks
- **Phase 4 (US2)**: 12 tasks
- **Phase 5 (US3)**: 11 tasks
- **Phase 6 (US4)**: 10 tasks
- **Phase 7 (Polish)**: 12 tasks

**Total**: 80 tasks

**Parallel Opportunities**: 35 tasks marked [P] can run in parallel within their phase

**MVP Scope**: 35 tasks (Phase 1 + Phase 2 + Phase 3)
