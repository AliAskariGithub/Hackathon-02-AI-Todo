# Implementation Tasks: Advanced Task Management with Dapr Abstraction

**Feature**: 010-dapr-abstraction
**Date**: 2026-02-11
**Status**: Ready for Implementation
**Branch**: 010-dapr-abstraction

## Overview

This document contains implementation tasks for Spec 010: Advanced Logic & Dapr Abstraction. Tasks are organized by user story and follow the Phase-V Event-Driven Architecture principles.

**User Stories**:
- **US1 (P1)**: Recurring Task Automation - Daily/Weekly/Monthly task generation
- **US2 (P2)**: Intelligent Time-Based Reminders - Exact-time notifications via Dapr Jobs API
- **US3 (P3)**: Advanced Search and Filtering - Server-side search with natural language support
- **US4 (P4)**: Multi-Level Priority Management - High/Medium/Low priority system

**Implementation Strategy**: MVP-first approach starting with US1 (Recurring Tasks), followed by US2 (Reminders), US3 (Search), and US4 (Priority Management).

## Task Format

```
- [ ] [TaskID] [P?] [Story?] Description with file path
```

- **TaskID**: Unique identifier (T001, T002, etc.)
- **[P]**: Parallel execution marker (can run concurrently with other [P] tasks)
- **[Story]**: User story label ([US1], [US2], [US3], [US4])
- **File path**: Exact path to file being created/modified

## Phase 1: Project Setup

### Environment & Dependencies

- [ ] [T001] [P] Install Dapr CLI v1.14+ and initialize in Kubernetes mode (`dapr init -k`)
- [X] [T002] [P] Update backend/requirements.txt with Dapr dependencies (dapr==1.14.0, dapr-ext-fastapi==0.2.0)
- [X] [T003] [P] Update frontend/package.json with Next.js 16.1.2 dependencies
- [ ] [T004] Create Kubernetes secret for credentials (`kubectl create secret generic dapr-secrets`)
- [ ] [T005] Verify Dapr installation and component status (`dapr status -k`)

## Phase 2: Foundational Infrastructure (Blocking Prerequisites)

### Dapr Components Configuration

- [X] [T010] Create PostgreSQL State Store component - backend/components/statestore-postgresql.yaml
- [X] [T011] Create Kafka Pub/Sub component (in-memory for local dev) - backend/components/pubsub-kafka.yaml
- [X] [T012] Create Kubernetes Secrets Store component - backend/components/secretstore-kubernetes.yaml
- [ ] [T013] Deploy Dapr components to Kubernetes (`kubectl apply -f backend/components/`)
- [ ] [T014] Verify component connectivity via Dapr sidecar (`curl http://localhost:3500/v1.0/metadata`)

### Event Schema & SDK Utilities

- [X] [T015] [P] Define standardized event schema - backend/src/events/schema.py
- [X] [T016] [P] Create Dapr State API utility functions - backend/src/dapr_sdk_utils/state.py
- [X] [T017] [P] Create Dapr Pub/Sub API utility functions - backend/src/dapr_sdk_utils/pubsub.py
- [X] [T018] [P] Create Dapr Secrets API utility functions - backend/src/dapr_sdk_utils/secrets.py
- [X] [T019] [P] Create Dapr Jobs API utility functions - backend/src/dapr_sdk_utils/jobs.py
- [X] [T020] Create correlation ID middleware for distributed tracing - backend/src/middleware/correlation.py

### Database Migration

- [X] [T021] Create Alembic migration for Task entity with recurrence fields - backend/alembic/versions/xxx_add_task_recurrence.py
- [X] [T022] Create Alembic migration for Reminder entity - backend/alembic/versions/xxx_add_reminder_entity.py
- [X] [T023] Create Alembic migration for Priority and Tag entities - backend/alembic/versions/xxx_add_priority_tag_entities.py
- [ ] [T024] Run migrations and verify schema (`alembic upgrade head`)

## Phase 3: User Story 1 - Recurring Task Automation (P1)

**Acceptance Criteria**:
- Daily tasks auto-generate at midnight
- Weekly tasks auto-generate on specified day of week
- Monthly tasks auto-generate on specified day of month
- Correlation IDs prevent duplicate generation on event replay

### Backend - Data Models

