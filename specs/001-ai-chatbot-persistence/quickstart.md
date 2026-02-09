# Quickstart Guide: AI Chatbot & Persistence

**Feature**: AI Chatbot & Persistence | **Branch**: `001-ai-chatbot-persistence` | **Date**: 2026-02-07

## For Developers

### Prerequisites

**Required Software**:
- Python 3.11 or higher
- Node.js 18 or higher
- PostgreSQL database (Neon account recommended)
- Git

**Required Accounts**:
- OpenRouter API account (for AI service)
- Neon account (for PostgreSQL database)

**Required API Keys**:
- OpenRouter API key
- Neon database connection string

---

### Backend Setup

**1. Navigate to backend directory**:
```bash
cd backend
```

**2. Create and activate virtual environment**:
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

**3. Install dependencies**:
```bash
pip install -r requirements.txt
```

**4. Configure environment variables**:

Add the following to your `.env` file in the backend directory:

```env
# OpenRouter Configuration
GROQ_API_KEY=your_GROQ_API_KEY_here
GROQ_MODEL=openai/gpt-oss-120b:free

# Database Configuration (existing)
DATABASE_URL=your_neon_database_url_here

# Authentication (existing)
BETTER_AUTH_SECRET=your_secret_here
JWT_SECRET=your_jwt_secret_here
```

**5. Run database migrations**:
```bash
# Apply migrations to create new tables
alembic upgrade head
```

**6. Start the backend server**:
```bash
python main.py
```

The backend will start on `http://localhost:8001`

**7. Verify backend is running**:
```bash
curl http://localhost:8001/health
```

Expected response: `{"status": "healthy"}`

---

### Frontend Setup

**1. Navigate to frontend directory**:
```bash
cd frontend
```

**2. Install dependencies**:
```bash
npm install
```

**3. Configure environment variables**:

Add the following to your `.env.local` file in the frontend directory:

```env
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8001

# Authentication (existing)
NEXT_PUBLIC_AUTH_URL=http://localhost:8001/api/auth
```

**4. Start the development server**:
```bash
npm run dev
```

The frontend will start on `http://localhost:3000`

**5. Verify frontend is running**:

Open your browser and navigate to `http://localhost:3000`

---

### Testing the Chat Feature

**1. Create an account or log in**:
- Navigate to `http://localhost:3000`
- Sign up with email and password, or log in if you already have an account

**2. Access the chat interface**:
- Click "Chat" in the navigation menu
- You should see an empty chat interface

**3. Test basic task creation**:

Send the following message:
```
Add a task to buy milk
```

Expected behavior:
- AI response streams in real-time
- Task is created in the database
- AI confirms the task was added

**4. Test task listing**:

Send the following message:
```
Show me all my tasks
```

Expected behavior:
- AI calls the list_tasks MCP tool
- AI displays all your tasks with their status

**5. Test task completion**:

Send the following message:
```
Mark the milk task as complete
```

Expected behavior:
- AI calls list_tasks to find the task ID
- AI calls update_task to mark it complete
- AI confirms the task was completed

**6. Test conversation persistence**:
- Refresh the page
- Your conversation history should be preserved
- You can continue the conversation where you left off

**7. Test multiple conversations**:
- Click "New Conversation" button
- Start a new conversation in a separate thread
- Switch between conversations to verify independent context

---

### Common Development Issues

**Issue: Backend fails to start with DNS resolution error**

**Symptom**: Error message about DNS resolution when calling OpenRouter API

**Solution**: This is a known Windows issue with asyncio. The workaround is implemented using synchronous requests with `asyncio.to_thread()`. If the issue persists:
1. Verify you're using the latest code with the workaround
2. Consider using Docker or WSL2 for development
3. Deploy to Linux environment for production

---

**Issue: Streaming responses not appearing**

**Symptom**: Messages appear all at once instead of streaming

**Solution**:
1. Verify Next.js proxy headers are correct (`Content-Type: text/event-stream`)
2. Check browser console for errors
3. Verify backend is sending SSE format correctly
4. Test with curl to isolate frontend vs backend issue:
```bash
curl -N -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"conversation_id": "uuid", "content": "test"}' \
  http://localhost:8001/api/user_id/chat
```

---

**Issue: Rate limiting errors**

**Symptom**: 429 Too Many Requests error

**Solution**:
1. Wait 1 minute before sending more messages
2. Check rate limit configuration in backend
3. For development, temporarily increase limits in `.env`:
```env
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_PER_HOUR=1000
```

---

**Issue: AI hallucinating task IDs**

**Symptom**: AI tries to update/delete tasks that don't exist

**Solution**: This is mitigated by tool docstrings that force the AI to call `list_tasks` first. If it persists:
1. Check that tool docstrings include "IMPORTANT: Always call list_tasks first"
2. Verify the AI is receiving the tool descriptions correctly
3. Consider adding validation layer in backend

