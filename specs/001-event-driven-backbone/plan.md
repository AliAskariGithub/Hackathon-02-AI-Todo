# Implementation Plan: Local Event-Driven Backbone

**Branch**: `001-event-driven-backbone` | **Date**: 2026-02-13 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-event-driven-backbone/spec.md`

## Summary

Deploy a local event-driven architecture using Kafka (Strimzi Operator in KRaft mode) and Dapr on Minikube to enable real-time task synchronization across browser tabs, automatic recurring task generation, and timely notifications. The system will consist of three new microservices (Notification, Recurring Task, Audit) communicating asynchronously via Kafka topics, with a WebSocket/SSE bridge for real-time frontend updates. All infrastructure will be packaged using Helm v3 and operate within 4GB RAM / 2-CPU resource constraints.

## Technical Context

**Language/Version**: Python 3.11+ (backend microservices), TypeScript/Next.js 16.1.2 (frontend)
**Primary Dependencies**: FastAPI (backend), Dapr Python SDK v1.14+, Strimzi Operator v0.43+, Next.js 16.1.2, Socket.IO or native WebSocket/SSE
**Storage**: Neon PostgreSQL (existing), Kafka topics for event streaming (new)
**Event Streaming**: Kafka via Strimzi Operator (KRaft mode, no Zookeeper)
**Distributed Runtime**: Dapr v1.14+ with Pub/Sub, Service Invocation, Jobs, and Secrets building blocks
**Testing**: pytest (backend), Playwright (E2E), manual event tracing via Kafka console consumer
**Target Platform**: Kubernetes (Minikube local development)
**Project Type**: Web application with microservices architecture
**Architecture Pattern**: Event-Driven Architecture (EDA) with Dapr abstraction layer
**Performance Goals**: <2s real-time sync latency, <500ms event processing (p95), 100 concurrent WebSocket connections
**Constraints**: 4GB RAM / 2-CPU Minikube limit, local-only deployment, no cloud dependencies
**Scale/Scope**: 3 new microservices, 4-6 Kafka topics, 100+ concurrent users, 10GB disk for Kafka persistence

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Core Principles Compliance

- **Agent-First Mandate**: All code and infrastructure YAML will be generated via SDD workflow (Claude Code orchestrating Gordon, kubectl-ai, Kagent)
- **Evolution Principle**: Phase-V builds upon existing Phase-I through Phase-IV functionality (authentication, task management, Kubernetes deployment)
- **Decoupled Evolution**: Services will communicate asynchronously through Kafka events via Dapr Pub/Sub
- **Infrastructure Abstraction**: Dapr components abstract Kafka, enabling provider swaps (Kafka → Redpanda) with zero code changes
- **Cloud-Native Excellence**: Horizontal scalability, automated recovery, proper observability via distributed tracing

### ✅ Infrastructure Standards

- **Helm Primary**: All Kubernetes resources managed via Helm charts in `/charts` directory
- **Stateless Services**: All microservices remain stateless; persistence via Neon PostgreSQL and Kafka topics
- **Standardized Labels**: All resources include required `app.kubernetes.io/*` labels
- **Dapr Sidecar Pattern**: All microservice pods will have `dapr.io/enabled: "true"` annotation
- **Strimzi Governance**: Kafka cluster managed by Strimzi Operator
- **Event Schema Standardization**: All events follow constitution-mandated JSON schema (event_type, payload, user_id, timestamp, correlation_id)
- **Topic Naming Convention**: `<domain>.<entity>.<action>` pattern (e.g., `todo.task.created`)

### ✅ Security & Operational Standards

- **Non-Root Execution**: All container images use dedicated `appuser` with minimal privileges
- **Secrets Management**: All credentials accessed via Dapr Secrets API (no hardcoded secrets)
- **Observability**: Health check endpoints, structured logging, Prometheus metrics, distributed tracing via Dapr/OpenTelemetry
- **Resource Management**: All pods define resource requests and limits
- **Scheduling Standards**: Dapr Jobs API for reminders (no polling-based cron jobs)

### ⚠️ Potential Violations Requiring Justification

None identified. All requirements align with constitution v3.0.0 Phase-V standards.

## Project Structure

### Documentation (this feature)

```text
specs/001-event-driven-backbone/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (in progress)
├── research.md          # Phase 0 output (to be created)
├── data-model.md        # Phase 1 output (to be created)
├── quickstart.md        # Phase 1 output (to be created)
├── contracts/           # Phase 1 output (to be created)
│   ├── event-schemas.yaml
│   ├── notification-service-api.yaml
│   ├── recurring-service-api.yaml
│   └── audit-service-api.yaml
├── checklists/
│   └── requirements.md  # Specification quality checklist (completed)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
# Existing structure (Phase I-IV)
backend/
├── src/
│   ├── main.py
│   ├── api/routers/
│   ├── models/
│   ├── services/
│   └── mcp/
└── tests/

frontend/
├── app/
├── components/
├── services/
└── tests/

# New structure (Phase V - Event-Driven Backbone)
services/                    # NEW: Microservices directory
├── notification/
│   ├── src/
│   │   ├── main.py         # FastAPI app with Dapr Pub/Sub subscriber
│   │   ├── handlers/       # Event handlers for reminders topic
│   │   ├── models/         # Event models (Reminder Event)
│   │   └── config.py       # Service configuration
│   ├── Dockerfile          # Multi-stage build, non-root user
│   ├── requirements.txt
│   └── tests/
│
├── recurring/
│   ├── src/
│   │   ├── main.py         # FastAPI app with Dapr Pub/Sub subscriber
│   │   ├── handlers/       # Event handlers for task.completed
│   │   ├── services/       # Recurring task calculation logic
│   │   ├── models/         # Event models (Task Event)
│   │   └── config.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── tests/
│
└── audit/
    ├── src/
    │   ├── main.py         # FastAPI app with Dapr Pub/Sub subscriber
    │   ├── handlers/       # Event handlers for all system events
    │   ├── storage/        # Audit log persistence logic
    │   ├── models/         # Event models (Audit Log Entry)
    │   └── config.py
    ├── Dockerfile
    ├── requirements.txt
    └── tests/

charts/                      # Helm charts directory
├── ai-todo/                # Existing main application chart
│   ├── Chart.yaml
│   ├── values.yaml
│   └── templates/
│
├── kafka-cluster/          # NEW: Strimzi Kafka cluster chart
│   ├── Chart.yaml
│   ├── values.yaml         # KRaft mode config, resource limits
│   └── templates/
│       ├── kafka.yaml      # Kafka custom resource
│       └── topics.yaml     # KafkaTopic custom resources
│
├── dapr-components/        # NEW: Dapr component configurations
│   ├── Chart.yaml
│   ├── values.yaml
│   └── templates/
│       ├── pubsub-kafka.yaml       # Dapr Pub/Sub component
│       ├── statestore-postgres.yaml # Dapr State component
│       ├── secretstore-k8s.yaml    # Dapr Secrets component
│       └── configuration.yaml      # Dapr Configuration (tracing)
│
└── microservices/          # NEW: Microservices deployment chart
    ├── Chart.yaml
    ├── values.yaml
    └── templates/
        ├── notification-deployment.yaml
        ├── recurring-deployment.yaml
        ├── audit-deployment.yaml
        └── services.yaml

backend/src/                # Updates to existing backend
├── events/                 # NEW: Event publishing logic
│   ├── publisher.py        # Dapr Pub/Sub event publisher
│   └── schemas.py          # Event schema definitions
│
└── websocket/              # NEW: WebSocket/SSE bridge
    ├── manager.py          # WebSocket connection manager
    ├── handlers.py         # Event handlers for real-time updates
    └── routes.py           # WebSocket endpoint routes

frontend/                   # Updates to existing frontend
├── hooks/
│   └── useRealtimeSync.ts  # NEW: WebSocket/SSE hook for real-time updates
└── services/
    └── websocket.ts        # NEW: WebSocket client service
```

**Structure Decision**: Microservices architecture with dedicated `/services` directory for new event-driven services. Existing `backend/` and `frontend/` remain for core API and UI. Helm charts organized by concern (kafka-cluster, dapr-components, microservices). This structure maintains clear separation between existing monolithic components and new event-driven microservices while enabling independent scaling and deployment.

## Complexity Tracking

> **No violations identified - this section is not applicable**

## Event-Driven Architecture Decisions (Phase-V)

### Communication Pattern

**Synchronous (HTTP/REST)**:
- User authentication and authorization (existing Better Auth JWT flow)
- Task CRUD operations from frontend to backend API (existing endpoints)
- Recurring Task Service → Backend API: Create new task instance (Dapr Service Invocation)
- Health check endpoints for all services

**Asynchronous (Events)**:
- Task state changes (created, updated, completed, deleted) → Kafka topics
- Reminder scheduling → Dapr Jobs API → Notification Service
- Real-time UI updates → WebSocket/SSE bridge → Frontend
- Audit logging → All system events → Audit Service
- Recurring task generation → task.completed event → Recurring Task Service

**Rationale**: Synchronous communication is used for operations requiring immediate user feedback (authentication, CRUD operations). Asynchronous events are used for operations that can tolerate eventual consistency and benefit from decoupling (notifications, audit logging, recurring task generation, real-time sync). This split enables independent service scaling, resilient failure handling, and loose coupling while maintaining responsive user experience for critical operations.

### Dapr Components Required

- [x] **State Store**: PostgreSQL (existing Neon database) - for audit log persistence and idempotency tracking
- [x] **Pub/Sub**: Kafka (Strimzi Operator) - for all event-driven communication
- [x] **Secrets**: Kubernetes Secrets - for DATABASE_URL, KAFKA_BOOTSTRAP_SERVERS, BETTER_AUTH_SECRET
- [x] **Jobs**: Dapr Jobs API - for scheduling task reminders at exact times

### Event Schema Design

**Events to Publish**:

1. `todo.task.created`
   - Payload: `{ task_id, title, description, priority, due_date, recurrence, tags, user_id }`
   - Consumers: Audit Service, Frontend (via WebSocket bridge)
   - Publisher: Backend API (on task creation)

2. `todo.task.updated`
   - Payload: `{ task_id, updated_fields, user_id }`
   - Consumers: Audit Service, Frontend (via WebSocket bridge)
   - Publisher: Backend API (on task update)

3. `todo.task.completed`
   - Payload: `{ task_id, completed_at, recurrence, recurrence_day_of_week, recurrence_day_of_month, user_id }`
   - Consumers: Recurring Task Service, Audit Service, Frontend (via WebSocket bridge)
   - Publisher: Backend API (on task completion)

4. `todo.task.deleted`
   - Payload: `{ task_id, user_id }`
   - Consumers: Audit Service, Frontend (via WebSocket bridge)
   - Publisher: Backend API (on task deletion)

5. `todo.reminder.scheduled`
   - Payload: `{ reminder_id, task_id, scheduled_time, user_id }`
   - Consumers: Notification Service (via Dapr Jobs API callback)
   - Publisher: Backend API (when reminder is created)

6. `todo.notification.sent`
   - Payload: `{ notification_id, task_id, sent_at, user_id }`
   - Consumers: Audit Service
   - Publisher: Notification Service (after logging notification)

**Events to Subscribe**:

1. `todo.task.completed` (Recurring Task Service)
   - Handler: `RecurringTaskHandler.handle_task_completed()`
   - Action: Calculate next due date based on recurrence pattern, invoke Backend API via Dapr Service Invocation to create new task instance

2. `todo.reminder.*` (Notification Service)
   - Handler: `NotificationHandler.handle_reminder()`
   - Action: Log notification trigger with timestamp, publish `todo.notification.sent` event

3. `todo.*` (Audit Service)
   - Handler: `AuditHandler.handle_all_events()`
   - Action: Persist event to audit log with correlation ID, timestamp, and full payload

4. `todo.task.*` (Frontend via WebSocket bridge)
   - Handler: `WebSocketManager.broadcast_to_user()`
   - Action: Push event to all connected WebSocket clients for the affected user

### Distributed Tracing Strategy

**Critical Paths**:
1. User completes task → Backend publishes event → Recurring Service generates next task → Backend creates task → Frontend receives update
2. User schedules reminder → Backend schedules Dapr Job → Notification Service receives callback → Notification logged
3. User creates task → Backend publishes event → Audit Service logs event → Frontend receives update

**Correlation ID Propagation**:
- Generate UUID correlation ID in Backend API for each user request
- Include correlation ID in all published events (event schema field)
- Dapr automatically propagates trace context across service boundaries
- Frontend includes correlation ID in WebSocket messages for end-to-end tracing

**Sampling Rate**:
- Development (Minikube): 100% sampling for full visibility
- Production: 10% adaptive sampling to reduce overhead while maintaining observability

### Cloud Provider Neutrality

**Provider-Specific Features Used**:
- None - all infrastructure uses CNCF-standard Kubernetes APIs
- Kafka managed by Strimzi Operator (cloud-agnostic)
- Dapr components abstract all infrastructure dependencies

**Abstraction Strategy**:
- Kafka access via Dapr Pub/Sub component (can swap to Redpanda, Azure Event Hubs, AWS Kinesis)
- State storage via Dapr State component (can swap PostgreSQL, Redis, Azure Cosmos DB)
- Secrets via Dapr Secrets component (can swap Kubernetes Secrets, Azure Key Vault, AWS Secrets Manager)

**Migration Path**:
1. Update Dapr component YAML files (e.g., change `pubsub-kafka.yaml` to `pubsub-redpanda.yaml`)
2. Update Helm values to point to new infrastructure endpoints
3. Zero application code changes required
4. Redeploy services with updated Dapr components

## Architecture Decisions Requiring Documentation

### Decision 1: Topic Partitioning Strategy

**Context**: Kafka topics require partition count configuration to balance parallelism and resource usage.

**Options Considered**:
1. Single partition per topic (simplest, maintains strict ordering)
2. 3 partitions per topic (moderate parallelism, realistic for production)
3. 10+ partitions per topic (maximum parallelism, higher resource usage)

**Decision**: **3 partitions per topic** for `todo.task.*` events, **1 partition** for `todo.reminder.*` and `todo.notification.*` events

**Rationale**:
- Task events benefit from parallelism (multiple consumers can process different users' tasks concurrently)
- 3 partitions balance local resource constraints (4GB RAM) with realistic production patterns
- Reminder/notification events require strict ordering per user, so single partition ensures sequential processing
- Partition key: `user_id` ensures all events for a user go to the same partition (maintains ordering per user)

**Tradeoffs**:
- More partitions = higher memory usage but better throughput
- Fewer partitions = lower resource usage but potential bottleneck under load
- 3 partitions is a pragmatic middle ground for local development that mirrors production patterns

### Decision 2: Dapr Component Scoping

**Context**: Dapr components can be scoped to specific namespaces or made globally accessible.

**Options Considered**:
1. Global Dapr components (all services access all topics)
2. Namespace-scoped components (services only access topics in their namespace)
3. Application-scoped components (fine-grained access control per service)

**Decision**: **Application-scoped Dapr Pub/Sub components** with explicit topic subscriptions per service

**Rationale**:
- Notification Service only subscribes to `todo.reminder.*` topics
- Recurring Task Service only subscribes to `todo.task.completed` topic
- Audit Service subscribes to all `todo.*` topics
- Backend API only publishes (no subscriptions)
- This prevents accidental cross-service event consumption and improves security

**Implementation**:
- Define Dapr Pub/Sub component with `scopes` field limiting access to specific app-ids
- Each service declares subscriptions in `/dapr/subscribe` endpoint
- Dapr enforces access control at runtime

**Tradeoffs**:
- More configuration overhead vs. simpler global access
- Better security and isolation vs. easier development
- Explicit scoping prevents accidental event consumption and makes event flows clearer

### Decision 3: UI Sync Strategy (WebSocket vs SSE)

**Context**: Real-time UI updates require bidirectional or unidirectional communication from backend to frontend.

**Options Considered**:
1. **WebSocket**: Full-duplex communication, requires connection management, more complex
2. **Server-Sent Events (SSE)**: Unidirectional (server → client), simpler, HTTP-based, auto-reconnect
3. **Long Polling**: Fallback option, higher latency, more resource-intensive

**Decision**: **Server-Sent Events (SSE)** for real-time task updates

**Rationale**:
- Task updates are unidirectional (backend → frontend) - no need for client → server messages via WebSocket
- SSE provides automatic reconnection on connection loss (critical for mobile/flaky networks)
- SSE is simpler to implement and debug (standard HTTP, no special protocols)
- SSE works through most corporate firewalls and proxies (HTTP-based)
- Next.js 16.1.2 has excellent SSE support via Route Handlers and `ReadableStream`
- Lower resource usage on backend (no WebSocket connection state management)

**Implementation**:
- Backend: FastAPI endpoint `/api/events/stream` returns `EventSourceResponse` with task events
- Frontend: `EventSource` API connects to SSE endpoint, receives events, updates UI via React state
- Reconnection: Browser automatically reconnects on connection loss (SSE built-in feature)
- Authentication: JWT token passed via query parameter or custom header

**Tradeoffs**:
- SSE is unidirectional (can't send messages from client to server) - acceptable since all user actions go through REST API
- WebSocket would enable bidirectional communication but adds complexity we don't need
- SSE has slightly higher latency than WebSocket but well within 2-second requirement

**Fallback**: If SSE proves insufficient, can upgrade to WebSocket without changing event architecture (only transport layer changes)

## Testing Strategy

### E2E Event Trace Test

**Objective**: Verify complete event flow from user action to service processing

**Test Steps**:
1. Open two browser tabs with task list
2. Mark a recurring task as complete in tab 1
3. Tail logs of Recurring Task Service: `kubectl logs -f deployment/recurring-service -c daprd`
4. Verify:
   - `task.completed` event received by Recurring Task Service within 500ms
   - New task instance created via Dapr Service Invocation
   - Tab 2 automatically shows new task within 2 seconds
   - Audit Service logs both `task.completed` and `task.created` events

**Success Criteria**: All events logged with correct correlation IDs, no duplicate task creation, both tabs synchronized

### Job Callback Test

**Objective**: Verify Dapr Jobs API triggers Notification Service at exact scheduled time

**Test Steps**:
1. Create task with reminder scheduled for 30 seconds in future
2. Verify Dapr Job created: `dapr jobs list`
3. Wait for scheduled time
4. Tail Notification Service logs: `kubectl logs -f deployment/notification-service`
5. Verify:
   - Notification logged within 1 second of scheduled time
   - `todo.notification.sent` event published
   - Audit Service captures notification event

**Success Criteria**: Notification triggered within 1-second accuracy, no missed or duplicate notifications

### State Consistency Test

**Objective**: Verify Audit Service captures all system events without gaps

**Test Steps**:
1. Perform sequence of operations: create task, update task, complete task, delete task
2. Query Audit Service logs: `kubectl exec -it deployment/audit-service -- cat /var/log/audit.log`
3. Verify:
   - All 4 events present in chronological order
   - Each event has unique correlation ID
   - No duplicate events
   - Timestamps are sequential

**Success Criteria**: 100% event capture rate, no gaps or duplicates, correct ordering

### Idempotency Validation Test

**Objective**: Ensure restarting Recurring Task Service doesn't create duplicate tasks

**Test Steps**:
1. Complete a recurring task
2. Verify new task instance created
3. Restart Recurring Task Service pod: `kubectl rollout restart deployment/recurring-service`
4. Wait for pod to restart and replay Kafka events
5. Verify:
   - No duplicate task instances created
   - Idempotency key prevents duplicate processing
   - Audit log shows only one `task.created` event

**Success Criteria**: Exactly one new task instance created, no duplicates after service restart

## Phase 0: Research Tasks

The following research tasks must be completed before proceeding to Phase 1 design:

1. **Strimzi Kafka KRaft Configuration for Resource-Constrained Environments**
   - Research optimal Kafka broker configuration for 4GB RAM / 2-CPU Minikube
   - Determine KRaft controller quorum size (1 vs 3 controllers)
   - Identify memory and CPU limits for Kafka pods
   - Find recommended JVM heap settings for small-scale deployments

2. **Dapr Python SDK Async Pub/Sub Patterns**
   - Research latest Dapr Python SDK (v1.14+) async/await patterns for event publishing
   - Identify best practices for Dapr Pub/Sub subscriber implementation in FastAPI
   - Determine error handling and retry strategies for event processing
   - Find examples of idempotency key implementation with Dapr

3. **Next.js 16.1.2 Server-Sent Events (SSE) Implementation**
   - Research Next.js 16 Route Handler patterns for SSE endpoints
   - Identify best practices for `ReadableStream` and `EventSource` API usage
   - Determine authentication strategies for SSE connections (JWT in query params vs headers)
   - Find examples of SSE reconnection handling and error recovery

4. **Kafka Topic Retention and Partition Configuration**
   - Research recommended retention policies for event-driven systems (7 days vs 30 days)
   - Determine optimal partition count for low-volume local development
   - Identify partition key strategies for user-scoped events
   - Find best practices for dead letter queue configuration

5. **Dapr Distributed Tracing Configuration**
   - Research Dapr Configuration YAML for OpenTelemetry tracing
   - Identify sampling strategies for development vs production
   - Determine trace context propagation across Dapr components
   - Find examples of correlation ID generation and propagation

## Phase 1: Design Artifacts (To Be Created)

The following artifacts will be created in Phase 1 after research is complete:

1. **data-model.md**: Event schemas, entity relationships, state transitions
2. **contracts/event-schemas.yaml**: OpenAPI/AsyncAPI specification for all events
3. **contracts/notification-service-api.yaml**: Notification Service API contract
4. **contracts/recurring-service-api.yaml**: Recurring Task Service API contract
5. **contracts/audit-service-api.yaml**: Audit Service API contract
6. **quickstart.md**: Step-by-step guide for local development setup

## Next Steps

1. Execute Phase 0 research tasks (use context7 MCP server for latest documentation)
2. Create research.md with findings and decisions
3. Execute Phase 1 design tasks (data models, contracts, quickstart)
4. Update agent context with new technologies
5. Re-validate Constitution Check after design
6. Proceed to `/sp.tasks` for task generation

---

**Status**: Plan complete, ready for Phase 0 research