- [X] [T030] [P] [US1] Create Task model with recurrence fields - backend/src/models/task.py
- [X] [T031] [P] [US1] Create RecurrencePattern model with calculation logic - backend/src/models/recurrence.py
- [X] [T032] [P] [US1] Add recurrence validation to Task model (day_of_week for Weekly, day_of_month for Monthly)

### Backend - Business Logic

- [X] [T033] [US1] Implement recurrence date calculation logic (Daily/Weekly/Monthly) - backend/src/services/recurrence_service.py
- [X] [T034] [US1] Create recurring task generation service with idempotency check - backend/src/services/task_generation_service.py
- [X] [T035] [US1] Implement event subscriber for `todo.task.completed` - backend/src/events/subscribers/task_completed.py
- [X] [T036] [US1] Add correlation ID storage and lookup in State Store - backend/src/services/idempotency_service.py

### Backend - API Endpoints

- [X] [T037] [P] [US1] Implement POST /api/tasks with recurrence support - backend/src/api/tasks.py
- [X] [T038] [P] [US1] Implement POST /api/tasks/{task_id}/complete with event publishing - backend/src/api/tasks.py
- [X] [T039] [P] [US1] Implement GET /api/tasks with recurrence filtering - backend/src/api/tasks.py
- [X] [T040] [P] [US1] Implement PATCH /api/tasks/{task_id} with recurrence updates - backend/src/api/tasks.py

### Frontend - UI Components

- [X] [T041] [P] [US1] Create RecurrenceSelector component (Daily/Weekly/Monthly dropdown) - frontend/src/components/tasks/RecurrenceSelector.tsx
- [X] [T042] [P] [US1] Create DayOfWeekPicker component for Weekly recurrence - frontend/src/components/tasks/DayOfWeekPicker.tsx
- [X] [T043] [P] [US1] Create DayOfMonthPicker component for Monthly recurrence - frontend/src/components/tasks/DayOfMonthPicker.tsx
- [X] [T044] [US1] Update TaskForm to include recurrence fields - frontend/src/components/tasks/TaskForm.tsx
- [ ] [T045] [US1] Update TaskList to display recurrence indicator - frontend/src/components/tasks/TaskList.tsx

### Frontend - Service Layer

- [X] [T046] [P] [US1] Create Dapr Service Invocation utility - frontend/src/services/dapr.ts
- [X] [T047] [P] [US1] Update task service to use Dapr sidecar (port 3500) - frontend/src/services/taskService.ts
- [X] [T048] [US1] Add recurrence fields to task creation/update API calls - frontend/src/services/taskService.ts

### Testing

- [ ] [T049] [P] [US1] Unit tests for recurrence date calculation (Daily/Weekly/Monthly) - backend/tests/unit/test_recurrence_service.py
- [ ] [T050] [P] [US1] Unit tests for idempotency service (correlation ID deduplication) - backend/tests/unit/test_idempotency_service.py
- [ ] [T051] [US1] Integration test: Create recurring task and verify event publishing - backend/tests/integration/test_recurring_tasks.py
- [ ] [T052] [US1] Integration test: Complete recurring task and verify next instance generation - backend/tests/integration/test_recurring_tasks.py
- [ ] [T053] [US1] E2E test: Create Daily recurring task via frontend and verify backend state - frontend/tests/e2e/recurring-tasks.spec.ts

**Parallel Execution Example (US1)**:
- T030, T031, T032 (data models) can run in parallel
- T037, T038, T039, T040 (API endpoints) can run in parallel after T033-T036 complete
- T041, T042, T043 (UI components) can run in parallel
- T049, T050 (unit tests) can run in parallel

## Phase 4: User Story 2 - Intelligent Time-Based Reminders (P2)

**Acceptance Criteria**:
- Reminders scheduled via Dapr Jobs API (no polling)
- Exact-time delivery with callback endpoint
- Reminder cancellation deletes Dapr Job
- Reminder status tracking (scheduled/sent/cancelled)

### Backend - Data Models

- [ ] [T060] [US2] Create Reminder model with Dapr Job integration - backend/src/models/reminder.py
- [ ] [T061] [US2] Add reminder validation (scheduled_time must be future, minimum 1 minute ahead)

### Backend - Business Logic

