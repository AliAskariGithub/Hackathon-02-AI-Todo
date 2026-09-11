# Phase 0: Research Findings

**Feature**: Local Event-Driven Backbone
**Date**: 2026-02-13
**Status**: Complete

## Research Overview

This document captures findings from Phase 0 research tasks required for implementing the event-driven architecture with Kafka, Dapr, and real-time UI updates.

---

## 1. Strimzi Kafka KRaft Configuration for Resource-Constrained Environments

### Research Question
Optimal Kafka broker configuration for 4GB RAM / 2-CPU Minikube cluster using Strimzi Operator in KRaft mode.

### Findings

**KRaft Controller Quorum Size**:
- **Decision**: Use 1 combined controller+broker node for local development
- **Rationale**: Single-node KRaft mode minimizes resource overhead while maintaining functionality
- **Production Note**: 3-node quorum recommended for production environments

**Memory and CPU Limits**:
```yaml
resources:
  requests:
    memory: "512Mi"
    cpu: "250m"
  limits:
    memory: "1Gi"
    cpu: "500m"
```

**JVM Heap Settings**:
- Heap Size: 256MB-512MB for local development
- Environment Variable: `KAFKA_HEAP_OPTS="-Xms256m -Xmx512m"`
- Rationale: Leaves sufficient memory for OS and other pods

**Strimzi Kafka Custom Resource**:
```yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: Kafka
metadata:
  name: ai-todo-kafka
spec:
  kafka:
    version: 3.6.0
    replicas: 1
    listeners:
      - name: plain
        port: 9092
        type: internal
        tls: false
    config:
      offsets.topic.replication.factor: 1
      transaction.state.log.replication.factor: 1
      transaction.state.log.min.isr: 1
      default.replication.factor: 1
      min.insync.replicas: 1
      log.retention.hours: 168  # 7 days
    storage:
      type: ephemeral
    resources:
      requests:
        memory: 512Mi
        cpu: 250m
      limits:
        memory: 1Gi
        cpu: 500m
    jvmOptions:
      -Xms: 256m
      -Xmx: 512m
  entityOperator:
    topicOperator: {}
    userOperator: {}
```

**Key Configuration Decisions**:
- Replication factor: 1 (single broker, no replication needed)
- Storage: Ephemeral (acceptable for local development)
- Retention: 7 days for task events, 30 days for audit events (configured per topic)

---

## 2. Dapr Python SDK Async Pub/Sub Patterns

### Research Question
Best practices for Dapr Python SDK (v1.14+) async/await patterns for event publishing and subscribing in FastAPI.

### Findings

**Event Publishing Pattern**:
```python
from dapr.clients import DaprClient
from dapr.ext.fastapi import DaprApp
import json

async def publish_task_event(event_type: str, task_data: dict, user_id: str):
    """Publish task event to Kafka via Dapr Pub/Sub"""
    with DaprClient() as client:
        event = {
            "event_type": event_type,
            "payload": task_data,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "correlation_id": str(uuid.uuid4())
        }

        # Publish to Dapr Pub/Sub component
        client.publish_event(
            pubsub_name="kafka-pubsub",
            topic_name="todo.task.events",
            data=json.dumps(event),
            data_content_type="application/json"
        )
```

**Event Subscription Pattern (FastAPI)**:
```python
from dapr.ext.fastapi import DaprApp
from fastapi import FastAPI

app = FastAPI()
dapr_app = DaprApp(app)

@dapr_app.subscribe(
    pubsub="kafka-pubsub",
    topic="todo.task.events",
    route="/events/task-completed"
)
async def handle_task_completed(event_data: dict):
    """Handle task.completed events for recurring task generation"""
    try:
        event = event_data.get("data", {})

        # Idempotency check using correlation_id
        correlation_id = event.get("correlation_id")
        if await is_event_processed(correlation_id):
            return {"status": "success", "message": "Event already processed"}

        # Process event
        if event.get("event_type") == "task.completed":
            task_data = event.get("payload", {})
            if task_data.get("is_recurring"):
                await generate_next_recurring_task(task_data)

        # Mark event as processed
        await mark_event_processed(correlation_id)

        return {"status": "success"}
    except Exception as e:
        # Log error and return failure for retry
        logger.error(f"Event processing failed: {e}")
        return {"status": "retry"}
```

**Idempotency Implementation**:
```python
# Using Dapr State Store for idempotency tracking
from dapr.clients import DaprClient

async def is_event_processed(correlation_id: str) -> bool:
    """Check if event has been processed using Dapr State Store"""
    with DaprClient() as client:
        state = client.get_state(
            store_name="statestore",
            key=f"processed_event_{correlation_id}"
        )
        return state.data is not None

async def mark_event_processed(correlation_id: str):
    """Mark event as processed in Dapr State Store"""
    with DaprClient() as client:
        client.save_state(
            store_name="statestore",
            key=f"processed_event_{correlation_id}",
            value="processed",
            state_metadata={"ttl": "86400"}  # 24 hour TTL
        )
```

