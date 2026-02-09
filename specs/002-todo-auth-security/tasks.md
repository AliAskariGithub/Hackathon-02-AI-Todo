---
description: "Task list for auth system and API security implementation"
---

# Tasks: Todo App Authentication & API Security

**Input**: Design documents from `/specs/002-todo-auth-security/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: The examples below include test tasks. Tests are OPTIONAL - only include them if explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create backend and frontend project structures per implementation plan
- [X] T002 Install Better Auth and JWT dependencies in frontend
- [X] T003 [P] Install PyJWT and FastAPI dependencies in backend
- [X] T004 [P] Configure shared BETTER_AUTH_SECRET environment variables

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 Configure Better Auth with JWT plugin in frontend/lib/auth.ts
- [X] T006 [P] Implement JWT verification middleware in backend/src/api/middleware/auth.py
- [X] T007 [P] Create JWT token extraction utility in backend/src/utils/jwt.py
- [X] T008 Create authentication dependency for FastAPI in backend/src/api/deps.py
- [X] T009 Configure CORS settings for frontend/backend communication

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Secure User Registration and Login (Priority: P1) 🎯 MVP

**Goal**: Enable users to register and login securely, receiving JWT tokens for authentication

**Independent Test**: Can be fully tested by registering a new user account, logging in, and verifying that the user receives a valid authentication token that grants access to their protected resources.

### Tests for User Story 1 (OPTIONAL - only if tests requested) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T010 [P] [US1] Contract test for signup endpoint in backend/tests/contract/test_auth.py
- [ ] T011 [P] [US1] Contract test for login endpoint in backend/tests/contract/test_auth.py

### Implementation for User Story 1

- [X] T012 [P] [US1] Create auth API routes in frontend/app/api/auth/route.ts
- [X] T013 [US1] Implement signup functionality in frontend/components/Auth/SignupForm.tsx
- [X] T014 [US1] Implement login functionality in frontend/components/Auth/LoginForm.tsx
- [X] T015 [US1] Handle JWT token storage from Better Auth in frontend/services/auth-service.ts
- [X] T016 [US1] Create authentication context in frontend/contexts/auth-context.tsx

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Secure Access to Personal Todo Lists (Priority: P1)

**Goal**: Allow authenticated users to access only their own todo lists and tasks, preventing unauthorized access to other users' data

**Independent Test**: Can be fully tested by having two users create accounts, logging in with one user's token, and attempting to access both users' data to ensure proper access controls are enforced.

### Tests for User Story 2 (OPTIONAL - only if tests requested) ⚠️

- [ ] T017 [P] [US2] Contract test for user-specific tasks endpoint in backend/tests/contract/test_tasks.py
- [ ] T018 [P] [US2] Integration test for user data isolation in backend/tests/integration/test_user_isolation.py

### Implementation for User Story 2

- [ ] T019 [P] [US2] Update task model to include user_id in backend/src/models/task.py
- [ ] T020 [US2] Implement user-specific task retrieval in backend/src/services/task_service.py
- [X] T021 [US2] Add JWT sub claim validation to task endpoints in backend/src/api/routers/tasks.py
- [X] T022 [US2] Update frontend to include user context in task API calls in frontend/services/task-service.ts
- [X] T023 [US2] Implement user ID comparison logic in JWT validation dependency

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Protected API Endpoints (Priority: P2)

**Goal**: Secure all existing CRUD endpoints to require authentication and reject unauthorized requests

**Independent Test**: Can be fully tested by attempting to access protected endpoints with and without valid authentication tokens to ensure proper access control.

### Tests for User Story 3 (OPTIONAL - only if tests requested) ⚠️

- [ ] T024 [P] [US3] Contract test for unauthorized access in backend/tests/contract/test_auth_protection.py
- [ ] T025 [P] [US3] Integration test for endpoint protection in backend/tests/integration/test_endpoint_security.py

### Implementation for User Story 3

- [X] T026 [P] [US3] Apply JWT dependency to all existing task endpoints in backend/src/api/routers/tasks.py
- [X] T027 [US3] Implement 401 Unauthorized response for missing tokens in backend/src/api/deps.py
- [X] T028 [US3] Implement 403 Forbidden response for user mismatch in backend/src/api/deps.py
- [X] T029 [US3] Add error handling for expired tokens in backend/src/api/deps.py
- [X] T030 [US3] Update frontend to handle authentication errors gracefully in frontend/services/api-client.ts

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T031 [P] Update documentation in docs/authentication.md
- [X] T032 Code cleanup and refactoring of authentication components
- [X] T033 Security hardening review of JWT implementation
- [X] T034 [P] Add comprehensive error logging in backend/src/utils/logging_config.py
- [X] T035 Run quickstart validation from specs/002-todo-auth-security/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (if tests requested):
Task: "Contract test for signup endpoint in backend/tests/contract/test_auth.py"
Task: "Contract test for login endpoint in backend/tests/contract/test_auth.py"

# Launch all models for User Story 1 together:
Task: "Create auth API routes in frontend/pages/api/auth/[...auth].ts"
Task: "Implement signup functionality in frontend/components/Auth/SignupForm.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence