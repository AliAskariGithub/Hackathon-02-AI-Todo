# Research: Dapr SDK Integration & Event-Driven Architecture

**Feature**: Advanced Task Management with Infrastructure Abstraction
**Date**: 2026-02-11
**Purpose**: Document technical decisions for Dapr Python SDK integration, Next.js Service Invocation, and event-driven architecture patterns

## 1. Dapr Python SDK Integration with FastAPI

### Decision: Use `dapr-ext-fastapi` Extension

**Rationale**:
- Official Dapr extension for FastAPI provides native integration
- Automatic Dapr client initialization and dependency injection
- Built-in middleware for Dapr Pub/Sub subscriptions
- Simplified error handling and retry logic

**Implementation Pattern**:
```python
from fastapi import FastAPI
from dapr.ext.fastapi import DaprApp

app = FastAPI()
dapr_app = DaprApp(app)

# Dapr client available via dependency injection
from dapr.clients import DaprClient

async def get_dapr_client():
    with DaprClient() as client:
        yield client
```

**Alternatives Considered**:
- Direct `DaprClient` usage without extension: More boilerplate, manual subscription registration
- Custom wrapper layer: Unnecessary complexity, reinventing official patterns

### Decision: Dapr State API for PostgreSQL Access

**Rationale**:
- Eliminates direct SQLAlchemy/psycopg2 dependencies
- Automatic connection pooling and retry logic
- Cloud-agnostic (can swap PostgreSQL for Redis with zero code changes)
- Built-in transaction support via bulk operations

**Implementation Pattern**:
```python
from dapr.clients import DaprClient

async def save_task(task_data: dict):
    async with DaprClient() as client:
        await client.save_state(
            store_name="statestore",
            key=f"task:{task_data['id']}",
            value=task_data,
            state_metadata={"contentType": "application/json"}
        )

async def get_task(task_id: str):
    async with DaprClient() as client:
        state = await client.get_state(
            store_name="statestore",
            key=f"task:{task_id}"
        )
        return state.data
```

**Alternatives Considered**:
- Direct PostgreSQL access via SQLModel: Violates Phase-V constitution (no direct infrastructure dependencies)
- Hybrid approach (Dapr + SQLModel): Adds complexity, defeats purpose of abstraction

### Decision: Dapr Pub/Sub API for Event Streaming

**Rationale**:
- Decouples application from Kafka-specific APIs
- Automatic message serialization/deserialization
- Built-in retry and dead letter queue support
- Topic-based routing with metadata filtering

**Implementation Pattern**:
```python
# Publishing events
async def publish_task_created_event(task_data: dict):
    event = {
        "event_type": "todo.task.created",
        "payload": task_data,
        "user_id": task_data["user_id"],
        "timestamp": datetime.utcnow().isoformat(),
        "correlation_id": str(uuid.uuid4())
    }

    async with DaprClient() as client:
        await client.publish_event(
            pubsub_name="pubsub",
            topic_name="todo.task.created",
            data=json.dumps(event),
            data_content_type="application/json"
        )

# Subscribing to events
@dapr_app.subscribe(pubsub_name="pubsub", topic="todo.task.completed")
async def handle_task_completed(event_data: dict):
    # Idempotency check via correlation_id
    correlation_id = event_data.get("correlation_id")
    if await is_already_processed(correlation_id):
        return {"status": "already_processed"}

    # Generate next recurring instance
    if event_data["payload"].get("recurrence"):
        await generate_next_task_instance(event_data["payload"])

    return {"status": "success"}
```

**Alternatives Considered**:
- Direct Kafka client (kafka-python): Violates constitution, tight coupling
- Custom event bus abstraction: Unnecessary, Dapr already provides this

### Decision: Dapr Secrets API for Configuration

**Rationale**:
- Eliminates direct environment variable access
- Supports multiple secret stores (Kubernetes, Azure Key Vault, AWS Secrets Manager)
- Automatic secret rotation support
- Centralized secret management

