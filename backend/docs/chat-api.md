# Chat API Documentation

## Overview

The Chat API provides endpoints for managing conversations and messages in the AI Task Assistant application. All endpoints require JWT authentication and enforce user-level access control.

## Base URL

```
http://localhost:8001/api/{user_id}
```

## Authentication

All endpoints require a valid JWT token in the Authorization header:

```
Authorization: Bearer <jwt_token>
```

## Endpoints

### Conversations

#### Create Conversation

Create a new conversation for a user.

**Endpoint:** `POST /api/{user_id}/conversations`

**Request Body:**
```json
{
  "title": "New Conversation",
  "user_id": "uuid"
}
```

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "title": "New Conversation",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

---

#### Get All Conversations

Retrieve all conversations for a user, ordered by creation date (newest first).

**Endpoint:** `GET /api/{user_id}/conversations`

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "user_id": "uuid",
    "title": "Task Management",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
]
```

---

#### Get Conversation by ID

Retrieve a specific conversation by ID.

**Endpoint:** `GET /api/{user_id}/conversations/{conversation_id}`

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "title": "Task Management",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**Error Responses:**
- `404 Not Found` - Conversation not found or doesn't belong to user

---

#### Update Conversation

Update a conversation's details (e.g., rename title).

**Endpoint:** `PATCH /api/{user_id}/conversations/{conversation_id}`

**Request Body:**
```json
{
  "title": "Updated Title"
}
```

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "title": "Updated Title",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:01Z"
}
```

**Error Responses:**
- `404 Not Found` - Conversation not found or doesn't belong to user

---

### Messages

#### Get Conversation Messages

Retrieve all messages for a specific conversation.

**Endpoint:** `GET /api/{user_id}/conversations/{conversation_id}/messages`

**Query Parameters:**
- `limit` (optional): Maximum number of messages to return (default: 50)
- `offset` (optional): Number of messages to skip (default: 0)

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "conversation_id": "uuid",
    "role": "user",
    "content": "Add a task to buy milk",
    "created_at": "2024-01-01T00:00:00Z",
    "tool_calls": null
  },
  {
    "id": "uuid",
    "conversation_id": "uuid",
    "role": "assistant",
    "content": "I've added the task 'Buy milk' to your list.",
    "created_at": "2024-01-01T00:00:01Z",
    "tool_calls": null
  }
]
```

---

#### Add Message to Conversation

Add a message to a specific conversation (manual message creation).

**Endpoint:** `POST /api/{user_id}/conversations/{conversation_id}/messages`

**Request Body:**
```json
{
  "conversation_id": "uuid",
  "role": "user",
  "content": "Message content",
  "tool_calls": null
}
```

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "conversation_id": "uuid",
  "role": "user",
  "content": "Message content",
  "created_at": "2024-01-01T00:00:00Z",
  "tool_calls": null
}
```

**Error Responses:**
- `400 Bad Request` - Invalid role (must be 'user' or 'assistant')

---

### Chat

#### Send Message (Non-Streaming)

Send a message and receive an AI response (non-streaming).

**Endpoint:** `POST /api/{user_id}/chat`

**Request Body:**
```json
{
  "content": "Add a task to buy milk",
  "conversation_id": "uuid",  // Optional - creates new conversation if not provided
  "role": "user"
}
```

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "conversation_id": "uuid",
  "role": "assistant",
  "content": "I've added the task 'Buy milk' to your list.",
  "created_at": "2024-01-01T00:00:01Z",
  "tool_calls": null
}
```

**Notes:**
- If `conversation_id` is not provided, a new conversation is created automatically
- The user message is saved to the database before processing
- The AI response is generated using the last 15 messages as context
- Rate limiting: 20 messages/minute, 200 messages/hour per user

---

#### Send Message (Streaming)

Send a message and receive an AI response via Server-Sent Events (SSE).

**Endpoint:** `POST /api/{user_id}/chat/stream`

**Request Body:**
```json
{
  "content": "Add a task to buy milk",
  "conversation_id": "uuid",  // Optional
  "role": "user"
}
```

**Response:** `200 OK` (text/event-stream)

**SSE Event Format:**

Content chunk:
```
data: {"type": "content", "content": "I've added"}
```

Completion:
```
data: {"type": "done"}
```

Error:
```
data: {"type": "error", "message": "Error message"}
```

**Notes:**
- Streams AI response in real-time as it's generated
- Automatically creates conversation if not provided
- User message is saved before streaming begins
- 30-second timeout for AI response generation

---

## Rate Limiting

All chat endpoints enforce rate limiting per user:
- **20 messages per minute**
- **200 messages per hour**

**Rate Limit Response:** `429 Too Many Requests`
```json
{
  "detail": "Rate limit exceeded. Please try again later."
}
```

---

## Error Responses

### Common Error Codes

- `400 Bad Request` - Invalid request body or parameters
- `401 Unauthorized` - Missing or invalid JWT token
- `403 Forbidden` - User doesn't own the requested resource
- `404 Not Found` - Resource not found
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

### Error Response Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## Context Management

The AI agent maintains conversation context using the last 15 messages from the conversation. This ensures:
- Relevant context for task management operations
- Cost control (limited context window)
- Reasonable response times

---

## Security

### User ID Injection

All MCP tool calls automatically inject the authenticated user's ID to prevent cross-user data access. Users can only:
- Access their own conversations
- View their own messages
- Manage their own tasks

### JWT Verification

All endpoints verify:
1. JWT token is valid and not expired
2. User ID in token matches user ID in URL path
3. User has permission to access the requested resource

---

## Frontend Integration

### Next.js Streaming Proxy

The frontend uses a Next.js API route (`/api/chat`) to proxy streaming requests to the backend. This handles:
- JWT token forwarding
- SSE stream pass-through
- Proper CORS headers
- Error handling

**Frontend Endpoint:** `POST /api/chat`

**Request Body:**
```json
{
  "content": "Message content",
  "conversation_id": "uuid",
  "user_id": "uuid"
}
```

---

## Examples

### Create Conversation and Send Message

```bash
# 1. Create conversation
curl -X POST http://localhost:8001/api/{user_id}/conversations \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"title": "Task Management", "user_id": "{user_id}"}'

# 2. Send message
curl -X POST http://localhost:8001/api/{user_id}/chat \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"content": "Add a task to buy milk", "conversation_id": "{conversation_id}", "role": "user"}'
```

### Stream AI Response

```bash
curl -X POST http://localhost:8001/api/{user_id}/chat/stream \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"content": "Show me all my tasks", "conversation_id": "{conversation_id}", "role": "user"}' \
  --no-buffer
```

---

## Testing

### Health Check

The backend provides a health check endpoint:

```bash
curl http://localhost:8001/health
```

### OpenAPI Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8001/docs`
- ReDoc: `http://localhost:8001/redoc`

---

## Deployment

### Environment Variables

Required environment variables:
```
GROQ_API_KEY=your_api_key
GROQ_MODEL=tngtech/deepseek-r1t2-chimera:free
DATABASE_URL=postgresql://...
JWT_SECRET=your_secret_key
```

### Production Considerations

1. **Rate Limiting**: Adjust limits based on usage patterns
2. **Context Window**: Monitor token usage and adjust message limit
3. **Timeouts**: Configure appropriate timeouts for AI responses
4. **Logging**: Enable comprehensive logging for debugging
5. **Monitoring**: Track rate limit violations and error rates
