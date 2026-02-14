# Event-Driven Architecture Diagram

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Frontend (Next.js)                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │  Dashboard   │  │  Task Forms  │  │  SSE Client  │  │  Chat UI     │   │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘   │
│         │                  │                  │                  │            │
│         └──────────────────┴──────────────────┴──────────────────┘           │
└─────────────────────────────┬───────────────────────────────────────────────┘
                              │ HTTP/SSE
                              │
┌─────────────────────────────┴───────────────────────────────────────────────┐
│                         Backend API (FastAPI)                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │ Task Router  │  │Events Router │  │Reminder Router│  │  Chat API    │   │
│  │  (CRUD)      │  │  (SSE Bridge)│  │  (Scheduler)  │  │              │   │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────────────┘   │
│         │                  │                  │                              │
│         │          ┌───────┴────────┐         │                              │
│         │          │  Dapr Sidecar  │         │                              │
│         │          │  - Pub/Sub     │         │                              │
│         │          │  - State Store │         │                              │
│         │          │  - Jobs API    │         │                              │
│         │          └───────┬────────┘         │                              │
│         └──────────────────┼──────────────────┘                              │
└────────────────────────────┼─────────────────────────────────────────────────┘
                             │
                    ┌────────┴─────────┐
                    │  Kafka (KRaft)   │
                    │  Strimzi Managed │
                    │  ┌────────────┐  │
                    │  │   Topics   │  │
                    │  │ • tasks    │  │
                    │  │ • reminders│  │
                    │  │ • notifs   │  │
                    │  │ • audit    │  │
                    │  │ • dlq      │  │
                    │  └────────────┘  │
                    └────────┬─────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────┴────────┐  ┌────────┴────────┐  ┌──────┴──────┐
│  Notification  │  │   Recurring     │  │    Audit    │
│    Service     │  │    Service      │  │   Service   │
│  ┌──────────┐  │  │  ┌──────────┐  │  │ ┌─────────┐ │
│  │  Dapr    │  │  │  │  Dapr    │  │  │ │  Dapr   │ │
│  │ Sidecar  │  │  │  │ Sidecar  │  │  │ │Sidecar  │ │
│  └──────────┘  │  │  └──────────┘  │  │ └─────────┘ │
└────────────────┘  └─────────────────┘  └─────────────┘
        │                    │                    │
        │                    │                    │
        ▼                    ▼                    ▼
┌────────────────┐  ┌─────────────────┐  ┌─────────────┐
│   PostgreSQL   │  │   PostgreSQL    │  │ PostgreSQL  │
│  (Reminders)   │  │  (Task State)   │  │ (Audit Log) │
└────────────────┘  └─────────────────┘  └─────────────┘
```

## Event Flow Diagrams

### 1. Task Creation Flow

```
User Action (Create Task)
    │
    ▼
Frontend Dashboard
    │ HTTP POST /api/tasks
    ▼
Backend Task Router
    │ 1. Save to DB
    │ 2. Publish event
    ▼
Dapr Pub/Sub (kafka-pubsub)
    │
    ▼
Kafka Topic: todo.task.events
    │
    ├─────────────────────┬─────────────────────┐
    │                     │                     │
    ▼                     ▼                     ▼
SSE Bridge          Recurring Service     Audit Service
    │                     │                     │
    │ Broadcast           │ Check recurrence    │ Store event
    ▼                     │                     ▼
Connected Clients         │                 PostgreSQL
    │                     │                 (Audit Log)
    ▼                     ▼
All User's Tabs      (No action for
Update in Real-Time   non-recurring)
```

### 2. Task Completion Flow (Recurring Task)

```
User Action (Complete Task)
    │
    ▼
Frontend Dashboard
    │ HTTP PATCH /api/tasks/{id}/complete
    ▼
Backend Task Router
    │ 1. Update status to "completed"
    │ 2. Publish task.completed event
    ▼
Dapr Pub/Sub (kafka-pubsub)
    │
    ▼
Kafka Topic: todo.task.events
    │
    ├─────────────────────┬─────────────────────┐
    │                     │                     │
    ▼                     ▼                     ▼
SSE Bridge          Recurring Service     Audit Service
    │                     │                     │
    │ Broadcast           │ 1. Check recurrence │ Store event
    ▼                     │ 2. Calculate next   ▼