**Implementation Pattern**:
```python
async def get_database_url():
    async with DaprClient() as client:
        secret = await client.get_secret(
            store_name="secretstore",
            key="DATABASE_URL"
        )
        return secret.secret["DATABASE_URL"]

# Usage in application startup
@app.on_event("startup")
async def configure_database():
    db_url = await get_database_url()
    # Configure connection pool with retrieved URL
```

**Alternatives Considered**:
- Direct environment variables: Violates Phase-V constitution
- Config files: Less secure, no rotation support

### Decision: Dapr Jobs API for Reminder Scheduling

**Rationale**:
- Exact-time scheduling (no polling required per constitution)
- Automatic retry and failure handling
- Distributed scheduling (works across multiple pods)
- ISO 8601 datetime format support

**Implementation Pattern**:
```python
async def schedule_reminder(task_id: str, reminder_time: datetime):
    job_data = {
        "task_id": task_id,
        "scheduled_time": reminder_time.isoformat()
    }

    async with DaprClient() as client:
        await client.schedule_job(
            job_name=f"reminder-{task_id}",
            schedule=reminder_time.isoformat(),  # ISO 8601 format
            data=json.dumps(job_data),
            callback_url="/api/reminders/callback"
        )

# Callback endpoint
@app.post("/api/reminders/callback")
async def reminder_callback(job_data: dict):
    task_id = job_data["task_id"]
    # Send notification (mock logger in this spec)
    logger.info(f"Reminder fired for task {task_id}")
    return {"status": "success"}
```

**Alternatives Considered**:
- Polling-based cron jobs: PROHIBITED by Phase-V constitution
- APScheduler: Doesn't work in distributed environment, no Dapr integration

## 2. Next.js 16.1.2 with Dapr Service Invocation

### Decision: HTTP-based Dapr Service Invocation

**Rationale**:
- Next.js frontend can call Dapr sidecar on localhost:3500
- No need for direct backend URL (Dapr handles service discovery)
- Automatic retry and circuit breaker patterns
- Works with Next.js Server Actions and API routes

**Implementation Pattern**:
```typescript
// services/dapr_client.ts
const DAPR_SIDECAR_URL = process.env.NEXT_PUBLIC_DAPR_SIDECAR_URL || 'http://localhost:3500';
const BACKEND_APP_ID = 'backend';

export async function invokeDaprService<T>(
  method: string,
  path: string,
  data?: any
): Promise<T> {
  const url = `${DAPR_SIDECAR_URL}/v1.0/invoke/${BACKEND_APP_ID}/method${path}`;

  const response = await fetch(url, {
    method,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${getAuthToken()}`
    },
    body: data ? JSON.stringify(data) : undefined
  });

  if (!response.ok) {
    throw new Error(`Dapr invocation failed: ${response.statusText}`);
  }

  return response.json();
}

// Usage in Server Action
export async function createTask(formData: FormData) {
  'use server';

  const taskData = {
    title: formData.get('title'),
    priority: formData.get('priority'),
    recurrence: formData.get('recurrence')
  };

  const result = await invokeDaprService('POST', '/api/tasks', taskData);
  revalidatePath('/tasks');
  return result;
}
```

**Alternatives Considered**:
- Direct backend HTTP calls: Bypasses Dapr benefits (retry, tracing, service discovery)
- gRPC: More complex, HTTP sufficient for this use case

### Decision: Server Actions for Mutations

**Rationale**:
- Next.js 16 App Router best practice for form submissions
- Automatic revalidation and cache management
- Type-safe with TypeScript
- Works seamlessly with Dapr Service Invocation

**Implementation Pattern**:
```typescript
// app/tasks/actions.ts
'use server';

export async function updateTaskPriority(taskId: string, priority: string) {
  await invokeDaprService('PATCH', `/api/tasks/${taskId}`, { priority });
  revalidatePath('/tasks');
}

// Usage in component
<form action={async (formData) => {
  await updateTaskPriority(taskId, formData.get('priority'));
}}>
  <select name="priority">
    <option value="High">High</option>
    <option value="Medium">Medium</option>
    <option value="Low">Low</option>
  </select>
  <button type="submit">Update</button>