- [ ] [T062] [US2] Implement reminder scheduling service using Dapr Jobs API - backend/src/services/reminder_service.py
- [ ] [T063] [US2] Implement reminder callback handler for Dapr Jobs - backend/src/services/reminder_callback_service.py
- [ ] [T064] [US2] Implement reminder cancellation with Dapr Job deletion - backend/src/services/reminder_service.py
- [ ] [T065] [US2] Add reminder notification logic (publish `todo.reminder.fired` event) - backend/src/events/publishers/reminder_events.py

### Backend - API Endpoints

- [ ] [T066] [P] [US2] Implement POST /api/reminders with Dapr Jobs scheduling - backend/src/api/reminders.py
- [ ] [T067] [P] [US2] Implement GET /api/reminders with filtering (task_id, status) - backend/src/api/reminders.py
- [ ] [T068] [P] [US2] Implement DELETE /api/reminders/{reminder_id} with Job cancellation - backend/src/api/reminders.py
- [ ] [T069] [US2] Implement POST /api/reminders/callback (Dapr Jobs callback endpoint) - backend/src/api/reminders.py

### Frontend - UI Components

- [ ] [T070] [P] [US2] Create ReminderScheduler component (date/time picker) - frontend/src/components/reminders/ReminderScheduler.tsx
- [ ] [T071] [P] [US2] Create ReminderList component with status indicators - frontend/src/components/reminders/ReminderList.tsx
- [ ] [T072] [US2] Update TaskDetail to include reminder scheduling UI - frontend/src/components/tasks/TaskDetail.tsx

### Frontend - Service Layer

- [ ] [T073] [P] [US2] Create reminder service with Dapr Service Invocation - frontend/src/services/reminderService.ts
- [ ] [T074] [US2] Add reminder scheduling/cancellation API calls - frontend/src/services/reminderService.ts

### Testing

- [ ] [T075] [P] [US2] Unit tests for reminder scheduling service - backend/tests/unit/test_reminder_service.py
- [ ] [T076] [P] [US2] Unit tests for reminder callback handler - backend/tests/unit/test_reminder_callback_service.py
- [ ] [T077] [US2] Integration test: Schedule reminder and verify Dapr Job creation - backend/tests/integration/test_reminders.py
- [ ] [T078] [US2] Integration test: Cancel reminder and verify Dapr Job deletion - backend/tests/integration/test_reminders.py
- [ ] [T079] [US2] Mock test: Simulate Dapr Jobs callback and verify event publishing - backend/tests/integration/test_reminder_callback.py

**Parallel Execution Example (US2)**:
- T066, T067, T068 (API endpoints) can run in parallel after T062-T065 complete
- T070, T071 (UI components) can run in parallel
- T075, T076 (unit tests) can run in parallel

## Phase 5: User Story 3 - Advanced Search and Filtering (P3)

**Acceptance Criteria**:
- Server-side keyword search (title/description)
- Multi-criteria filtering (status, priority, tags, due_date)
- Sorting by due_date, priority, created_at, updated_at
- Natural language query parsing for chatbot integration
- Pagination support (limit/offset)

### Backend - Business Logic

- [ ] [T080] [US3] Implement keyword search service with Dapr State Store queries - backend/src/services/search_service.py
- [ ] [T081] [US3] Implement multi-criteria filtering logic (status, priority, tags, due_date) - backend/src/services/filter_service.py
- [ ] [T082] [US3] Implement sorting logic (due_date, priority, created_at, updated_at) - backend/src/services/sort_service.py
- [ ] [T083] [US3] Implement natural language query parser (extract filters from text) - backend/src/services/nlp_query_service.py
- [ ] [T084] [US3] Implement pagination logic with limit/offset - backend/src/services/pagination_service.py

### Backend - API Endpoints

- [ ] [T085] [P] [US3] Implement GET /api/search/tasks with query parameters - backend/src/api/search.py
- [ ] [T086] [P] [US3] Implement POST /api/search/natural-language with query parsing - backend/src/api/search.py
- [ ] [T087] [P] [US3] Implement GET /api/search/tags (list unique user tags) - backend/src/api/search.py

### Frontend - UI Components

