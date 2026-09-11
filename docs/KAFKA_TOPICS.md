# Kafka Topics Documentation

## Overview

This document describes all Kafka topics used in the AI Todo Event-Driven Architecture, their purposes, schemas, retention policies, and usage patterns.

## Topic List

| Topic Name | Partitions | Retention | Purpose |
|------------|------------|-----------|---------|
| `todo.task.events` | 3 | 7 days | Task lifecycle events (create, update, complete, delete) |
| `todo.reminders` | 1 | 1 day | Reminder scheduling and firing events |
| `todo.notifications` | 1 | 7 days | Notification delivery events |
| `todo.audit.events` | 1 | 30 days | System-wide audit trail events |
| `todo.task.events.dlq` | 1 | 7 days | Dead letter queue for failed task events |

---

## Topic Details

### 1. todo.task.events

**Purpose**: Carries all task lifecycle events for real-time synchronization across browser tabs and microservices.

**Partitions**: 3 (for parallel processing and load distribution)

**Retention**: 7 days (604800000 ms)

**Producers**:
- Backend API (task router endpoints)
- Recurring Service (generates new task instances)

**Consumers**:
- SSE Bridge (forwards to frontend clients)
- Recurring Service (listens for task.completed events)
- Audit Service (logs all events)

**Event Types**:

#### task.created
```json
{
  "event_type": "todo.task.created",
  "payload": {
    "task_id": "uuid",
    "user_id": "uuid",
    "task_data": {
      "title": "string",
      "description": "string",
      "status": "pending",
      "priority": "High|Medium|Low",
      "due_date": "ISO8601",
      "recurrence": "Daily|Weekly|Monthly|null",
      "recurrence_day_of_week": "0-6|null",
      "recurrence_day_of_month": "1-31|null",
      "tags": ["string"],
      "created_at": "ISO8601",
      "parent_task_id": "uuid|null"
    }
  },
  "timestamp": "ISO8601",
  "correlation_id": "uuid"
}
```

#### task.updated
```json
{
  "event_type": "todo.task.updated",
  "payload": {
    "task_id": "uuid",
    "user_id": "uuid",
    "task_data": {
      "title": "string",
      "description": "string",
      "status": "pending|in_progress|completed",
      "priority": "High|Medium|Low",
      "due_date": "ISO8601",
      "updated_at": "ISO8601"
    }
  },
  "timestamp": "ISO8601",
  "correlation_id": "uuid"
}
```

#### task.completed
```json
{
  "event_type": "todo.task.completed",
  "payload": {
    "task_id": "uuid",
    "user_id": "uuid",
    "task_data": {
      "title": "string",
      "status": "completed",
      "completed_at": "ISO8601",
      "recurrence": "Daily|Weekly|Monthly|null",
      "recurrence_day_of_week": "0-6|null",
      "recurrence_day_of_month": "1-31|null",
      "parent_task_id": "uuid|null"
    }
  },
  "timestamp": "ISO8601",
  "correlation_id": "uuid"
}
```

#### task.deleted
```json
{
  "event_type": "todo.task.deleted",
  "payload": {
    "task_id": "uuid",
    "user_id": "uuid",
    "task_data": {
      "title": "string",
      "deleted_at": "ISO8601"
    }
  },
  "timestamp": "ISO8601",
  "correlation_id": "uuid"
}
```

**Usage Patterns**:
- High throughput during peak hours (100-500 events/minute)
- Bursty traffic when users complete multiple tasks
- Requires ordered processing per user (partition by user_id)

---

### 2. todo.reminders

**Purpose**: Handles reminder scheduling and notification events.

**Partitions**: 1 (low volume, order preservation important)

**Retention**: 1 day (86400000 ms) - short retention as reminders are time-sensitive

**Producers**:
- Backend API (reminder service)
- Notification Service (reminder.fired events)

**Consumers**:
- Notification Service (processes scheduled reminders)
- Audit Service (logs reminder events)

**Event Types**:

#### reminder.scheduled
```json
{
  "event_type": "todo.reminder.scheduled",
  "payload": {
    "reminder_id": "uuid",
    "task_id": "uuid",
    "user_id": "uuid",
    "scheduled_time": "ISO8601",
    "job_name": "string"
  },
  "timestamp": "ISO8601",
  "correlation_id": "uuid"
}
```

#### reminder.fired
```json
{
  "event_type": "todo.reminder.fired",
  "payload": {
    "reminder_id": "uuid",
    "task_id": "uuid",
    "user_id": "uuid",
    "scheduled_time": "ISO8601",
    "actual_time": "ISO8601",
    "time_difference_seconds": "float"
  },
  "timestamp": "ISO8601",
  "correlation_id": "uuid"
}
```

#### reminder.cancelled
```json
{
  "event_type": "todo.reminder.cancelled",
  "payload": {
    "reminder_id": "uuid",
    "task_id": "uuid",
    "user_id": "uuid",
    "cancelled_at": "ISO8601"
  },
  "timestamp": "ISO8601",
  "correlation_id": "uuid"
}
```

**Usage Patterns**:
- Low volume (10-50 events/hour)
- Time-critical processing (1-second accuracy requirement)
- Requires Dapr Jobs API integration

---

### 3. todo.notifications

**Purpose**: Tracks notification delivery events for monitoring and analytics.

**Partitions**: 1 (low volume, sequential processing)

**Retention**: 7 days (604800000 ms)

**Producers**:
- Notification Service (after processing reminders)

**Consumers**:
- Audit Service (logs notification events)
- Analytics Service (future: notification metrics)

**Event Types**:

#### notification.sent
```json
{
  "event_type": "todo.notification.sent",
  "payload": {
    "reminder_id": "uuid",
    "task_id": "uuid",
    "user_id": "uuid",
    "scheduled_time": "ISO8601",
    "actual_time": "ISO8601",
    "time_difference_seconds": "float",
    "is_on_time": "boolean"
  },
  "timestamp": "ISO8601",
  "correlation_id": "uuid"
}
```

**Usage Patterns**:
- Low volume (matches reminder.fired events)
- Used for SLA monitoring (1-second accuracy)
- Enables notification delivery analytics

---

### 4. todo.audit.events

**Purpose**: Comprehensive audit trail of all system events for compliance and debugging.

**Partitions**: 1 (sequential order critical for audit trail)

**Retention**: 30 days (2592000000 ms) - longer retention for compliance

**Producers**:
- Audit Service (republishes all events from other topics)

**Consumers**:
- Audit Service (stores in PostgreSQL)
- Compliance Tools (future: external audit systems)

**Event Schema**:
```json
{
  "event_type": "todo.audit.event",
  "payload": {
    "original_event": {
      "event_type": "string",
      "payload": "object",
      "timestamp": "ISO8601",
      "correlation_id": "uuid"
    },
    "audit_metadata": {
      "service_name": "string",
      "user_id": "uuid",
      "audit_timestamp": "ISO8601"
    }
  },
  "timestamp": "ISO8601",
  "correlation_id": "uuid"
}
```

**Usage Patterns**:
- High volume (mirrors all other topics)
- Write-heavy, read-light (queries for debugging/compliance)
- Requires chronological ordering validation

---

### 5. todo.task.events.dlq

**Purpose**: Dead letter queue for failed task events that couldn't be processed after retries.

**Partitions**: 1 (error handling, sequential processing)

**Retention**: 7 days (604800000 ms)

**Producers**:
- All event consumers (when max retries exceeded)

**Consumers**:
- DLQ Handler (manual reprocessing)
- Monitoring/Alerting (error rate tracking)

**Event Schema**:
```json
{
  "event_type": "todo.dlq.event",
  "payload": {
    "original_event": "object",
    "error_message": "string",
    "retry_count": "integer",
    "original_topic": "string",
    "dlq_timestamp": "ISO8601"
  },
  "timestamp": "ISO8601",
  "correlation_id": "uuid"
}
```

**Usage Patterns**:
- Very low volume (should be near-zero in healthy system)
- Requires alerting when events arrive
- Manual intervention needed for reprocessing

---

## Topic Configuration

### Replication Factor

All topics use `replication.factor: 1` for local development. In production:
- Critical topics (task.events, audit.events): 3 replicas
- Non-critical topics (reminders, notifications): 2 replicas
- DLQ: 2 replicas

### Cleanup Policy

All topics use `cleanup.policy: delete` (time-based retention).

### Compression

Recommended: `compression.type: snappy` for production (reduces storage and network usage).

### Partitioning Strategy

**task.events**: Partition by `user_id` hash for:
- Load distribution across partitions
- Ordered processing per user
- Parallel processing of different users

**Other topics**: Single partition for:
- Simpler ordering guarantees
- Lower volume doesn't require parallelism

---

## Monitoring

### Key Metrics

1. **Message Rate**
   - Messages/second per topic
   - Alert if task.events > 1000 msg/s (capacity limit)

2. **Consumer Lag**
   - Time between message production and consumption
   - Alert if lag > 5 seconds for task.events
   - Alert if lag > 1 second for reminders

3. **DLQ Volume**
   - Messages in DLQ topic
   - Alert if any messages arrive (indicates processing failures)

4. **Retention Compliance**
   - Verify messages deleted after retention period
   - Audit topic must retain 30 days for compliance

### Monitoring Commands

```bash
# View topic lag
kubectl exec -it ai-todo-kafka-kafka-0 -- \
  bin/kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 \
  --describe --group <consumer-group>

# View topic message count
kubectl exec -it ai-todo-kafka-kafka-0 -- \
  bin/kafka-run-class.sh kafka.tools.GetOffsetShell \
  --broker-list localhost:9092 \
  --topic todo.task.events

# View topic configuration
kubectl exec -it ai-todo-kafka-kafka-0 -- \
  bin/kafka-configs.sh \
  --bootstrap-server localhost:9092 \
  --describe --entity-type topics \
  --entity-name todo.task.events
```

---

## Best Practices

1. **Event Ordering**: Use correlation_id to track related events across topics
2. **Idempotency**: All consumers must handle duplicate events (use correlation_id)
3. **Schema Evolution**: Add new fields only, never remove or rename existing fields
4. **Error Handling**: Implement exponential backoff (3 retries) before sending to DLQ
5. **Monitoring**: Alert on consumer lag > 5 seconds or DLQ messages > 0
6. **Testing**: Use separate topics for development/staging/production environments

---

## Troubleshooting

### High Consumer Lag

1. Check consumer pod resources: `kubectl top pods`
2. Scale consumers horizontally: `kubectl scale deployment <name> --replicas=3`
3. Verify Kafka broker health: `kubectl get kafka`

### Messages in DLQ

1. Query DLQ messages: `kubectl exec -it ai-todo-kafka-kafka-0 -- bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic todo.task.events.dlq --from-beginning`
2. Identify error patterns in error_message field
3. Fix root cause in consumer code
4. Reprocess DLQ messages using DLQ handler

### Topic Not Found

1. Verify topic exists: `kubectl get kafkatopics`
2. Check Strimzi operator logs: `kubectl logs -l name=strimzi-cluster-operator -n kafka`
3. Recreate topic: `kubectl apply -f charts/kafka-cluster/templates/topics.yaml`