</form>
```

**Alternatives Considered**:
- Client-side fetch: Less optimal for mutations, no automatic revalidation
- API routes: Extra layer, Server Actions more direct

## 3. Event-Driven Architecture Patterns

### Decision: Decorator-Based Event Subscriptions

**Rationale**:
- Clean, declarative syntax
- Automatic subscription registration on app startup
- Built-in error handling and retry logic
- Supports metadata filtering

**Implementation Pattern**:
```python
from dapr.ext.fastapi import DaprApp

@dapr_app.subscribe(
    pubsub_name="pubsub",
    topic="todo.task.completed",
    metadata={"rawPayload": "true"}
)
async def on_task_completed(event: dict):
    # Idempotency check
    correlation_id = event.get("correlation_id")
    if await is_duplicate(correlation_id):
        return {"status": "duplicate"}

    # Process event
    await handle_recurring_task_generation(event)

    return {"status": "success"}
```

**Alternatives Considered**:
- Manual subscription registration: More boilerplate, error-prone
- Polling-based event consumption: Inefficient, violates constitution

### Decision: Correlation ID for Idempotency

**Rationale**:
- Prevents duplicate task generation on event replay
- Enables distributed tracing across services
- Standard pattern for event-driven systems

**Implementation Pattern**:
```python
# Store processed correlation IDs in state store
async def is_duplicate(correlation_id: str) -> bool:
    async with DaprClient() as client:
        state = await client.get_state(
            store_name="statestore",
            key=f"processed:{correlation_id}"
        )
        return state.data is not None

async def mark_as_processed(correlation_id: str):
    async with DaprClient() as client:
        await client.save_state(
            store_name="statestore",
            key=f"processed:{correlation_id}",
            value={"processed_at": datetime.utcnow().isoformat()},
            state_metadata={"ttlInSeconds": "86400"}  # 24 hour TTL
        )
```

**Alternatives Considered**:
- Database-based deduplication: Requires direct DB access, violates abstraction
- In-memory cache: Doesn't work in distributed environment

## 4. Dapr Component Configuration

### Decision: YAML-based Component Definitions

**Rationale**:
- Declarative infrastructure configuration
- Version-controlled alongside application code
- Easy to swap providers (Kafka → Redpanda) by changing YAML
- Kubernetes-native deployment

**PostgreSQL State Store Component**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
  namespace: default
spec:
  type: state.postgresql
  version: v1
  metadata:
  - name: connectionString
    secretKeyRef:
      name: dapr-secrets
      key: DATABASE_URL
  - name: tableName
    value: "dapr_state"
  - name: keyPrefix
    value: "todo"
```

**Kafka Pub/Sub Component**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub
  namespace: default
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    secretKeyRef:
      name: dapr-secrets
      key: KAFKA_BOOTSTRAP_SERVERS
  - name: consumerGroup
    value: "todo-backend"
  - name: authType
    value: "none"  # Update for production
```

**Kubernetes Secrets Component**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: secretstore
  namespace: default
spec:
  type: secretstores.kubernetes
  version: v1
  metadata:
  - name: vaultName
    value: "default"
```

**Alternatives Considered**:
- Programmatic component registration: Less portable, harder to manage
- Environment-specific components: Increases complexity, YAML sufficient

## 5. Testing Strategies

### Decision: Dapr Mock Components for Unit Tests

**Rationale**:
- Test application logic without infrastructure dependencies
- Fast test execution
- Deterministic test results

**Implementation Pattern**:
```python
# tests/conftest.py
import pytest
from unittest.mock import AsyncMock, patch

@pytest.fixture
def mock_dapr_client():
    with patch('dapr.clients.DaprClient') as mock:
        client = AsyncMock()
        mock.return_value.__aenter__.return_value = client
        yield client

# tests/unit/test_recurrence_logic.py
async def test_daily_recurrence_calculation(mock_dapr_client):
    # Mock state store responses
    mock_dapr_client.get_state.return_value.data = {
        "id": "task-123",
        "recurrence": "Daily",
        "due_date": "2026-02-11"
    }

    # Test recurring task generation
    next_task = await generate_next_task_instance("task-123")

    assert next_task["due_date"] == "2026-02-12"
    mock_dapr_client.save_state.assert_called_once()
```