- [ ] [T088] [P] [US3] Create SearchBar component with keyword input - frontend/src/components/search/SearchBar.tsx
- [ ] [T089] [P] [US3] Create FilterPanel component (status, priority, tags, due_date) - frontend/src/components/search/FilterPanel.tsx
- [ ] [T090] [P] [US3] Create SortSelector component (due_date, priority, created_at) - frontend/src/components/search/SortSelector.tsx
- [ ] [T091] [US3] Create NaturalLanguageSearch component for chatbot integration - frontend/src/components/search/NaturalLanguageSearch.tsx
- [ ] [T092] [US3] Update TaskList to support search/filter/sort results - frontend/src/components/tasks/TaskList.tsx

### Frontend - Service Layer

- [ ] [T093] [P] [US3] Create search service with Dapr Service Invocation - frontend/src/services/searchService.ts
- [ ] [T094] [US3] Add search/filter/sort API calls with query parameters - frontend/src/services/searchService.ts

### Testing

- [ ] [T095] [P] [US3] Unit tests for keyword search service - backend/tests/unit/test_search_service.py
- [ ] [T096] [P] [US3] Unit tests for multi-criteria filtering - backend/tests/unit/test_filter_service.py
- [ ] [T097] [P] [US3] Unit tests for natural language query parser - backend/tests/unit/test_nlp_query_service.py
- [ ] [T098] [US3] Integration test: Search tasks by keyword and verify results - backend/tests/integration/test_search.py
- [ ] [T099] [US3] Integration test: Filter tasks by multiple criteria - backend/tests/integration/test_search.py
- [ ] [T100] [US3] E2E test: Natural language search via chatbot - frontend/tests/e2e/natural-language-search.spec.ts

**Parallel Execution Example (US3)**:
- T085, T086, T087 (API endpoints) can run in parallel after T080-T084 complete
- T088, T089, T090 (UI components) can run in parallel
- T095, T096, T097 (unit tests) can run in parallel

## Phase 6: User Story 4 - Multi-Level Priority Management (P4)

**Acceptance Criteria**:
- Three priority levels: High, Medium, Low
- Priority-based sorting and filtering
- Visual priority indicators in UI
- Priority updates trigger events

### Backend - Data Models

- [ ] [T110] [US4] Create PriorityLevel enum (High, Medium, Low) - backend/src/models/priority.py
- [ ] [T111] [US4] Add priority field to Task model with default value (Medium)

### Backend - Business Logic

- [ ] [T112] [US4] Implement priority validation service - backend/src/services/priority_service.py
- [ ] [T113] [US4] Add priority change event publishing (`todo.task.priority_changed`) - backend/src/events/publishers/task_events.py

### Backend - API Endpoints

- [ ] [T114] [US4] Update POST /api/tasks to include priority field - backend/src/api/tasks.py
- [ ] [T115] [US4] Update PATCH /api/tasks/{task_id} to support priority updates - backend/src/api/tasks.py
- [ ] [T116] [US4] Update GET /api/tasks to support priority filtering - backend/src/api/tasks.py

### Frontend - UI Components

- [ ] [T117] [P] [US4] Create PrioritySelector component (High/Medium/Low dropdown) - frontend/src/components/tasks/PrioritySelector.tsx
- [ ] [T118] [P] [US4] Create PriorityBadge component with color coding - frontend/src/components/tasks/PriorityBadge.tsx
- [ ] [T119] [US4] Update TaskForm to include priority selector - frontend/src/components/tasks/TaskForm.tsx
- [ ] [T120] [US4] Update TaskList to display priority badges - frontend/src/components/tasks/TaskList.tsx

### Frontend - Service Layer

- [ ] [T121] [US4] Update task service to include priority in API calls - frontend/src/services/taskService.ts

### Testing

- [ ] [T122] [P] [US4] Unit tests for priority validation - backend/tests/unit/test_priority_service.py
- [ ] [T123] [US4] Integration test: Create task with priority and verify storage - backend/tests/integration/test_priority.py
- [ ] [T124] [US4] Integration test: Update task priority and verify event publishing - backend/tests/integration/test_priority.py
- [ ] [T125] [US4] E2E test: Filter tasks by priority via frontend - frontend/tests/e2e/priority-filtering.spec.ts

**Parallel Execution Example (US4)**:
- T117, T118 (UI components) can run in parallel
- T122 (unit test) can run independently

## Phase N: Polish & Cross-Cutting Concerns

### Documentation

