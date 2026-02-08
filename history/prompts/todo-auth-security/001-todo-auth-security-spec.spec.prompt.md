---
id: 1
title: todo-auth-security-spec
stage: spec
date: 2026-02-02
surface: agent
model: claude-sonnet-4-5-20250929
feature: auth-security
branch: 002-todo-auth-security
user: Dell
command: /sp.specify
labels: ["auth", "security", "jwt", "specification", "api-security"]
links:
  spec: specs/002-todo-auth-security/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/002-todo-auth-security/spec.md
 - specs/002-todo-auth-security/checklists/requirements.md
tests:
 - none
---

## Prompt

Todo Full-Stack Web Application - Spec 2: Auth System & API Security

Target functionality:
- Integrate Better Auth into the Next.js frontend to handle user lifecycle (Signup/Signin).
- Configure Better Auth JWT plugin to issue verifiable tokens.
- Implement a JWT verification middleware in FastAPI.
- Secure all existing CRUD endpoints to require a valid Bearer token.

Focus:
- Shared Secret synchronization between Next.js and FastAPI.
- Middleware logic: Extracting the `sub` (User ID) from the JWT.
- Contextual filtering: Ensuring the `user_id` in the URL matches the `user_id` in the JWT.

Success criteria:
- Unauthorized requests (missing or invalid token) return 401 Unauthorized.
- Successful login on frontend generates a JWT stored in local state/cookies.
- Backend correctly decodes JWT using the shared `BETTER_AUTH_SECRET`.
- Logic test: User A attempts to access `/api/user_B/tasks` and receives a 403 Forbidden or 401 Unauthorized.

Constraints:
- Documentation: Use Context7 MCP to fetch the latest "Better Auth JWT Plugin" implementation details.
- Security: Secrets must never be hardcoded; use `BETTER_AUTH_SECRET` environment variable.
- Technology: Better Auth (Frontend), FastAPI-Users or custom Jose/PyJWT implementation (Backend).

Not building:
- Final UI styling for the dashboard (handled in Spec 3).
- Password reset via email flow (MVP focuses on Signup/Signin).
- Social login (OAuth) providers (sticking to email/password for the hackathon MVP).

## Response snapshot

Successfully created feature specification for authentication and API security. Generated comprehensive spec.md file covering user scenarios, functional requirements, key entities, and success criteria. Created validation checklist and ensured all [NEEDS CLARIFICATION] markers were resolved.

## Outcome

- ✅ Impact: Created complete specification for auth system integration with JWT security and API protection
- 🧪 Tests: none
- 📁 Files: specs/002-todo-auth-security/spec.md, specs/002-todo-auth-security/checklists/requirements.md
- 🔁 Next prompts: /sp.clarify or /sp.plan for implementation planning
- 🧠 Reflection: Balancing security requirements with user experience needs in authentication design

## Evaluation notes (flywheel)

- Failure modes observed: PowerShell script not available in environment, had to manually create branch and spec
- Graders run and results (PASS/FAIL): PASS - all validation checklist items completed
- Prompt variant (if applicable):
- Next experiment (smallest change to try): Automate branch creation process when PowerShell unavailable