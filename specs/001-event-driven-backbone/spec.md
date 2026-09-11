# Feature Specification: Local Event-Driven Backbone

**Feature Branch**: `001-event-driven-backbone`
**Created**: 2026-02-13
**Status**: Draft
**Input**: User description: "Todo Full-Stack Web Application - Spec 11: Local Event-Driven Backbone - Deploy Kafka cluster on Minikube using Strimzi Operator, integrate Dapr microservices (Notification, Recurring Task, Audit), and implement real-time UI updates with WebSocket/SSE"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Real-Time Task Synchronization Across Browser Tabs (Priority: P1)

When a user updates a task in one browser tab, all other open tabs automatically reflect the change without requiring a page refresh, ensuring consistent task state across all user sessions.

**Why this priority**: This is the core user-facing value of the event-driven architecture. Without real-time synchronization, users experience data inconsistency and must manually refresh pages, leading to confusion and potential data conflicts.

**Independent Test**: Can be fully tested by opening two browser tabs, completing a task in one tab, and verifying the task status updates automatically in the second tab within 2 seconds. Delivers immediate value by eliminating manual refreshes and preventing stale data views.

**Acceptance Scenarios**:

1. **Given** two browser tabs are open with the same task list, **When** a user marks a task as complete in tab 1, **Then** tab 2 automatically shows the task as completed within 2 seconds
2. **Given** a user is viewing their task list in one tab, **When** another user (or the same user in another session) creates a new task, **Then** the new task appears in the list automatically without page refresh
3. **Given** multiple tabs are open, **When** a task is deleted in one tab, **Then** the task disappears from all other tabs within 2 seconds
4. **Given** a user edits task details (title, description, priority) in one tab, **When** the changes are saved, **Then** all other tabs reflect the updated task details automatically

---

### User Story 2 - Automatic Recurring Task Generation (Priority: P2)

When a user completes a recurring task, the system automatically generates the next instance of the task based on the recurrence pattern (daily, weekly, monthly), eliminating manual task recreation.

**Why this priority**: This automates a repetitive manual process and ensures users never miss recurring tasks. It's a key productivity feature that leverages the event-driven architecture to provide seamless task management.

**Independent Test**: Can be fully tested by creating a weekly recurring task, marking it complete, and verifying a new instance is automatically created with the correct next due date. Delivers value by eliminating manual task recreation for recurring activities.

**Acceptance Scenarios**:

1. **Given** a user has a weekly recurring task due today, **When** the user marks it as complete, **Then** a new instance of the task is automatically created with a due date 7 days from today
2. **Given** a user has a daily recurring task, **When** the task is completed, **Then** a new instance appears immediately with tomorrow's date
3. **Given** a user has a monthly recurring task (e.g., "Pay rent on the 1st"), **When** the task is completed, **Then** a new instance is created for the 1st of the next month
4. **Given** a recurring task is completed, **When** the new instance is generated, **Then** all task properties (title, description, priority, tags) are preserved except the due date

---

### User Story 3 - Timely Task Reminder Notifications (Priority: P3)

Users receive reminder notifications at the exact scheduled time for tasks with due dates, ensuring they never miss important deadlines.

**Why this priority**: While important for user engagement, this is less critical than core task management and real-time sync. Users can still manage tasks effectively without notifications, but notifications enhance the user experience.

**Independent Test**: Can be fully tested by creating a task with a reminder scheduled for 1 minute in the future, waiting for the scheduled time, and verifying the notification is logged at the exact second. Delivers value by proactively alerting users about upcoming tasks.

**Acceptance Scenarios**:

1. **Given** a user schedules a task reminder for 3:00 PM, **When** the system clock reaches 3:00 PM, **Then** a notification is triggered within 1 second of the scheduled time
2. **Given** a user has multiple reminders scheduled, **When** each reminder time arrives, **Then** notifications are triggered in the correct order without delays
3. **Given** a reminder is scheduled but the task is completed before the reminder time, **When** the reminder time arrives, **Then** no notification is sent (reminder is cancelled)
4. **Given** the notification service is temporarily unavailable, **When** it recovers, **Then** missed reminders are not retroactively sent (only future reminders are processed)

---