**Error Handling and Retry Strategy**:
- Return `{"status": "success"}` for successful processing
- Return `{"status": "retry"}` for transient failures (triggers Dapr retry)
- Return `{"status": "drop"}` for permanent failures (moves to dead letter queue)
- Configure retry policy in Dapr subscription metadata

**Key Decisions**:
- Use synchronous `DaprClient()` context manager for publishing (simpler, sufficient for low volume)
- Use `@dapr_app.subscribe` decorator for FastAPI route-based subscriptions
- Implement idempotency using Dapr State Store with TTL
- Use correlation IDs for event deduplication

---

## 3. Next.js 16.1.2 Server-Sent Events (SSE) Implementation

### Research Question
Best practices for implementing Server-Sent Events in Next.js 16 App Router for real-time task updates.

### Findings

**SSE Route Handler (Next.js 16 App Router)**:
```typescript
// app/api/events/route.ts
import { NextRequest } from 'next/server';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function GET(request: NextRequest) {
  // Verify JWT token from query params or headers
  const token = request.nextUrl.searchParams.get('token');
  if (!token || !verifyJWT(token)) {
    return new Response('Unauthorized', { status: 401 });
  }

  const userId = getUserIdFromToken(token);

  // Create ReadableStream for SSE
  const stream = new ReadableStream({
    start(controller) {
      // Send initial connection message
      controller.enqueue(`data: ${JSON.stringify({ type: 'connected' })}\n\n`);

      // Subscribe to Kafka events via backend API
      const eventSource = subscribeToTaskEvents(userId);

      eventSource.on('message', (event: any) => {
        // Forward event to client
        controller.enqueue(`data: ${JSON.stringify(event)}\n\n`);
      });

      eventSource.on('error', (error: any) => {
        console.error('SSE error:', error);
        controller.close();
      });

      // Cleanup on connection close
      request.signal.addEventListener('abort', () => {
        eventSource.close();
        controller.close();
      });
    }
  });

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
    },
  });
}
```

**Client-Side EventSource Implementation**:
```typescript
// hooks/useTaskEvents.ts
import { useEffect, useState } from 'react';

export function useTaskEvents(token: string) {
  const [events, setEvents] = useState<any[]>([]);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    const eventSource = new EventSource(
      `/api/events?token=${encodeURIComponent(token)}`
    );

    eventSource.onopen = () => {
      setIsConnected(true);
      console.log('SSE connection established');
    };

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setEvents((prev) => [...prev, data]);

      // Handle different event types
      if (data.event_type === 'task.updated') {
        // Update task in local state
        updateTaskInCache(data.payload);
      }
    };

    eventSource.onerror = (error) => {
      console.error('SSE error:', error);
      setIsConnected(false);
      eventSource.close();

      // Automatic reconnection after 5 seconds
      setTimeout(() => {
        window.location.reload();
      }, 5000);
    };

    return () => {
      eventSource.close();
    };
  }, [token]);

  return { events, isConnected };
}
```

**Authentication Strategy**:
- **Decision**: Pass JWT token as query parameter for SSE connection
- **Rationale**: EventSource API doesn't support custom headers, query params are the standard approach
- **Security**: Token validated on server before establishing connection

**Reconnection Handling**:
- EventSource API provides automatic reconnection by default
- Implement custom reconnection logic with exponential backoff for better control
- Display connection status indicator in UI

**Key Decisions**:
- Use Next.js 16 Route Handlers with `ReadableStream` for SSE
- Pass JWT token via query parameter (EventSource limitation)
- Implement automatic reconnection with 5-second delay
- Use `force-dynamic` to prevent route caching

---

## 4. Kafka Topic Retention and Partition Configuration

### Research Question
Recommended retention policies and partition strategies for event-driven task management system.

### Findings

**Retention Policies**:
- **Task Events** (`todo.task.events`): 7 days retention
  - Rationale: Short-lived operational events, no long-term replay needed
  - Configuration: `retention.ms=604800000` (7 days in milliseconds)

- **Audit Events** (`todo.audit.events`): 30 days retention
  - Rationale: Compliance and debugging require longer history
  - Configuration: `retention.ms=2592000000` (30 days in milliseconds)

- **Reminder Events** (`todo.reminders`): 1 day retention
  - Rationale: Reminders are time-sensitive, no replay needed after execution
  - Configuration: `retention.ms=86400000` (1 day in milliseconds)

**Partition Configuration**:
- **Task Events Topic**: 3 partitions
  - Partition Key: `user_id` (ensures all events for a user go to same partition)
  - Rationale: Balances load distribution with ordering guarantees per user