---

## For End Users

### Accessing the Chat

**1. Log in to your account**:
- Navigate to the application URL
- Enter your email and password
- Click "Log In"

**2. Navigate to the chat interface**:
- Click "Chat" in the main navigation menu
- You'll see the chat interface with a message input box

**3. Start a conversation**:
- Type your message in the input box at the bottom
- Press Enter or click the Send button
- The AI will respond in real-time

---

### Example Commands

**Creating Tasks**:
- "Add a task to buy groceries"
- "Create a todo to call mom"
- "Remind me to finish the report"

**Viewing Tasks**:
- "Show me all my tasks"
- "What do I need to do?"
- "List my todos"

**Completing Tasks**:
- "Mark the groceries task as complete"
- "I finished calling mom"
- "Complete the report task"

**Updating Tasks**:
- "Change the groceries task to buy milk instead"
- "Update the report task description"

**Deleting Tasks**:
- "Delete the groceries task"
- "Remove the call mom todo"

---

### Tips for Best Results

**Be Specific**:
- Instead of "complete it", say "complete the groceries task"
- The AI understands context but specific references are clearer

**Use Natural Language**:
- You don't need to use exact commands
- "I need to buy milk" works just as well as "Add a task to buy milk"

**Check Your Tasks**:
- Ask "show me my tasks" regularly to see what the AI has created
- This helps you verify the AI understood your request correctly

**Multiple Conversations**:
- Create separate conversations for different topics (work, personal, etc.)
- Each conversation maintains its own context
- Switch between conversations using the sidebar

**Message Limits**:
- Messages are limited to 2,000 characters
- If you need to provide more detail, break it into multiple messages

**Rate Limits**:
- You can send up to 20 messages per minute
- Maximum 200 messages per hour
- If you hit the limit, wait a minute before continuing

---

### Troubleshooting

**Problem: AI doesn't understand my request**

**Solution**: Try rephrasing your request more explicitly:
- Instead of: "do that thing"
- Try: "add a task to buy milk"

---

**Problem: AI can't find my task**

**Solution**: Ask the AI to list all your tasks first:
- "Show me all my tasks"
- Then reference the task by its exact description

---

**Problem: Conversation history is missing**

**Solution**:
- Refresh the page
- If history is still missing, contact support
- Your messages are stored permanently unless you delete them

---

**Problem: Streaming is slow or stops**

**Solution**:
- Check your internet connection
- Refresh the page and try again
- If the problem persists, the AI service may be experiencing high load

---

## Testing Scenarios

### Scenario 1: First-Time User Experience

**Goal**: Verify a new user can successfully create and manage tasks through chat

**Steps**:
1. Sign up for a new account
2. Navigate to chat interface
3. Send message: "Add a task to buy milk"
4. Verify task is created and AI confirms
5. Send message: "Show me my tasks"
6. Verify task appears in the list
7. Send message: "Mark the milk task as complete"
8. Verify task is marked complete

**Expected Result**: All operations succeed, AI provides clear confirmations

---

### Scenario 2: Conversation Persistence

**Goal**: Verify conversation history is preserved across sessions

**Steps**:
1. Log in and start a conversation
2. Send several messages and create tasks
3. Close the browser completely
4. Reopen browser and log in again
5. Navigate to chat interface
6. Verify conversation history is displayed
7. Continue the conversation

**Expected Result**: All previous messages are visible, context is maintained

---

### Scenario 3: Multiple Conversations

**Goal**: Verify users can manage multiple independent conversations

**Steps**:
1. Create first conversation about work tasks
2. Add several work-related tasks
3. Create second conversation about personal tasks
4. Add several personal tasks
5. Switch back to first conversation
6. Verify only work tasks are referenced
7. Switch to second conversation
8. Verify only personal tasks are referenced

**Expected Result**: Each conversation maintains independent context

---

### Scenario 4: Rate Limiting

**Goal**: Verify rate limiting prevents abuse

**Steps**:
1. Send 20 messages rapidly (within 1 minute)
2. Attempt to send 21st message
3. Verify 429 error is returned
4. Wait 1 minute
5. Send another message
6. Verify message is accepted

**Expected Result**: Rate limit is enforced, clear error message displayed

---

### Scenario 5: User Isolation

**Goal**: Verify users cannot access each other's data

**Steps**:
1. Log in as User A
2. Create tasks and conversations
3. Note conversation IDs
4. Log out
5. Log in as User B
6. Attempt to access User A's conversation ID via URL manipulation
7. Verify access is denied

**Expected Result**: User B cannot access User A's data, 403 error returned

---

## Next Steps

After completing the quickstart:
1. Review the [Data Model](./data-model.md) for database schema details
2. Review the [API Contracts](./contracts/) for endpoint specifications
3. Review the [Implementation Plan](./plan.md) for architecture decisions
4. Begin implementation following the [Tasks](./tasks.md) checklist
