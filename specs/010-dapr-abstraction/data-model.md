# Data Model: Advanced Task Management with Infrastructure Abstraction

**Feature**: 010-dapr-abstraction
**Date**: 2026-02-11
**Purpose**: Define entities, relationships, validation rules, and state transitions for recurring tasks, reminders, and priorities

## Entity Overview

```text
┌─────────────┐       ┌──────────────────┐       ┌─────────────┐
│    User     │──────<│      Task        │>──────│  Reminder   │
│             │  1:N  │                  │  1:N  │             │
└─────────────┘       │ - id             │       └─────────────┘
                      │ - title          │
                      │ - description    │       ┌─────────────┐
                      │ - status         │       │ Recurrence  │
                      │ - priority       │       │  Pattern    │
                      │ - due_date       │       └─────────────┘
                      │ - recurrence     │              │
                      │ - tags[]         │              │
                      │ - created_at     │              │ 1:1
                      │ - updated_at     │              │
                      │ - user_id        │<─────────────┘
                      └──────────────────┘
```

## 1. Task Entity

**Purpose**: Represents a user's todo item with support for recurrence, priorities, due dates, and reminders.

**Fields**:

| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| id | UUID | Yes | UUID v4 format | Unique task identifier |
| user_id | UUID | Yes | UUID v4 format, foreign key | Owner of the task |
| title | String | Yes | 1-200 characters | Task title |
| description | String | No | 0-2000 characters | Detailed task description |
| status | Enum | Yes | "pending", "in_progress", "completed", "deleted" | Current task state |
| priority | Enum | Yes | "High", "Medium", "Low" | Task importance level |
| due_date | DateTime | No | ISO 8601, must be future | When task is due |
| recurrence | Enum | No | "Daily", "Weekly", "Monthly", null | Recurrence pattern |
| recurrence_day_of_week | Integer | No | 0-6 (Monday=0) | For Weekly recurrence |
| recurrence_day_of_month | Integer | No | 1-31 | For Monthly recurrence |
| tags | Array[String] | No | Max 10 tags, 1-50 chars each | User-defined labels |
| created_at | DateTime | Yes | ISO 8601, auto-generated | Task creation timestamp |
| updated_at | DateTime | Yes | ISO 8601, auto-updated | Last modification timestamp |
| completed_at | DateTime | No | ISO 8601 | When task was completed |
| parent_task_id | UUID | No | UUID v4, self-reference | For recurring task chains |
| correlation_id | UUID | No | UUID v4 | For event tracing |

**Validation Rules**:
- `title` must not be empty or whitespace-only
- `due_date` must be in the future when creating a task
- `recurrence_day_of_week` required only when `recurrence="Weekly"`
- `recurrence_day_of_month` required only when `recurrence="Monthly"`
- `tags` must be unique within a task
- `completed_at` can only be set when `status="completed"`
- `parent_task_id` must reference an existing task

**State Transitions**:
```text
pending ──────> in_progress ──────> completed
   │                 │                   │
   │                 │                   │
   └─────────────────┴───────────────────> deleted
```

**Business Rules**:
- When a task with `recurrence` is marked `completed`, a new task instance is generated
- New instance inherits: `title`, `description`, `priority`, `recurrence`, `tags`, `user_id`
- New instance gets: new `id`, new `due_date` (calculated), `status="pending"`, `parent_task_id=original_id`
- Deleted tasks cannot be restored (soft delete not implemented in this spec)

**Dapr State Store Key Pattern**:
- Primary key: `task:{user_id}:{task_id}`
- Index by user: `tasks:user:{user_id}` (list of task IDs)
- Index by status: `tasks:user:{user_id}:status:{status}` (list of task IDs)
- Index by priority: `tasks:user:{user_id}:priority:{priority}` (list of task IDs)

## 2. Recurrence Pattern Entity

**Purpose**: Defines how often a task repeats and calculates next due dates.

**Fields**:

| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| pattern | Enum | Yes | "Daily", "Weekly", "Monthly" | Recurrence frequency |
| day_of_week | Integer | Conditional | 0-6 (Monday=0) | Required for Weekly |
| day_of_month | Integer | Conditional | 1-31 | Required for Monthly |