### User Story 4 - System Activity Audit Trail (Priority: P4)

System administrators and developers can view a chronological log of all system events (task created, completed, updated, deleted) for debugging, compliance, and analytics purposes.

**Why this priority**: This is primarily for operational and debugging purposes rather than direct user value. While important for system observability, it doesn't impact the core user experience of task management.

**Independent Test**: Can be fully tested by performing various task operations (create, update, complete, delete) and verifying all events are captured in the audit log with correct timestamps and event details. Delivers value by enabling system monitoring and troubleshooting.

**Acceptance Scenarios**:

1. **Given** a user creates a new task, **When** the task is saved, **Then** a "task.created" event is logged in the audit trail with task ID, user ID, and timestamp
2. **Given** a user completes a task, **When** the completion is processed, **Then** a "task.completed" event is logged with the task ID and completion timestamp
3. **Given** multiple events occur in rapid succession, **When** querying the audit log, **Then** all events are present in chronological order without gaps
4. **Given** an event processing failure occurs, **When** the system recovers, **Then** the failure is logged in the audit trail with error details

---

### Edge Cases

- What happens when the Kafka cluster is temporarily unavailable? System should queue events locally and retry delivery when connectivity is restored, with a maximum retry period of 5 minutes before alerting administrators.
- How does the system handle event processing failures in microservices? Failed events should be moved to a dead letter queue after 3 retry attempts, and administrators should be notified for manual intervention.
- What happens when a user's browser loses network connectivity? The UI should display a "disconnected" indicator and automatically reconnect when network is restored, replaying any missed events.
- How does the system handle duplicate events? Each event should include an idempotency key, and consumers should deduplicate events based on this key to prevent duplicate processing.
- What happens when the Minikube cluster runs out of resources? The system should gracefully degrade by throttling event processing and alerting administrators when resource usage exceeds 80% of allocated limits.
- How does the system handle clock skew between services? All timestamps should use UTC, and services should synchronize time using NTP to ensure consistent event ordering.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST deploy a Kafka cluster on Minikube using the Strimzi Operator in KRaft mode (without Zookeeper) to minimize resource consumption
- **FR-002**: System MUST configure Kafka cluster to operate within 4GB RAM and 2-CPU Minikube resource limits
- **FR-003**: System MUST deploy three microservices: Notification Service, Recurring Task Service, and Audit Service, each with Dapr sidecar integration
- **FR-004**: System MUST package all infrastructure components (Kafka, Dapr, microservices) using Helm v3 charts for reproducible deployments
- **FR-005**: System MUST establish real-time communication between frontend and backend using WebSocket or Server-Sent Events (SSE)
- **FR-006**: System MUST ensure services do not share databases - all inter-service communication must occur via Kafka topics abstracted by Dapr Pub/Sub
- **FR-007**: System MUST provide a health check endpoint that reports the operational status of all Kafka brokers and Dapr sidecars
- **FR-008**: System MUST support multiple concurrent browser sessions with automatic synchronization of task updates across all sessions
- **FR-009**: System MUST preserve all task properties (title, description, priority, tags) when generating recurring task instances
- **FR-010**: System MUST cancel scheduled reminders when tasks are completed before the reminder time

### Event-Driven Requirements (Phase-V)

- **EDR-001**: System MUST publish `task.completed` event to Kafka topic when a user marks a task as complete
- **EDR-002**: Recurring Task Service MUST subscribe to `task.completed` events and generate new task instances for recurring tasks
- **EDR-003**: System MUST publish `task.created`, `task.updated`, and `task.deleted` events to Kafka topic for all task operations
- **EDR-004**: Frontend MUST subscribe to `task.updates` topic via WebSocket/SSE bridge to receive real-time task changes
- **EDR-005**: Notification Service MUST subscribe to `reminders` topic via Dapr Pub/Sub and log notification triggers
- **EDR-006**: Audit Service MUST subscribe to all system events and persist them to a chronological activity log
- **EDR-007**: All events MUST include correlation IDs for distributed tracing across microservices
- **EDR-008**: System MUST use Dapr Jobs API for scheduling task reminders (no polling-based cron jobs)
- **EDR-009**: System MUST handle event delivery failures with exponential backoff retry strategy (3 attempts) before moving to dead letter queue
- **EDR-010**: System MUST ensure at-least-once event delivery semantics with idempotency keys to prevent duplicate processing
- **EDR-011**: System MUST use Dapr Service Invocation for synchronous inter-service communication (e.g., Recurring Task Service creating new tasks)
- **EDR-012**: System MUST configure Kafka topics with appropriate retention policies (7 days for task events, 30 days for audit events)