- **Reminder Events Topic**: 1 partition
  - Partition Key: None (round-robin)
  - Rationale: Strict ordering required for scheduled reminders

- **Audit Events Topic**: 1 partition
  - Partition Key: None (round-robin)
  - Rationale: Chronological ordering required for audit trail

**Dead Letter Queue Configuration**:
```yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: todo.task.events.dlq
spec:
  partitions: 1
  replicas: 1
  config:
    retention.ms: 604800000  # 7 days
    cleanup.policy: delete
```

**Topic Creation (Strimzi KafkaTopic CRD)**:
```yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: todo.task.events
  labels:
    strimzi.io/cluster: ai-todo-kafka
spec:
  partitions: 3
  replicas: 1
  config:
    retention.ms: 604800000
    segment.bytes: 1073741824
    cleanup.policy: delete
```

**Key Decisions**:
- Use `user_id` as partition key for task events (ordering per user)
- 3 partitions for task events (balances load with resource constraints)
- 1 partition for reminders and audit (strict ordering)
- 7-day retention for operational events, 30-day for audit

---

## 5. Dapr Distributed Tracing Configuration

### Research Question
Dapr Configuration for OpenTelemetry tracing with correlation ID propagation.

### Findings

**Dapr Configuration YAML**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Configuration
metadata:
  name: tracing-config
spec:
  tracing:
    samplingRate: "1"  # 100% sampling for development
    otel:
      endpointAddress: "http://zipkin.default.svc.cluster.local:9411/api/v2/spans"
      isSecure: false
      protocol: http
  metric:
    enabled: true
```

**Sampling Strategies**:
- **Development**: 100% sampling (`samplingRate: "1"`)
- **Production**: Adaptive sampling (10-20%, `samplingRate: "0.1"`)
- **Rationale**: Full tracing in dev for debugging, reduced overhead in production

**Trace Context Propagation**:
- Dapr automatically propagates trace context via W3C Trace Context headers
- Headers: `traceparent`, `tracestate`
- Correlation IDs included in trace spans automatically

**Correlation ID Generation**:
```python
import uuid
from opentelemetry import trace

def generate_correlation_id() -> str:
    """Generate correlation ID and add to trace span"""
    correlation_id = str(uuid.uuid4())

    # Add correlation ID to current trace span
    span = trace.get_current_span()
    span.set_attribute("correlation_id", correlation_id)

    return correlation_id
```

**Zipkin Deployment (Optional for Local Development)**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: zipkin
spec:
  replicas: 1
  selector:
    matchLabels:
      app: zipkin
  template:
    metadata:
      labels:
        app: zipkin
    spec:
      containers:
      - name: zipkin
        image: openzipkin/zipkin:latest
        ports:
        - containerPort: 9411
---
apiVersion: v1
kind: Service
metadata:
  name: zipkin
spec:
  selector:
    app: zipkin
  ports:
  - port: 9411
    targetPort: 9411
```

**Key Decisions**:
- Use Zipkin as tracing backend (lightweight, easy to deploy)
- 100% sampling in development for full visibility
- Dapr handles trace context propagation automatically
- Correlation IDs added as span attributes for cross-service tracing

---

## Summary of Key Decisions

| Area | Decision | Rationale |
|------|----------|-----------|
| Kafka Deployment | Single-node KRaft mode | Minimizes resource usage for local development |
| Kafka Memory | 512MB-1GB with 256-512MB heap | Fits within 4GB Minikube constraint |
| Event Publishing | Synchronous DaprClient | Simpler implementation, sufficient for low volume |
| Event Subscription | FastAPI route-based with @dapr_app.subscribe | Native Dapr integration with FastAPI |
| Idempotency | Dapr State Store with correlation IDs | Prevents duplicate event processing |
| SSE Implementation | Next.js Route Handlers with ReadableStream | Native Next.js 16 App Router support |
| SSE Authentication | JWT token in query parameter | EventSource API limitation |
| Task Events Retention | 7 days | Short-lived operational events |
| Audit Events Retention | 30 days | Compliance and debugging requirements |
| Task Events Partitions | 3 partitions with user_id key | Balances load with ordering per user |
| Reminder Partitions | 1 partition | Strict ordering for scheduled tasks |
| Tracing Backend | Zipkin | Lightweight, easy to deploy locally |
| Tracing Sampling | 100% in dev, 10-20% in prod | Full visibility vs performance tradeoff |

---

## Next Steps

1. ✅ Research complete - all 5 research tasks documented
2. Create `data-model.md` with event schemas and entity relationships
3. Create `contracts/` directory with API specifications
4. Create `quickstart.md` with local setup guide
5. Proceed to `/sp.tasks` for task generation

---

**Research Status**: Complete
**Ready for Phase 1**: Yes
**Blockers**: None
