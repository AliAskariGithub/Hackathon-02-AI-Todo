---
id: 2
title: todo-chatkit-persistence-plan
stage: plan
date: 2026-02-06
surface: agent
model: claude-sonnet-4-5-20250929
feature: todo-chatkit-persistence
branch: 007-todo-chatkit-persistence
user: Claude User
command: "/sp.plan Spec 7: ChatKit UI & Persistence\\n\\nCreate:\\n- **Session Bridge:** Implement a `ChatKitServer` in FastAPI that uses `OpenAIConversationsSession` (or a custom `SQLModelSession`) to map `conversation_id` to Neon DB records.\\n- **Frontend Integration:** - Mount the `@openai/chatkit-react` component in a new `/chat` route.\\n    - Implement the `useChatKit` hook to connect to the `/api/chatkit/session` endpoint.\\n- **Stateless Persistence:** Logic to fetch/store `Message` and `Conversation` models using SQLModel before and after the Agent run.\\n- **Proxy Configuration:** Update `proxy.ts` (Next.js 16.1.2) to handle the network boundary and streaming headers for the chat endpoint.\\n\\nDecisions needing documentation:\\n- **Streaming vs. Buffer:** Strategy for handling \"Thinking\" states (Recommended: Enable streaming to allow ChatKit to show real-time tool-invocation logs).\\n- **Session Management:** Using `BETTER_AUTH_SECRET` to ensure the `user` parameter in the ChatKit session is cryptographically tied to the logged-in user.\\n- **Widget Selection:** Choosing between standard text bubbles and Shadcn-themed \"Task Cards\" for tool results.\\n\\nTesting strategy:\\n- **Memory Test:** Send a message, refresh the browser, and verify the `conversation_id` persists the history via ChatKit's history API.\\n- **Security Check:** Attempt to access a `conversation_id` belonging to a different `user_id` (Verify 403 Forbidden).\\n- **Tool UI:** Verify that `add_task` calls show a \"Success\" badge or widget in the chat flow.\\n\\nTechnical details:\\n- Use Context7 MCP to confirm the `proxy.ts` export syntax for Next.js 16.1.2.\\n- Backend: Use `openai.chatkit.sessions.create` to generate the `client_secret` for the frontend.\\n- Database: Ensure `created_at` timestamps are synced to prevent \"out of order\" message rendering.\\n- Phases: DB Model Implementation -> FastAPI Session Logic -> Next.js Proxy Setup -> ChatKit UI Polishing."
labels: ["plan", "chatkit", "persistence", "ai", "mcp"]
links:
  spec: ../../specs/007-todo-chatkit-persistence/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/007-todo-chatkit-persistence/plan.md
  - specs/007-todo-chatkit-persistence/research.md
  - specs/007-todo-chatkit-persistence/data-model.md
  - specs/007-todo-chatkit-persistence/contracts/conversation-openapi.yaml
  - specs/007-todo-chatkit-persistence/quickstart.md
  - .specify/memory/agent-context.md
tests:
  - specs/007-todo-chatkit-persistence/research.md
  - specs/007-todo-chatkit-persistence/data-model.md
  - specs/007-todo-chatkit-persistence/contracts/conversation-openapi.yaml
---

## Prompt

Spec 7: ChatKit UI & Persistence

Create:
- **Session Bridge:** Implement a `ChatKitServer` in FastAPI that uses `OpenAIConversationsSession` (or a custom `SQLModelSession`) to map `conversation_id` to Neon DB records.
- **Frontend Integration:** - Mount the `@openai/chatkit-react` component in a new `/chat` route.
    - Implement the `useChatKit` hook to connect to the `/api/chatkit/session` endpoint.
- **Stateless Persistence:** Logic to fetch/store `Message` and `Conversation` models using SQLModel before and after the Agent run.
- **Proxy Configuration:** Update `proxy.ts` (Next.js 16.1.2) to handle the network boundary and streaming headers for the chat endpoint.

Decisions needing documentation:
- **Streaming vs. Buffer:** Strategy for handling "Thinking" states (Recommended: Enable streaming to allow ChatKit to show real-time tool-invocation logs).
- **Session Management:** Using `BETTER_AUTH_SECRET` to ensure the `user` parameter in the ChatKit session is cryptographically tied to the logged-in user.
- **Widget Selection:** Choosing between standard text bubbles and Shadcn-themed "Task Cards" for tool results.

Testing strategy:
- **Memory Test:** Send a message, refresh the browser, and verify the `conversation_id` persists the history via ChatKit's history API.
- **Security Check:** Attempt to access a `conversation_id` belonging to a different `user_id` (Verify 403 Forbidden).
- **Tool UI:** Verify that `add_task` calls show a "Success" badge or widget in the chat flow.

Technical details:
- Use Context7 MCP to confirm the `proxy.ts` export syntax for Next.js 16.1.2.
- Backend: Use `openai.chatkit.sessions.create` to generate the `client_secret` for the frontend.
- Database: Ensure `created_at` timestamps are synced to prevent "out of order" message rendering.
- Phases: DB Model Implementation -> FastAPI Session Logic -> Next.js Proxy Setup -> ChatKit UI Polishing.

## Response snapshot

Successfully created comprehensive implementation plan for the ChatKit UI & Persistence feature (007-todo-chatkit-persistence). The plan includes:

1. **Technical Context**: Analysis of current state and target architecture
2. **Constitution Check**: Verification of compliance with project principles
3. **Research Phase**: Resolved all unknowns including Next.js proxy configuration, ChatKit session integration, MCP tool integration patterns, and JWT authentication
4. **Data Model Design**: Defined Conversation and Message entities with proper relationships and validation
5. **API Contract**: Complete OpenAPI specification for all MCP and conversation endpoints
6. **Architecture**: Session bridge implementation, frontend integration patterns, persistence logic, and streaming configuration
7. **Security Model**: User isolation and authentication enforcement
8. **Quickstart Guide**: How-to for developers to run and use the feature

The plan addresses all core requirements including persistent chat history, MCP tool integration with visual feedback, and proper authentication context.

## Outcome

- ✅ Impact: Complete architecture plan for MCP integration with persistent chat functionality
- 🧪 Tests: Testing strategy defined with memory, security, and UI validation
- 📁 Files: Created plan.md, research.md, data-model.md, contracts/conversation-openapi.yaml, quickstart.md, updated agent-context.md
- 🔁 Next prompts: Ready for `/sp.tasks` to generate implementation tasks
- 🧠 Reflection: Plan addresses all core requirements with proper security and async handling

## Evaluation notes (flywheel)

- Failure modes observed: None - all technical requirements addressed with proper error handling
- Graders run and results (PASS/FAIL): PASS - Plan aligns with specification and follows project constitution
- Prompt variant (if applicable): Original requirements implemented as specified
- Next experiment (smallest change to try): Generate tasks from this plan with `/sp.tasks`