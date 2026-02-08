# Quickstart Guide: ChatKit UI & Persistence

**Feature**: 007-todo-chatkit-persistence
**Date**: 2026-02-06

## Overview

This guide provides essential information to get the ChatKit UI & Persistence feature up and running quickly.

## Prerequisites

- Node.js 18+ for frontend
- Python 3.11+ for backend
- OpenAI API key for ChatKit integration
- Better Auth configured for authentication
- SQLModel and Neon database connection established
- Existing MCP & Agent Logic (Spec 6) implementation deployed

## Environment Setup

### Backend Configuration
Add these variables to your `.env` file:
```bash
OPENAI_API_KEY="your-openai-api-key-here"
```

### Frontend Configuration
Ensure proxy settings in `proxy.ts` support streaming:
```typescript
// Next.js 16.1.2 proxy configuration for ChatKit streaming
export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  // Configure for streaming responses
  res.writeHead(200, {
    'Content-Type': 'text/plain',
    'Transfer-Encoding': 'chunked',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive'
  });
}
```

## Architecture Components

### Backend Components
1. **ChatKit Server** (`src/mcp/mcp_server.py`): Bridge between ChatKit and database
2. **Task Tools** (`src/mcp/tools/task_tools.py`): MCP tool implementations with authentication
3. **MCP Middleware** (`src/mcp/middleware/auth_middleware.py`): Authentication context injection
4. **Database Models** (`src/models.py`): Conversation and Message SQLModel entities

### Frontend Components
1. **Chat Route** (`frontend/app/dashboard/chat/page.tsx`): Main ChatKit integration
2. **Authentication Context**: User JWT token handling with Better Auth
3. **UI Styling**: #0FFF50 accent colors and theme compatibility
4. **Tool Visualization**: Special components for MCP tool execution

## Running the System

### 1. Start Backend Services
```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Start the FastAPI server
uvicorn main:app --reload
```

### 2. Start Frontend
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the Next.js application
npm run dev
```

### 3. Access the Chat Interface
Visit `http://localhost:3000/dashboard/chat` after logging in.

## Key Implementation Patterns

### Session Bridge Pattern
```python
# The ChatKit server maps session to Neon DB records
mcp_server = FastMCP("TodoServer")
mcp_server.add_tool("add_task", add_task_wrapper, get_add_task_schema())
```

### Authentication Flow
1. JWT token verified in auth middleware
2. User context injected into all MCP tool calls
3. Database operations scoped to authenticated user only

### Streaming Response Pattern
```python
# All responses streamed for real-time experience
async def stream_chat_response(user_query, user_id):
    for token in await agent_response(user_query, user_id):
        yield {"content": token, "type": "streaming"}
```

### Tool Execution Visualization
1. MCP tools executed within conversation context
2. Tool status (in-progress, success, error) shown in UI
3. Tool results formatted as special message types

## Integration Points

### Backend Integration
- FastAPI endpoint at `/api/{user_id}/chatkit/session`
- SQLModel persistence for conversations and messages
- Existing authentication middleware reuse
- MCP tools integration for task operations

### Frontend Integration
- Next.js route at `/dashboard/chat`
- OpenAI ChatKit React component mounting
- Custom styling with #0FFF50 theme colors
- Better Auth JWT token passing to backend

## Testing the Implementation

### 1. Basic Functionality Test
```bash
# Test conversation creation
curl -X POST http://localhost:8000/api/{user_id}/conversations \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Conversation"}'
```

### 2. Message Persistence Test
```bash
# Test message addition
curl -X POST http://localhost:8000/api/{user_id}/conversations/{conv_id}/messages \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"role": "user", "content": "Hello, AI assistant!"}'
```

### 3. ChatKit Session Test
```bash
# Test ChatKit session creation
curl -X POST http://localhost:8000/api/{user_id}/chatkit/session \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{}'
```

## Security Considerations

- User isolation enforced at database and API levels
- JWT token validation for all operations
- Cross-user access prevention
- Tool execution scoped to authenticated user context
- Proper error handling without data leakage

## Common Issues & Troubleshooting

### Issue: Token Authentication Problems
**Symptom**: "Unauthorized" or "Invalid token" errors
**Solution**: Verify JWT token is valid and matches user context

### Issue: Streaming Not Working
**Symptom**: Delayed responses or buffering
**Solution**: Check proxy configuration and streaming headers

### Issue: Tool Execution Failures
**Symptom**: MCP tools not executing properly
**Solution**: Verify tool schemas and authentication context injection

### Issue: Database Connection Errors
**Symptom**: Cannot save/load conversations or messages
**Solution**: Verify Neon DB connection and SQLModel model relationships

## Success Indicators

- ✅ Users can create conversations and messages that persist
- ✅ Page refresh retains chat history
- ✅ AI agent correctly uses MCP tools in conversation context
- ✅ Tool execution shows proper UI indicators
- ✅ Follow-up questions work with context from previous messages
- ✅ Security checks prevent cross-user access