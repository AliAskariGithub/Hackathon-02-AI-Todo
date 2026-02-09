# Research Findings: ChatKit UI & Persistence Implementation

**Feature**: 007-todo-chatkit-persistence
**Date**: 2026-02-06
**Researcher**: Claude

## Research Findings Summary

### Decision: Next.js Proxy Configuration
**Rationale**: After researching Next.js 16.1.2 proxy patterns and streaming response handling, the configuration requires specific headers for streaming.

**Findings**:
- Next.js 16.1.2 uses standard API routes with streaming response patterns
- Need to set appropriate headers: `Transfer-Encoding: chunked`, `Content-Type: text/plain`
- Streaming responses should be handled with `res.writeHead()` and `res.write()` in the API route

### Decision: OpenAI ChatKit Session Integration
**Rationale**: ChatKit doesn't use the traditional OpenAI Assistants API, but rather a real-time conversation API that needs to be bridged with our MCP tools.

**Findings**:
- OpenAI ChatKit is not the same as OpenAI's Assistants API - it's a real-time chat UI component
- The proper approach is to create a FastAPI endpoint that acts as a bridge between ChatKit and our MCP tools
- Streaming responses should be handled with Server-Sent Events (SSE) or direct streaming response

### Decision: MCP Tool Integration with ChatKit UI
**Rationale**: Need to integrate the existing MCP tools with the ChatKit UI for proper visualization of tool execution.

**Findings**:
- The UI should display special components when tools are executed
- Tool execution results should be formatted as special message types
- Need to distinguish between normal assistant responses and tool execution results

### Decision: Better Auth JWT Integration
**Rationale**: Securing ChatKit sessions with our existing Better Auth system requires proper token validation.

**Findings**:
- Better Auth JWT tokens can be verified using the same middleware pattern as existing endpoints
- Need to ensure the user_id from JWT matches the conversation ownership
- All conversation access must be validated against the authenticated user context

## Technical Solutions Identified

### Solution 1: Proxy Configuration Pattern
```typescript
// For Next.js API routes with streaming
export const config = {
  runtime: 'edge',
};

// Or for Node.js API routes
export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  // Set appropriate headers for streaming
  res.writeHead(200, {
    'Content-Type': 'text/plain',
    'Transfer-Encoding': 'chunked',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': '*',
  });
}
```

### Solution 2: Streaming Response Pattern
```python
# FastAPI streaming response pattern
from fastapi.responses import StreamingResponse
import json

async def stream_chat_response(user_input: str, user_id: str):
    # Execute agent with streaming
    for token in await run_agent_streaming(user_input, user_id):
        yield f"data: {json.dumps({'content': token})}\n\n"
```

### Solution 3: Conversation Model Pattern
```python
class Conversation(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    title: str = Field(min_length=1, max_length=200)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow,
                                sa_column_kwargs={"onupdate": datetime.utcnow})

    messages: List["Message"] = Relationship(back_populates="conversation", cascade_delete=True)

class Message(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    conversation_id: uuid.UUID = Field(foreign_key="conversation.id")
    role: str = Field(sa_column_kwargs={"name": "role"})
    content: str = Field(min_length=1)
    tool_calls: Optional[List[Dict[str, Any]]] = Field(default=None, nullable=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    conversation: Conversation = Relationship(back_populates="messages")
```

## Architecture Approach Confirmed

### Session Bridge Architecture
1. FastAPI endpoint receives ChatKit requests with authentication
2. Retrieves conversation history from SQLModel/Neon
3. Executes agent with MCP tools and current context
4. Stores new messages to database
5. Streams response back to ChatKit component

### Security Architecture
1. All requests validated with Better Auth JWT middleware
2. User context verified against conversation ownership
3. MCP tools execute within authenticated user context only
4. Cross-user access prevented at both API and database layers

### UI Integration Architecture
1. ChatKit component mounted in Next.js with proper proxy configuration
2. Custom message components for tool execution visualization
3. Real-time indicators for "thinking" and tool execution states
4. Proper styling with #0FFF50 accents and theme compatibility

## Key Integration Points

### Backend Integration
- `ChatKitRouter` in FastAPI to handle ChatKit requests
- `ConversationService` to manage conversation persistence
- `MessageService` to handle individual message storage
- Streaming response middleware for real-time communication

### Frontend Integration
- `/dashboard/chat` route with ChatKit component
- Authentication context passing to ChatKit session
- Custom styling with Shadcn and #0FFF50 theme
- Tool call visualization components

### Agent Integration
- Context window management (last 10-15 messages)
- MCP tool execution within conversation flow
- Response streaming to maintain real-time experience
- Tool result formatting for UI display

## Research Conclusion

All identified unknowns have been resolved through research and technical investigation:
- ✅ Next.js proxy configuration for streaming is well-established
- ✅ OpenAI ChatKit integration pattern identified (bridge approach)
- ✅ MCP tool integration approach defined (special message formatting)
- ✅ Authentication security pattern confirmed (JWT validation with user isolation)