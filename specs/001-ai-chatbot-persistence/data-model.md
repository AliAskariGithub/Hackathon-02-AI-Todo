# Data Model: AI Chatbot & Persistence

**Feature**: AI Chatbot & Persistence | **Branch**: `001-ai-chatbot-persistence` | **Date**: 2026-02-07

## Overview

This document defines the database schema for conversation and message persistence. The data model extends the existing User and Task entities with new Conversation and Message entities to support chat functionality.

## New Entities

### Conversation

Represents a thread of messages between a user and the AI assistant.

**Fields**:
- `id`: UUID (primary key)
- `user_id`: UUID (foreign key to users table, indexed)
- `title`: String (max 200 characters, default "New Conversation")
- `created_at`: DateTime (auto-generated)
- `updated_at`: DateTime (auto-updated on message add)

**Relationships**:
- Belongs to one User
- Has many Messages (cascade delete)

**Indexes**:
- `user_id` - for filtering conversations by user
- `updated_at` - for sorting conversation list by most recent activity

**Constraints**:
- `user_id` must exist in users table (foreign key constraint)
- `title` cannot be null or empty

**Business Rules**:
- When a new message is added to a conversation, `updated_at` is automatically updated
- Deleting a conversation cascades to delete all associated messages
- Users can only access their own conversations (enforced at API level)

---

### Message

Represents a single message within a conversation.

**Fields**:
- `id`: UUID (primary key)
- `conversation_id`: UUID (foreign key to conversations table, indexed)
- `role`: Enum('user', 'assistant')
- `content`: Text (max 2,000 characters for user messages, unlimited for assistant)
- `created_at`: DateTime (auto-generated)
- `tool_calls`: JSONB (nullable, stores MCP tool invocations)

**Relationships**:
- Belongs to one Conversation

**Indexes**:
- `conversation_id` - for filtering messages by conversation
- `created_at` - for chronological ordering within a conversation

**Constraints**:
- `conversation_id` must exist in conversations table (foreign key constraint)
- `role` must be either 'user' or 'assistant'
- `content` cannot be null or empty

**Business Rules**:
- User messages are limited to 2,000 characters (enforced at API level)
- Assistant messages can be unlimited length
- `tool_calls` stores JSON array of MCP tool invocations for debugging and audit
- Messages are immutable once created (no updates, only reads and deletes via conversation cascade)

---

## Existing Entities (Reference)

### User

**Fields**:
- `id`: UUID (primary key)
- `user_name`: String
- `email`: String (unique)
- `password`: String (hashed)
- `created_at`: DateTime
- `updated_at`: DateTime

**Relationships**:
- Has many Conversations
- Has many Tasks

**Note**: No changes to User entity for this feature.

---

### Task

**Fields**:
- `id`: UUID (primary key)
- `user_id`: UUID (foreign key to users table)
- `description`: String (max 500 characters)
- `is_completed`: Boolean (default false)
- `created_at`: DateTime
- `updated_at`: DateTime

**Relationships**:
- Belongs to one User

**Note**: No changes to Task entity for this feature. Tasks are accessed via MCP tools during chat interactions.

---

## Entity Relationship Diagram

```
┌──────────────┐
│     User     │
│              │
│ - id         │
│ - user_name  │
│ - email      │
│ - password   │
└──────┬───────┘
       │
       │ 1:N
       │
       ├─────────────────────────┐
       │                         │
       ▼                         ▼
┌──────────────┐         ┌──────────────┐
│ Conversation │         │     Task     │
│              │         │              │
│ - id         │         │ - id         │
│ - user_id    │         │ - user_id    │
│ - title      │         │ - description│
│ - created_at │         │ - completed  │
│ - updated_at │         └──────────────┘
└──────┬───────┘
       │
       │ 1:N
       │
       ▼
┌──────────────┐
│   Message    │
│              │
│ - id         │
│ - conv_id    │
│ - role       │
│ - content    │
│ - tool_calls │
│ - created_at │
└──────────────┘
```

## SQLModel Implementation Notes

**File Locations**:
- `backend/src/models/conversation.py` - Conversation model
- `backend/src/models/message.py` - Message model

**Key Considerations**:
1. Use SQLModel's `Field` with `foreign_key` parameter for relationships
2. Use `relationship()` for ORM-level relationships (optional, for convenience)
3. Use `sa_column` with `Index` for composite indexes if needed
4. Use Enum type for `role` field to ensure type safety
5. Use JSONB column type for `tool_calls` (PostgreSQL-specific)

**Migration Strategy**:
- Create new tables without modifying existing User and Task tables
- Use Alembic for database migrations
- Test migrations on development database before production

## Data Access Patterns

**Common Queries**:
1. Get all conversations for a user (sorted by updated_at desc)
2. Get last N messages for a conversation (sorted by created_at asc)
3. Create new conversation and first message atomically
4. Update conversation updated_at when new message added

**Performance Considerations**:
- Index on `(user_id, updated_at)` for conversation list queries
- Index on `(conversation_id, created_at)` for message history queries
- Limit message queries to last 50 by default (pagination)
- Consider partitioning messages table if volume exceeds 10M rows

## Security Considerations

**Data Isolation**:
- All queries MUST filter by authenticated user_id
- Never expose conversation_id or message_id without user_id validation
- Prevent cross-user data access through API-level checks

**Data Retention**:
- Messages retained indefinitely (per FR-006)
- User-initiated deletion only
- Consider GDPR compliance for user data export/deletion

## Testing Requirements

**Unit Tests**:
- Model validation (field constraints, relationships)
- Cascade delete behavior
- Enum validation for role field

**Integration Tests**:
- Create conversation with messages
- Query messages with pagination
- Update conversation timestamp on message add
- User isolation (User A cannot access User B's conversations)

**Performance Tests**:
- Query performance with 1000+ conversations per user
- Message history load time with 100+ messages
- Concurrent conversation creation