**Alternatives Considered**:
- Integration tests only: Slow, requires infrastructure
- Custom mocking framework: Unnecessary, standard mocks sufficient

### Decision: Integration Tests with Dapr Sidecars

**Rationale**:
- Validate actual Dapr integration
- Test event flows end-to-end
- Catch configuration issues early

**Implementation Pattern**:
```python
# tests/integration/test_dapr_pubsub.py
import pytest
from dapr.clients import DaprClient

@pytest.mark.integration
async def test_task_completed_event_triggers_recurrence():
    # Publish event
    async with DaprClient() as client:
        await client.publish_event(
            pubsub_name="pubsub",
            topic_name="todo.task.completed",
            data=json.dumps({
                "event_type": "todo.task.completed",
                "payload": {
                    "task_id": "task-123",
                    "recurrence": "Daily"
                },
                "correlation_id": str(uuid.uuid4())
            })
        )

    # Wait for event processing
    await asyncio.sleep(2)

    # Verify next instance created
    async with DaprClient() as client:
        state = await client.get_state(
            store_name="statestore",
            key="task:task-123-next"
        )
        assert state.data is not None
```

**Alternatives Considered**:
- Mock-only testing: Doesn't catch integration issues
- Manual testing: Not repeatable, error-prone

## 6. Architecture Decision Summary

| Decision Area | Choice | Rationale |
|--------------|--------|-----------|
| Backend Framework | FastAPI + dapr-ext-fastapi | Official Dapr integration, async support |
| State Management | Dapr State API → PostgreSQL | Cloud-agnostic, zero direct DB dependencies |
| Event Streaming | Dapr Pub/Sub API → Kafka | Decoupled, swappable providers |
| Secret Management | Dapr Secrets API → K8s Secrets | Centralized, rotation support |
| Reminder Scheduling | Dapr Jobs API | Exact-time scheduling, no polling |
| Frontend Communication | Dapr Service Invocation | Service discovery, retry logic |
| Event Subscriptions | Decorator-based | Clean syntax, automatic registration |
| Idempotency | Correlation ID + State Store | Prevents duplicates, distributed-safe |
| Testing | Mock components + Integration | Fast unit tests, validated integration |
| Component Config | YAML manifests | Declarative, version-controlled |

## 7. Implementation Phases

**Phase 1: Foundation**
- Set up Dapr sidecar injection in Kubernetes
- Create Dapr component YAML files
- Implement Dapr SDK utility wrappers

**Phase 2: State Migration**
- Refactor task CRUD to use Dapr State API
- Remove direct PostgreSQL dependencies
- Migrate secrets to Dapr Secrets API

**Phase 3: Event-Driven Features**
- Implement event publishing for task lifecycle
- Add event subscriptions for recurring tasks
- Integrate Dapr Jobs API for reminders

**Phase 4: Frontend Integration**
- Implement Dapr Service Invocation client
- Update Next.js components to use Dapr
- Add connectivity tests

## 8. Risk Mitigation

**Risk**: Dapr sidecar unavailable
**Mitigation**: Implement circuit breaker pattern, graceful degradation

**Risk**: Event processing failures
**Mitigation**: Dead letter queue configuration, automatic retry with exponential backoff

**Risk**: State store connection issues
**Mitigation**: Dapr built-in retry logic, connection pooling

**Risk**: Jobs API callback failures
**Mitigation**: Retry configuration, idempotent callback handlers

## 9. Performance Considerations

- **State Store**: Use bulk operations for batch reads/writes
- **Pub/Sub**: Configure appropriate consumer group settings
- **Jobs API**: Limit concurrent job executions
- **Service Invocation**: Set appropriate timeouts (5s default)

## 10. Security Considerations

- All secrets accessed via Dapr Secrets API (no environment variables)
- JWT validation on all API endpoints
- Correlation IDs for audit trails
- Network policies to restrict pod-to-pod communication
