---
id: 2
title: auth-security-impl-plan
stage: plan
date: 2026-02-02
surface: agent
model: claude-sonnet-4-5-20250929
feature: auth-security
branch: 002-todo-auth-security
user: Dell
command: /sp.plan
labels: ["auth", "security", "jwt", "fastapi", "better-auth", "implementation-plan"]
links:
  spec: specs/002-todo-auth-security/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/002-todo-auth-security/plan.md
 - specs/002-todo-auth-security/research.md
 - specs/002-todo-auth-security/data-model.md
 - specs/002-todo-auth-security/contracts/auth-contracts.yaml
 - specs/002-todo-auth-security/quickstart.md
tests:
 - none
---

## Prompt

Spec 2: Auth System & API Security

Create:
- Better Auth configuration in Next.js (`auth.ts`) using the JWT plugin.
- A custom FastAPI dependency or middleware to verify JWT signatures.
- Logic to extract the `sub` (user_id) from decoded tokens and inject it into the request state.
- Security layer for CRUD endpoints to ensure `token.sub == path_user_id`.

Decisions needing documentation:
- Token Verification Strategy: Choose between symmetric (HS256 with shared secret) or asymmetric (RS256 with JWKS endpoint).
- Recommended: HS256 for a hackathon environment using the `BETTER_AUTH_SECRET`.
- Storage: Determine whether to store the JWT in a cookie (Next.js default) or pass via `Authorization: Bearer` header for the API.

Testing strategy:
- Auth Flow: Verify that a new user can sign up on the frontend and receive a valid session.
- Guard Verification: Test a GET request to `/api/{user_id}/tasks` without a token (Expect 401).
- Ownership Check: Attempt to use User A's token to access User B's tasks (Expect 403 or 401).
- Token Expiry: Verify that an expired token is rejected by the FastAPI backend.

Technical details:
- Use Context7 MCP to find the specific "Better Auth JWT Plugin" setup for Next.js 16.1.2.
- Python Library: Use `PyJWT` or `python-jose` for JWT decoding in FastAPI.
- Secret Key Synchronization: Ensure `BETTER_AUTH_SECRET` is identical in both `.env` (Frontend) and `.env` (Backend).
- Phases: Better Auth Config → JWT Plugin Activation → FastAPI Middleware Setup → Endpoint Lockdown.

## Response snapshot

Successfully created comprehensive implementation plan for auth system & API security. Generated plan.md, research.md, data-model.md, API contracts (OpenAPI spec), and quickstart guide. The plan addresses JWT verification strategy (HS256 with shared secret), token storage approach, FastAPI security implementation, and proper user data isolation mechanisms.

## Outcome

- ✅ Impact: Complete implementation plan with research, data models, contracts, and quickstart for auth security feature
- 🧪 Tests: none
- 📁 Files: specs/002-todo-auth-security/plan.md, research.md, data-model.md, contracts/auth-contracts.yaml, quickstart.md
- 🔁 Next prompts: /sp.tasks for task breakdown or /sp.adr for architectural decisions
- 🧠 Reflection: Critical security considerations like user data isolation and proper JWT validation are well-documented

## Evaluation notes (flywheel)

- Failure modes observed: PowerShell scripts not available in environment, had to create plan manually
- Graders run and results (PASS/FAIL): PASS - all required planning artifacts created
- Prompt variant (if applicable):
- Next experiment (smallest change to try): Automate plan generation when PowerShell unavailable