**Calculation Logic**:

**Daily Recurrence**:
```python
def calculate_next_due_date_daily(current_due_date: datetime) -> datetime:
    return current_due_date + timedelta(days=1)
```

**Weekly Recurrence**:
```python
def calculate_next_due_date_weekly(current_due_date: datetime, day_of_week: int) -> datetime:
    # Find next occurrence of specified day_of_week
    days_ahead = (day_of_week - current_due_date.weekday()) % 7
    if days_ahead == 0:
        days_ahead = 7  # Next week if today is the target day
    return current_due_date + timedelta(days=days_ahead)
```

**Monthly Recurrence**:
```python
def calculate_next_due_date_monthly(current_due_date: datetime, day_of_month: int) -> datetime:
    # Move to next month
    next_month = current_due_date.month + 1
    next_year = current_due_date.year
    if next_month > 12:
        next_month = 1
        next_year += 1

    # Handle months with fewer days (e.g., Feb 31 -> Feb 28/29)
    max_day = calendar.monthrange(next_year, next_month)[1]
    actual_day = min(day_of_month, max_day)

    return datetime(next_year, next_month, actual_day,
                   current_due_date.hour, current_due_date.minute)
```

**Edge Cases**:
- Monthly recurrence on day 31: Use last day of month if target month has fewer days
- Weekly recurrence completed on target day: Schedule for next week
- Timezone handling: All dates stored in UTC, converted to user timezone for display

## 3. Reminder Entity

**Purpose**: Represents a scheduled notification for a task at a specific time.

**Fields**:

| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| id | UUID | Yes | UUID v4 format | Unique reminder identifier |
| task_id | UUID | Yes | UUID v4, foreign key | Associated task |
| user_id | UUID | Yes | UUID v4, foreign key | Reminder recipient |
| scheduled_time | DateTime | Yes | ISO 8601, must be future | When to send reminder |
| status | Enum | Yes | "scheduled", "sent", "cancelled" | Reminder state |
| created_at | DateTime | Yes | ISO 8601, auto-generated | Reminder creation timestamp |
| sent_at | DateTime | No | ISO 8601 | When reminder was sent |
| dapr_job_name | String | No | Max 100 chars | Dapr Jobs API job identifier |

**Validation Rules**:
- `scheduled_time` must be at least 1 minute in the future
- `scheduled_time` must be before task `due_date` (if due date exists)
- Cannot create reminder for completed or deleted tasks
- Maximum 5 reminders per task

**State Transitions**:
```text
scheduled ──────> sent
    │
    │
    └──────────> cancelled
```

**Business Rules**:
- When task is completed before `scheduled_time`, reminder is automatically cancelled
- When task is deleted, all associated reminders are cancelled
- Sent reminders are retained for audit purposes (not deleted)
- Dapr Jobs API callback updates reminder status to "sent"

**Dapr State Store Key Pattern**:
- Primary key: `reminder:{user_id}:{reminder_id}`
- Index by task: `reminders:task:{task_id}` (list of reminder IDs)
- Index by user: `reminders:user:{user_id}` (list of reminder IDs)

## 4. Priority Level Entity

**Purpose**: Categorizes task importance for filtering and sorting.

**Values**:
- **High**: Urgent, critical tasks requiring immediate attention
- **Medium**: Important tasks with moderate urgency
- **Low**: Nice-to-have tasks with low urgency

**Visual Indicators** (Frontend):
- High: Red badge, exclamation icon
- Medium: Yellow badge, dash icon
- Low: Green badge, circle icon

**Sorting Order**:
1. High (priority=1)
2. Medium (priority=2)
3. Low (priority=3)

**Default Value**: Medium (when not specified)

## 5. Tag Entity

**Purpose**: User-defined labels for categorizing and filtering tasks.

**Fields**:

| Field | Type | Required | Validation | Description |
|-------|------|----------|------------|-------------|
| name | String | Yes | 1-50 characters, alphanumeric + spaces | Tag label |
| color | String | No | Hex color code (#RRGGBB) | Visual color |

**Validation Rules**:
- Tag names are case-insensitive (stored lowercase)
- No duplicate tags on a single task
- Maximum 10 tags per task
- Tags are not shared across users (user-scoped)

**Dapr State Store Key Pattern**:
- User tags: `tags:user:{user_id}` (list of unique tag names)

## 6. Event Schema

**Purpose**: Standardized event format for Dapr Pub/Sub.

**Base Event Structure**:
```json
{
  "event_type": "todo.task.created",
  "payload": {
    "task_id": "uuid",
    "title": "string",
    "user_id": "uuid",
    "priority": "High|Medium|Low",
    "due_date": "ISO8601",
    "recurrence": "Daily|Weekly|Monthly|null"
  },
  "user_id": "uuid",
  "timestamp": "ISO8601",
  "correlation_id": "uuid"
}
```

**Event Types**:

1. **todo.task.created**
   - Payload: Full task object
   - Published: When task is created via API

2. **todo.task.completed**
   - Payload: `{ task_id, user_id, completed_at, recurrence }`
   - Published: When task status changes to "completed"
   - Triggers: Recurring task generation (if recurrence exists)

3. **todo.task.updated**
   - Payload: `{ task_id, user_id, updated_fields, old_values, new_values }`
   - Published: When task properties are modified

4. **todo.reminder.scheduled**
   - Payload: `{ reminder_id, task_id, user_id, scheduled_time }`
   - Published: When reminder is created

## 7. Database Schema (Dapr State Store)

**Note**: While using Dapr State API, the underlying PostgreSQL schema is managed by Dapr:

```sql
-- Dapr automatically creates this table
CREATE TABLE dapr_state (
    key TEXT PRIMARY KEY,
    value JSONB NOT NULL,
    etag TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Example stored values:
-- key: "task:user-123:task-456"
-- value: { "id": "task-456", "title": "Buy groceries", ... }
```

**Indexing Strategy** (via Dapr metadata):
- User-based queries: Store task IDs in separate keys (`tasks:user:{user_id}`)
- Status filtering: Store task IDs in status-specific keys
- Priority filtering: Store task IDs in priority-specific keys

## 8. Data Integrity Rules

**User Isolation**:
- All queries MUST filter by `user_id`
- JWT token validation enforces user identity
- No cross-user data access permitted

**Referential Integrity**:
- Reminders reference valid tasks
- Recurring tasks reference parent tasks
- Orphaned reminders are cleaned up when tasks are deleted

**Consistency Rules**:
- Task completion triggers event publication (eventual consistency)
- Recurring task generation is idempotent (correlation_id check)
- Reminder scheduling is atomic (Dapr Jobs API transaction)

## 9. Performance Considerations

**Indexing**:
- Maintain separate index keys for common queries (user, status, priority)
- Use bulk operations for batch reads/writes
- Implement pagination for large result sets (limit 100 per page)

**Caching**:
- Cache user's active tasks in memory (TTL: 5 minutes)
- Invalidate cache on task mutations
- Use Dapr State Store TTL for temporary data (processed correlation IDs)

**Query Optimization**:
- Fetch task IDs from index keys first, then batch-fetch task details
- Use Dapr bulk state operations for multi-task retrieval
- Implement server-side filtering to reduce data transfer

## 10. Migration Strategy

**Phase 1**: Add new fields to existing Task model
- `recurrence`, `recurrence_day_of_week`, `recurrence_day_of_month`
- `priority` (default: "Medium")
- `parent_task_id`, `correlation_id`

**Phase 2**: Create Reminder entity and state store keys

**Phase 3**: Migrate existing tasks to Dapr State Store
- Read from current PostgreSQL database
- Write to Dapr State Store with proper key patterns
- Validate data integrity
- Switch application to use Dapr State API

**Phase 4**: Remove direct PostgreSQL dependencies
- Delete SQLAlchemy models
- Remove psycopg2 dependency
- Update all queries to use Dapr State API

**Rollback Plan**:
- Keep PostgreSQL database as backup during migration
- Implement dual-write pattern (write to both) during transition
- Validate data consistency before full cutover