Connected Clients         │    due date         PostgreSQL
    │                     │ 3. Create new task  (Audit Log)
    ▼                     │    via Dapr Service
All User's Tabs           │    Invocation
Update Status             ▼
                    Backend Task Router
                          │ /tasks/internal
                          │ 1. Create new task
                          │ 2. Publish task.created
                          ▼
                    Kafka Topic: todo.task.events
                          │
                          ▼
                    SSE Bridge → All Tabs
                    (New task appears)
```

### 3. Reminder Notification Flow

```
User Action (Create Task with Reminder)
    │
    ▼
Backend Task Router
    │ 1. Create task
    │ 2. Schedule reminder via Dapr Jobs API
    ▼
Dapr Jobs API
    │ Store job with scheduled time
    ▼
(Wait until scheduled time)
    │
    ▼
Dapr Jobs API (Fires at scheduled time)
    │ HTTP POST /api/reminders/callback
    ▼
Backend Reminder Router
    │ 1. Publish reminder.fired event
    ▼
Kafka Topic: todo.reminders
    │
    ▼
Notification Service
    │ 1. Process reminder
    │ 2. Log notification
    │ 3. Publish notification.sent event
    ▼
Kafka Topic: todo.notifications
    │
    ▼
Audit Service
    │ Store notification event
    ▼
PostgreSQL (Audit Log)
```

### 4. Error Handling Flow (DLQ)

```
Event Processing Error
    │
    ▼
Event Consumer (Any Service)
    │ 1. Catch exception
    │ 2. Retry with exponential backoff
    │    (3 attempts)
    ▼
Still Failing?
    │ Yes
    ▼
DLQ Handler
    │ 1. Enrich event with error metadata
    │ 2. Publish to DLQ topic
    ▼
Kafka Topic: todo.task.events.dlq
    │
    ▼
DLQ Handler Service
    │ 1. Log to file
    │ 2. Alert monitoring
    │ 3. Manual intervention required
```

## Component Interactions

### Dapr Components Used

1. **kafka-pubsub** (Pub/Sub Component)
   - Type: `pubsub.kafka`
   - Used by: All services for event publishing/subscribing
   - Topics: task.events, reminders, notifications, audit.events, dlq

2. **statestore** (State Store Component)
   - Type: `state.postgresql`
   - Used by: All services for idempotency tracking
   - Keys: `idempotency:{correlation_id}`

3. **secretstore** (Secret Store Component)
   - Type: `secretstores.kubernetes`
   - Used by: All services for database credentials

4. **tracing-config** (Configuration Component)
   - Type: `configuration`
   - Used by: All services for distributed tracing
   - Sends traces to Zipkin

### Service Communication Patterns

1. **Synchronous**: Frontend ↔ Backend API (HTTP/REST)
2. **Asynchronous**: Backend → Kafka → Microservices (Event-Driven)
3. **Real-Time**: Backend → Frontend (Server-Sent Events)
4. **Service-to-Service**: Recurring Service → Backend API (Dapr Service Invocation)
5. **Scheduled**: Dapr Jobs API → Backend API (HTTP Callback)

## Resilience Patterns

1. **Idempotency**: Correlation ID tracking in Dapr State Store
2. **Retry**: Exponential backoff (3 attempts, 1s → 2s → 4s)
3. **Dead Letter Queue**: Failed events after max retries
4. **Circuit Breaker**: Protect service invocation calls
5. **Graceful Degradation**: Local event queue when Kafka unavailable
6. **Rate Limiting**: Max 100 concurrent SSE connections per user

## Monitoring & Observability

1. **Distributed Tracing**: OpenTelemetry → Zipkin
2. **Metrics**: Prometheus metrics exposed at `/metrics`
3. **Structured Logging**: JSON logs with correlation IDs
4. **Health Checks**: `/health` endpoints on all services
5. **Audit Trail**: All events logged to PostgreSQL (30-day retention)

## Security

1. **Authentication**: JWT tokens (cookie + query parameter for SSE)
2. **Authorization**: User ID verification for all operations
3. **Secrets Management**: Kubernetes secrets via Dapr
4. **Network Policies**: Pod-to-pod communication restrictions
5. **Resource Limits**: CPU/memory limits on all pods