- [ ] [T130] [P] Update API documentation with new endpoints - backend/docs/api.md
- [ ] [T131] [P] Create Dapr component configuration guide - docs/dapr-components.md
- [ ] [T132] [P] Update quickstart guide with new features - specs/010-dapr-abstraction/quickstart.md
- [ ] [T133] Create troubleshooting guide for Dapr integration - docs/troubleshooting.md

### Performance & Monitoring

- [ ] [T134] [P] Add distributed tracing with correlation IDs to all endpoints - backend/src/middleware/tracing.py
- [ ] [T135] [P] Configure Zipkin integration for trace visualization - backend/src/config/zipkin.py
- [ ] [T136] Add performance metrics for Dapr API calls - backend/src/middleware/metrics.py
- [ ] [T137] Create Grafana dashboard for event streaming metrics - charts/ai-todo/dashboards/events.json

### Security & Validation

- [ ] [T138] [P] Add input validation for all new API endpoints - backend/src/validators/
- [ ] [T139] [P] Implement rate limiting for search endpoints - backend/src/middleware/rate_limit.py
- [ ] [T140] Add CORS configuration for Dapr sidecar communication - backend/src/config/cors.py

### Deployment

- [ ] [T141] Update Helm chart with Dapr sidecar annotations - charts/ai-todo/templates/backend-deployment.yaml
- [ ] [T142] Create Kubernetes manifests for Dapr components - charts/ai-todo/templates/dapr-components.yaml
- [ ] [T143] Update CI/CD pipeline to deploy Dapr components - .github/workflows/deploy.yml
- [ ] [T144] Create production environment configuration - backend/.env.production

## Dependencies

### Story Completion Order

1. **Phase 2 (Foundational)** must complete before any user story work begins
   - Dapr components (T010-T014)
   - Event schema & SDK utilities (T015-T020)
   - Database migrations (T021-T024)

2. **US1 (Recurring Tasks)** should complete before US2 (Reminders)
   - Reminders depend on Task entity with recurrence fields
   - Event schema from US1 is reused in US2

3. **US3 (Search)** and **US4 (Priority)** can run in parallel after US1 completes
   - Both depend on Task entity from US1
   - No direct dependencies between US3 and US4

4. **Phase N (Polish)** runs after all user stories complete
   - Documentation updates reference all features
   - Performance monitoring covers all endpoints

### Critical Path

```
Phase 2 (Foundational) → US1 (Recurring Tasks) → US2 (Reminders)
                                                ↘
                                                  Phase N (Polish)
                                                ↗
                         US3 (Search) + US4 (Priority) [Parallel]
```

## Acceptance Criteria Checklist

### US1 - Recurring Task Automation
- [ ] Daily tasks auto-generate at midnight
- [ ] Weekly tasks auto-generate on specified day of week
- [ ] Monthly tasks auto-generate on specified day of month
- [ ] Correlation IDs prevent duplicate generation on event replay
- [ ] Event `todo.task.completed` triggers recurring instance generation
- [ ] Parent-child relationship tracked via `parent_task_id`

### US2 - Intelligent Time-Based Reminders
- [ ] Reminders scheduled via Dapr Jobs API (no polling)
- [ ] Exact-time delivery with callback endpoint
- [ ] Reminder cancellation deletes Dapr Job
- [ ] Reminder status tracking (scheduled/sent/cancelled)
- [ ] Event `todo.reminder.fired` published on delivery

### US3 - Advanced Search and Filtering
- [ ] Server-side keyword search (title/description)
- [ ] Multi-criteria filtering (status, priority, tags, due_date)
- [ ] Sorting by due_date, priority, created_at, updated_at
- [ ] Natural language query parsing for chatbot integration
- [ ] Pagination support (limit/offset)
- [ ] Tag listing endpoint for filter UI

### US4 - Multi-Level Priority Management
- [ ] Three priority levels: High, Medium, Low
- [ ] Priority-based sorting and filtering
- [ ] Visual priority indicators in UI
- [ ] Priority updates trigger events
- [ ] Default priority (Medium) applied to new tasks

## Notes

- All tasks follow Phase-V Event-Driven Architecture principles
- Dapr sidecar pattern used for all infrastructure access
- No direct database, Kafka, or secrets access in application code
- Correlation IDs used for distributed tracing and idempotency
- Cloud provider neutrality maintained via YAML-based component configuration
- Testing strategy includes unit, integration, and E2E tests for each user story