### Key Entities

- **Task Event**: Represents a state change in a task (created, updated, completed, deleted), including task ID, user ID, event type, timestamp, and full task payload
- **Reminder Event**: Represents a scheduled notification for a task, including task ID, user ID, scheduled time, and reminder message
- **Audit Log Entry**: Represents a system event for observability, including event ID, event type, timestamp, service name, correlation ID, and event payload
- **WebSocket Connection**: Represents a real-time connection between frontend and backend for event streaming, including connection ID, user ID, and subscription topics

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: When a task is completed in one browser tab, all other open tabs reflect the change within 2 seconds (measured via automated end-to-end tests)
- **SC-002**: Recurring Task Service successfully processes 100% of task completion events and generates new task instances within 5 seconds
- **SC-003**: Notification Service logs reminder notifications within 1 second of the scheduled time (measured via timestamp comparison)
- **SC-004**: System maintains 99.9% uptime for event processing during normal operation (measured over 24-hour period)
- **SC-005**: Kafka cluster and all Dapr sidecars report healthy status when queried via health check endpoint
- **SC-006**: System handles at least 100 concurrent WebSocket connections without performance degradation
- **SC-007**: Audit Service captures 100% of system events in chronological order without gaps or duplicates
- **SC-008**: System operates within 4GB RAM and 2-CPU resource limits on Minikube (measured via Kubernetes metrics)
- **SC-009**: Event processing latency (from event publication to consumer processing) averages under 500ms for 95% of events
- **SC-010**: System recovers automatically from Kafka broker failures within 30 seconds without data loss

## Assumptions *(optional)*

- Minikube cluster is already installed and running on the local development machine
- Developers have kubectl and Helm v3 CLI tools installed and configured
- The existing FastAPI backend and Next.js frontend are already deployed and operational
- Network connectivity between Minikube pods is reliable with low latency (<10ms)
- System clock synchronization (NTP) is configured across all services to ensure consistent timestamps
- Developers have basic knowledge of Kafka, Dapr, and Kubernetes concepts
- The existing task management API endpoints are compatible with event-driven architecture (can publish events)
- Browser clients support WebSocket or Server-Sent Events (SSE) for real-time communication
- Local development environment has sufficient disk space for Kafka message persistence (minimum 10GB)

## Constraints *(optional)*

- **Resource Limits**: Kafka cluster and all microservices must operate within 4GB RAM and 2-CPU Minikube limits
- **Local Environment**: Solution must run entirely on local Minikube cluster (no cloud dependencies)
- **Tooling**: Must use Strimzi Operator for Kafka, Dapr CLI for service integration, and Helm v3 for packaging
- **Decoupling**: Services must not share databases - all synchronization via Kafka topics only
- **No Production Features**: No real SMTP/push notification integration (logging only), no CI/CD pipelines, no cloud Kubernetes provisioning
- **Documentation**: Must use context7 MCP server for latest Dapr 1.15+ and Next.js 16.1+ documentation
- **KRaft Mode**: Kafka must use KRaft mode (no Zookeeper) for resource efficiency

## Out of Scope *(optional)*

- Cloud-hosted Kafka solutions (Redpanda Cloud, Confluent Cloud)
- Production CI/CD pipelines and automated deployment workflows
- Cloud Kubernetes provisioning (AWS EKS, Azure AKS, Google GKE)
- Real SMTP email integration or mobile push notifications (only logging)
- Advanced Kafka features like Kafka Streams or ksqlDB
- Multi-cluster Kafka replication or disaster recovery
- Advanced monitoring and alerting (Prometheus, Grafana) - basic health checks only
- Load testing and performance optimization beyond basic requirements
- Security hardening (TLS, authentication, authorization) - development environment only
- Data encryption at rest or in transit
