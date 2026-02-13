# Tasks: Local Event-Driven Backbone

**Input**: Design documents from `/specs/001-event-driven-backbone/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Tests are NOT explicitly requested in the specification. This task list focuses on implementation only.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `- [ ] [ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/src/`
- **Frontend**: `frontend/`
- **Microservices**: `services/notification/`, `services/recurring/`, `services/audit/`
- **Helm Charts**: `charts/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure for event-driven architecture

- [X] T001 Create microservices directory structure at repository root: `services/notification/`, `services/recurring/`, `services/audit/` - **COMPLETED**
- [X] T002 [P] Initialize Notification Service Python project with FastAPI and Dapr SDK in `services/notification/` - **COMPLETED**
- [X] T003 [P] Initialize Recurring Task Service Python project with FastAPI and Dapr SDK in `services/recurring/` - **COMPLETED**
- [X] T004 [P] Initialize Audit Service Python project with FastAPI and Dapr SDK in `services/audit/` - **COMPLETED**
- [X] T005 [P] Create Helm chart directory structure: `charts/kafka-cluster/`, `charts/dapr-components/`, `charts/microservices/` - **COMPLETED**
- [X] T006 [P] Configure linting and formatting tools for all three microservices (black, flake8, mypy) - **COMPLETED**

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Kafka & Strimzi Setup

- [X] T007 Create Strimzi Kafka cluster Helm chart in `charts/kafka-cluster/Chart.yaml` - **COMPLETED**
- [X] T008 Create Kafka cluster custom resource YAML in `charts/kafka-cluster/templates/kafka.yaml` (KRaft mode, 1 replica, 512Mi-1Gi memory) - **COMPLETED**
- [X] T009 [P] Create KafkaTopic for task events in `charts/kafka-cluster/templates/topics.yaml` (todo.task.events, 3 partitions, 7-day retention) - **COMPLETED**
- [X] T010 [P] Create KafkaTopic for reminders in `charts/kafka-cluster/templates/topics.yaml` (todo.reminders, 1 partition, 1-day retention) - **COMPLETED**
- [X] T011 [P] Create KafkaTopic for notifications in `charts/kafka-cluster/templates/topics.yaml` (todo.notifications, 1 partition, 7-day retention) - **COMPLETED**
- [X] T012 [P] Create KafkaTopic for audit events in `charts/kafka-cluster/templates/topics.yaml` (todo.audit.events, 1 partition, 30-day retention) - **COMPLETED**
- [X] T013 [P] Create KafkaTopic for dead letter queue in `charts/kafka-cluster/templates/topics.yaml` (todo.task.events.dlq, 1 partition, 7-day retention) - **COMPLETED**
- [X] T014 Create Kafka cluster values.yaml in `charts/kafka-cluster/values.yaml` with resource limits and JVM heap settings - **COMPLETED**

### Dapr Components Setup

- [X] T015 Create Dapr components Helm chart in `charts/dapr-components/Chart.yaml` - **COMPLETED**
- [X] T016 [P] Create Dapr Pub/Sub component YAML in `charts/dapr-components/templates/pubsub-kafka.yaml` (kafka-pubsub, connects to Kafka bootstrap server) - **COMPLETED**
- [X] T017 [P] Create Dapr State Store component YAML in `charts/dapr-components/templates/statestore-postgresql.yaml` (connects to Neon PostgreSQL) - **COMPLETED**
- [X] T018 [P] Create Dapr Secrets component YAML in `charts/dapr-components/templates/secretstore-kubernetes.yaml` (Kubernetes secrets store) - **COMPLETED**
- [X] T019 [P] Create Dapr Configuration YAML in `charts/dapr-components/templates/tracing-config.yaml` (OpenTelemetry tracing, 100% sampling) - **COMPLETED**
- [X] T020 Create Dapr components values.yaml in `charts/dapr-components/values.yaml` with Kafka bootstrap server and PostgreSQL connection string - **COMPLETED**

### Event Schema & Tracing

- [X] T021 [P] Create base event schema model in `backend/src/models/events/base_event.py` (event_type, payload, user_id, timestamp, correlation_id) - **COMPLETED**: Implemented in `backend/src/events/schema.py`
- [X] T022 [P] Create task event models in `backend/src/models/events/task_events.py` (TaskCreated, TaskUpdated, TaskCompleted, TaskDeleted) - **COMPLETED**: Implemented in `backend/src/events/schema.py`
- [X] T023 [P] Create reminder event model in `backend/src/models/events/reminder_events.py` (ReminderScheduled) - **COMPLETED**: Implemented in `backend/src/events/schema.py`
- [X] T024 [P] Create notification event model in `backend/src/models/events/notification_events.py` (NotificationSent) - **COMPLETED**: Implemented in `backend/src/events/schema.py`
- [X] T025 [P] Create audit event model in `backend/src/models/events/audit_events.py` (AuditLogged) - **COMPLETED**: Implemented in `backend/src/events/schema.py`
- [X] T026 Implement correlation ID generation utility in `backend/src/utils/correlation.py` with OpenTelemetry span integration - **COMPLETED**: Implemented in `backend/src/middleware/correlation.py`
- [X] T027 Implement event publishing utility in `backend/src/utils/event_publisher.py` using Dapr Python SDK - **COMPLETED**: Implemented in `backend/src/dapr_sdk_utils/pubsub.py`

### Microservice Base Structure

- [X] T028 [P] Create Notification Service main.py in `services/notification/src/main.py` with FastAPI app and Dapr integration - **COMPLETED**
- [X] T029 [P] Create Recurring Task Service main.py in `services/recurring/src/main.py` with FastAPI app and Dapr integration - **COMPLETED**
- [X] T030 [P] Create Audit Service main.py in `services/audit/src/main.py` with FastAPI app and Dapr integration - **COMPLETED**
- [X] T031 [P] Implement health check endpoint in `services/notification/src/main.py` (/health, /ready) - **COMPLETED**
- [X] T032 [P] Implement health check endpoint in `services/recurring/src/main.py` (/health, /ready) - **COMPLETED**
- [X] T033 [P] Implement health check endpoint in `services/audit/src/main.py` (/health, /ready) - **COMPLETED**
- [X] T034 [P] Implement Dapr subscription endpoint in `services/notification/src/main.py` (/dapr/subscribe) - **COMPLETED**
- [X] T035 [P] Implement Dapr subscription endpoint in `services/recurring/src/main.py` (/dapr/subscribe) - **COMPLETED**
- [X] T036 [P] Implement Dapr subscription endpoint in `services/audit/src/main.py` (/dapr/subscribe) - **COMPLETED**

### Idempotency Infrastructure

- [X] T037 [P] Implement idempotency check utility in `services/notification/src/utils/idempotency.py` using Dapr State Store - **COMPLETED**
- [X] T038 [P] Implement idempotency check utility in `services/recurring/src/utils/idempotency.py` using Dapr State Store - **COMPLETED**
- [X] T039 [P] Implement idempotency check utility in `services/audit/src/utils/idempotency.py` using Dapr State Store - **COMPLETED**

### Docker & Deployment

- [X] T040 [P] Create Dockerfile for Notification Service in `services/notification/Dockerfile` (multi-stage, non-root user) - **COMPLETED**
- [X] T041 [P] Create Dockerfile for Recurring Task Service in `services/recurring/Dockerfile` (multi-stage, non-root user) - **COMPLETED**
- [X] T042 [P] Create Dockerfile for Audit Service in `services/audit/Dockerfile` (multi-stage, non-root user) - **COMPLETED**
- [X] T043 Create microservices Helm chart in `charts/microservices/Chart.yaml` - **COMPLETED**
- [X] T044 [P] Create Notification Service deployment YAML in `charts/microservices/templates/notification-deployment.yaml` (Dapr sidecar annotations) - **COMPLETED**
- [X] T045 [P] Create Recurring Task Service deployment YAML in `charts/microservices/templates/recurring-deployment.yaml` (Dapr sidecar annotations) - **COMPLETED**
- [X] T046 [P] Create Audit Service deployment YAML in `charts/microservices/templates/audit-deployment.yaml` (Dapr sidecar annotations) - **COMPLETED**
- [X] T047 [P] Create Kubernetes Service for Notification Service in `charts/microservices/templates/notification-service.yaml` - **COMPLETED**
- [X] T048 [P] Create Kubernetes Service for Recurring Task Service in `charts/microservices/templates/recurring-service.yaml` - **COMPLETED**
- [X] T049 [P] Create Kubernetes Service for Audit Service in `charts/microservices/templates/audit-service.yaml` - **COMPLETED**
- [X] T050 Create microservices values.yaml in `charts/microservices/values.yaml` with resource limits and image tags - **COMPLETED**

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Real-Time Task Synchronization Across Browser Tabs (Priority: P1) 🎯 MVP

**Goal**: Enable automatic task synchronization across all open browser tabs within 2 seconds when tasks are created, updated, completed, or deleted

**Independent Test**: Open two browser tabs, complete a task in tab 1, verify task status updates automatically in tab 2 within 2 seconds

### Backend Event Publishing

- [X] T051 [P] [US1] Add event publishing to create_task endpoint in `backend/src/api/routes/tasks.py` (publish task.created event) - **COMPLETED**: Implemented with correlation ID and error handling
- [X] T052 [P] [US1] Add event publishing to update_task endpoint in `backend/src/api/routes/tasks.py` (publish task.updated event) - **COMPLETED**: Implemented with correlation ID and error handling
- [X] T053 [P] [US1] Add event publishing to complete_task endpoint in `backend/src/api/routes/tasks.py` (publish task.completed event) - **COMPLETED**: Implemented at line 337
- [X] T054 [P] [US1] Add event publishing to delete_task endpoint in `backend/src/api/routes/tasks.py` (publish task.deleted event) - **COMPLETED**: Implemented with task data capture before deletion, correlation ID, and error handling

### SSE Bridge Implementation

- [X] T055 [US1] Create SSE route handler in `frontend/app/api/events/route.ts` with ReadableStream and JWT authentication - **COMPLETED**: Implemented with token verification and streaming
- [X] T056 [US1] Implement Kafka consumer bridge in `backend/src/api/routes/events.py` to forward task events to SSE clients - **COMPLETED**: Implemented with Dapr Pub/Sub webhook and broadcast mechanism
- [X] T057 [US1] Add user_id filtering to SSE bridge to ensure users only receive their own task events - **COMPLETED**: Implemented in broadcast_event function with user_id extraction
- [X] T058 [US1] Implement SSE heartbeat mechanism (30-second interval) in `frontend/app/api/events/route.ts` - **COMPLETED**: Implemented in both frontend and backend with 30-second intervals

### Frontend SSE Integration

- [X] T059 [P] [US1] Create useTaskEvents hook in `frontend/hooks/useTaskEvents.ts` with EventSource API and reconnection logic - **COMPLETED**: Implemented with automatic reconnection, exponential backoff, and comprehensive event handling
- [X] T060 [US1] Integrate useTaskEvents hook into dashboard page in `frontend/app/dashboard/page.tsx` - **COMPLETED**: Integrated with event handlers and connection state management
- [X] T061 [US1] Implement task state update handler for task.created events in `frontend/app/dashboard/page.tsx` - **COMPLETED**: Implemented in handleTaskCreated with duplicate prevention
- [X] T062 [US1] Implement task state update handler for task.updated events in `frontend/app/dashboard/page.tsx` - **COMPLETED**: Implemented in handleTaskUpdated
- [X] T063 [US1] Implement task state update handler for task.completed events in `frontend/app/dashboard/page.tsx` - **COMPLETED**: Implemented in handleTaskCompleted
- [X] T064 [US1] Implement task state update handler for task.deleted events in `frontend/app/dashboard/page.tsx` - **COMPLETED**: Implemented in handleTaskDeleted
- [X] T065 [US1] Add connection status indicator to dashboard UI in `frontend/app/dashboard/page.tsx` (connected/disconnected) - **COMPLETED**: Added with Wifi/WifiOff icons and reconnect button
- [X] T066 [US1] Implement automatic reconnection with 5-second delay on SSE connection failure - **COMPLETED**: Implemented in useTaskEvents hook with exponential backoff

**Checkpoint**: At this point, User Story 1 should be fully functional - tasks sync across all browser tabs within 2 seconds

---

## Phase 4: User Story 2 - Automatic Recurring Task Generation (Priority: P2)

**Goal**: Automatically generate next instance of recurring tasks when completed, preserving all task properties except due date

**Independent Test**: Create a weekly recurring task, mark it complete, verify new instance is automatically created with due date 7 days from today

### Recurring Task Service Implementation

- [X] T067 [P] [US2] Create task completed event handler in `services/recurring/src/handlers/task_completed_handler.py` - **COMPLETED**: Implemented with full event processing logic
- [X] T068 [US2] Implement recurrence pattern calculation logic in `services/recurring/src/services/recurrence_calculator.py` (daily, weekly, monthly) - **COMPLETED**: Implemented with validation
- [X] T069 [US2] Implement next due date calculation for daily pattern in `services/recurring/src/services/recurrence_calculator.py` - **COMPLETED**: Implemented in _calculate_daily
- [X] T070 [US2] Implement next due date calculation for weekly pattern in `services/recurring/src/services/recurrence_calculator.py` - **COMPLETED**: Implemented in _calculate_weekly
- [X] T071 [US2] Implement next due date calculation for monthly pattern in `services/recurring/src/services/recurrence_calculator.py` - **COMPLETED**: Implemented in _calculate_monthly with edge case handling
- [X] T072 [US2] Implement task creation via Dapr Service Invocation in `services/recurring/src/services/task_creator.py` (calls backend API) - **COMPLETED**: Implemented with httpx client
- [X] T073 [US2] Add idempotency check to task completed handler using correlation_id - **COMPLETED**: Integrated in TaskCompletedHandler
- [X] T074 [US2] Add error handling and retry logic for task creation failures - **COMPLETED**: Implemented create_task_with_retry with exponential backoff
- [X] T075 [US2] Add logging for recurring task generation events - **COMPLETED**: Comprehensive logging throughout handler and services

### Backend API Integration

- [X] T076 [US2] Create internal task creation endpoint in `backend/src/api/routes/tasks.py` (/internal/tasks, accepts Dapr Service Invocation) - **COMPLETED**: Implemented at /api/{user_id}/tasks/internal
- [X] T077 [US2] Add validation for recurring task properties in internal endpoint - **COMPLETED**: Comprehensive validation for daily/weekly/monthly patterns
- [X] T078 [US2] Ensure task.created event is published for generated recurring tasks - **COMPLETED**: Event publishing integrated in internal endpoint

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - recurring tasks generate automatically and sync across tabs

---

## Phase 5: User Story 3 - Timely Task Reminder Notifications (Priority: P3)

**Goal**: Trigger reminder notifications at exact scheduled time using Dapr Jobs API with 1-second accuracy

**Independent Test**: Create task with reminder scheduled for 1 minute in future, verify notification is logged at exact scheduled time

### Reminder Scheduling

- [X] T079 [P] [US3] Create reminder scheduling endpoint in `backend/src/api/routes/reminders.py` (POST /reminders) - **COMPLETED**: Already implemented with full CRUD operations
- [X] T080 [US3] Implement Dapr Jobs API integration in `backend/src/services/reminder_scheduler.py` (schedule job with callback URL) - **COMPLETED**: Implemented with schedule, cancel, and status methods
- [X] T081 [US3] Create Reminder entity model in `backend/src/models/reminder.py` (id, task_id, user_id, scheduled_time, message, job_name, status) - **COMPLETED**: Already implemented with Dapr Jobs integration
- [X] T082 [US3] Implement reminder creation logic in `backend/src/services/reminder_service.py` - **COMPLETED**: Already implemented with scheduling and cancellation
- [X] T083 [US3] Add reminder.scheduled event publishing after job creation - **COMPLETED**: Integrated in reminder_service.py
- [X] T084 [US3] Implement reminder cancellation logic when task is completed before reminder time - **COMPLETED**: Integrated in complete_task endpoint

### Notification Service Implementation

- [X] T085 [P] [US3] Create Dapr Jobs callback endpoint in `services/notification/src/handlers/job_callback_handler.py` (/jobs/reminder-callback) - **COMPLETED**: Implemented with full callback processing
- [X] T086 [US3] Implement notification logging in `services/notification/src/services/notification_logger.py` - **COMPLETED**: Implemented with timing validation
- [X] T087 [US3] Add notification.sent event publishing after logging - **COMPLETED**: Integrated in job_callback_handler
- [X] T088 [US3] Add timestamp validation to ensure notification triggered within 1 second of scheduled time - **COMPLETED**: Implemented in notification_logger with 1-second tolerance
- [X] T089 [US3] Add error handling for failed notification processing - **COMPLETED**: Comprehensive error handling throughout handler

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently - reminders trigger at exact scheduled time

---

## Phase 6: User Story 4 - System Activity Audit Trail (Priority: P4)

**Goal**: Capture all system events in chronological audit log for debugging, compliance, and analytics

**Independent Test**: Perform task operations (create, update, complete, delete), verify all events captured in audit log with correct timestamps

### Audit Service Implementation

- [X] T090 [P] [US4] Create audit event handler in `services/audit/src/handlers/audit_handler.py` (subscribes to all topics) - **COMPLETED**: Implemented with full event processing and service name extraction
- [X] T091 [US4] Create AuditLog entity model in `services/audit/src/models/audit_log.py` (id, event_type, event_payload, user_id, correlation_id, service_name, timestamp) - **COMPLETED**: Implemented with composite indexes for query optimization
- [X] T092 [US4] Implement audit log persistence in `services/audit/src/storage/audit_storage.py` (PostgreSQL via SQLModel) - **COMPLETED**: Implemented with full CRUD operations
- [X] T093 [US4] Add chronological ordering validation (ensure no gaps in timestamps) - **COMPLETED**: Implemented validate_chronological_order method
- [X] T094 [US4] Add duplicate event detection using correlation_id - **COMPLETED**: Implemented check_duplicate_event method
- [X] T095 [US4] Implement audit log query endpoint in `services/audit/src/api/routes.py` (GET /audit/logs with filtering) - **COMPLETED**: Implemented with comprehensive filtering
- [X] T096 [US4] Implement audit statistics endpoint in `services/audit/src/api/routes.py` (GET /audit/stats) - **COMPLETED**: Implemented with aggregated statistics
- [X] T097 [US4] Add pagination support for audit log queries (limit, offset) - **COMPLETED**: Integrated in query endpoint
- [X] T098 [US4] Add filtering by user_id, event_type, correlation_id, date range - **COMPLETED**: All filters implemented in AuditLogQuery

**Checkpoint**: All user stories should now be independently functional - complete audit trail of all system events

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and production readiness

### Monitoring & Observability

- [X] T099 [P] Deploy Zipkin for distributed tracing in `charts/zipkin/` - **COMPLETED**: Created Helm chart with deployment, service, and helpers
- [X] T100 [P] Configure Dapr tracing to send spans to Zipkin - **COMPLETED**: Already configured in dapr-components values.yaml with Zipkin endpoint
- [X] T101 [P] Add structured logging to all microservices using Python logging module - **COMPLETED**: Created logger.py for notification, recurring, and audit services with JSON formatting and correlation ID tracking
- [X] T102 [P] Add Prometheus metrics endpoints to all microservices (/metrics) - **COMPLETED**: Created metrics.py for all services with HTTP, event processing, and business metrics

### Error Handling & Resilience

- [X] T103 [P] Implement dead letter queue handler for failed events in `backend/src/services/dlq_handler.py` - **COMPLETED**: Implemented with DLQ event management and file logging fallback
- [X] T104 [P] Add exponential backoff retry logic to all event consumers (3 attempts before DLQ) - **COMPLETED**: Implemented RetryPolicy class and process_event_with_retry function
- [X] T105 [P] Add circuit breaker pattern for Dapr Service Invocation calls - **COMPLETED**: Created circuit_breaker.py with CLOSED/OPEN/HALF_OPEN states and configurable thresholds
- [X] T106 [P] Implement graceful degradation when Kafka is unavailable (local event queue with 5-minute retry) - **COMPLETED**: Created local_event_queue.py with in-memory buffering and periodic retry

### Documentation & Validation

- [X] T107 [P] Update README.md with event-driven architecture overview and setup instructions - **COMPLETED**: Already updated with Event-Driven Architecture section in tech stack
- [X] T108 [P] Create architecture diagram showing event flow from UI to microservices - **COMPLETED**: Created ARCHITECTURE_DIAGRAM.md with system overview, event flows, and component interactions
- [X] T109 [P] Document all Kafka topics and their purposes in `docs/KAFKA_TOPICS.md` - **COMPLETED**: Already created with detailed topic documentation, schemas, and monitoring
- [X] T110 [P] Document all Dapr components and their configurations in `docs/DAPR_COMPONENTS.md` - **COMPLETED**: Already created with component details, usage examples, and best practices
- [ ] T111 Run quickstart.md validation (follow all steps and verify system works end-to-end)

### Security & Performance

- [X] T112 [P] Add rate limiting to SSE endpoint (max 100 concurrent connections per user) - **COMPLETED**: Added MAX_CONNECTIONS_PER_USER check in events.py with 429 response
- [X] T113 [P] Add JWT token validation to SSE endpoint query parameter - **COMPLETED**: Created get_current_user_from_query in deps.py and updated SSE endpoint to support token query parameter
- [X] T114 [P] Configure Kafka topic retention policies per requirements (7 days for tasks, 30 days for audit) - **COMPLETED**: Already configured in topics.yaml with correct retention periods
- [X] T115 [P] Optimize event payload size (remove unnecessary fields, compress if needed) - **COMPLETED**: Created event_optimizer.py with field removal, compression, and size validation

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Integrates with US1 (task.created events sync to UI) but independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Integrates with US1 (notification.sent events sync to UI) but independently testable
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Captures events from all stories but independently testable

### Within Each User Story

- **US1**: Backend event publishing → SSE bridge → Frontend integration
- **US2**: Event handler → Recurrence calculator → Task creator → Backend integration
- **US3**: Reminder scheduling → Dapr Jobs integration → Notification service callback
- **US4**: Audit handler → Storage layer → Query endpoints

### Parallel Opportunities

- **Phase 1**: All 6 setup tasks can run in parallel
- **Phase 2**:
  - Kafka topics (T009-T013) can run in parallel
  - Dapr components (T016-T019) can run in parallel
  - Event models (T021-T025) can run in parallel
  - Microservice base structure (T028-T036) can run in parallel
  - Idempotency utilities (T037-T039) can run in parallel
  - Dockerfiles (T040-T042) can run in parallel
  - Deployment YAMLs (T044-T049) can run in parallel
- **Phase 3 (US1)**: Backend event publishing tasks (T051-T054) can run in parallel
- **Phase 4 (US2)**: Recurrence calculation methods (T069-T071) can run in parallel
- **Phase 5 (US3)**: Reminder scheduling and notification service can be developed in parallel
- **Phase 6 (US4)**: Audit handler and query endpoints can be developed in parallel
- **Phase 7**: All polish tasks can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all backend event publishing tasks together:
Task T051: "Add event publishing to create_task endpoint"
Task T052: "Add event publishing to update_task endpoint"
Task T053: "Add event publishing to complete_task endpoint"
Task T054: "Add event publishing to delete_task endpoint"

# Then launch frontend integration tasks together:
Task T059: "Create useTaskEvents hook"
Task T065: "Add connection status indicator"
```

---

## Parallel Example: Foundational Phase

```bash
# Launch all Kafka topic creation tasks together:
Task T009: "Create KafkaTopic for task events"
Task T010: "Create KafkaTopic for reminders"
Task T011: "Create KafkaTopic for notifications"
Task T012: "Create KafkaTopic for audit events"
Task T013: "Create KafkaTopic for dead letter queue"

# Launch all event model creation tasks together:
Task T021: "Create base event schema model"
Task T022: "Create task event models"
Task T023: "Create reminder event model"
Task T024: "Create notification event model"
Task T025: "Create audit event model"

# Launch all microservice Dockerfile creation tasks together:
Task T040: "Create Dockerfile for Notification Service"
Task T041: "Create Dockerfile for Recurring Task Service"
Task T042: "Create Dockerfile for Audit Service"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (6 tasks)
2. Complete Phase 2: Foundational (44 tasks - CRITICAL, blocks all stories)
3. Complete Phase 3: User Story 1 (16 tasks)
4. **STOP and VALIDATE**: Test User Story 1 independently
   - Open two browser tabs
   - Create/update/complete/delete tasks in tab 1
   - Verify changes appear in tab 2 within 2 seconds
5. Deploy/demo if ready

**Total MVP Tasks**: 66 tasks
**Estimated MVP Effort**: 3-4 days with parallel execution

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready (50 tasks)
2. Add User Story 1 → Test independently → Deploy/Demo (MVP! - 66 tasks total)
3. Add User Story 2 → Test independently → Deploy/Demo (78 tasks total)
4. Add User Story 3 → Test independently → Deploy/Demo (89 tasks total)
5. Add User Story 4 → Test independently → Deploy/Demo (98 tasks total)
6. Add Polish → Production ready (115 tasks total)

Each story adds value without breaking previous stories.

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (50 tasks)
2. Once Foundational is done:
   - Developer A: User Story 1 (16 tasks)
   - Developer B: User Story 2 (12 tasks)
   - Developer C: User Story 3 (11 tasks)
   - Developer D: User Story 4 (9 tasks)
3. Stories complete and integrate independently
4. Team completes Polish together (17 tasks)

---

## Task Summary

**Total Tasks**: 115
- Phase 1 (Setup): 6 tasks
- Phase 2 (Foundational): 44 tasks
- Phase 3 (US1 - Real-Time Sync): 16 tasks
- Phase 4 (US2 - Recurring Tasks): 12 tasks
- Phase 5 (US3 - Reminders): 11 tasks
- Phase 6 (US4 - Audit Trail): 9 tasks
- Phase 7 (Polish): 17 tasks

**Parallel Opportunities**: 67 tasks marked [P] can run in parallel within their phase

**MVP Scope**: Phases 1-3 (66 tasks) deliver core real-time synchronization

**Independent Test Criteria**:
- US1: Open two tabs, verify task changes sync within 2 seconds
- US2: Complete recurring task, verify new instance created with correct due date
- US3: Schedule reminder, verify notification logged at exact scheduled time
- US4: Perform task operations, verify all events captured in audit log

---

## Notes

- [P] tasks = different files, no dependencies within phase
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All tasks follow strict checklist format: `- [ ] [ID] [P?] [Story?] Description with file path`
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
