# Testing Guide: AI Chatbot & Persistence

## Overview

This guide provides instructions for testing the AI Chatbot & Persistence feature implementation. All core functionality has been implemented and is ready for validation.

## Testing Tasks

### T078: Test All Quickstart.md Scenarios

**Status**: Ready for manual testing

**Objective**: Verify all scenarios in quickstart.md work as documented

**Test Checklist**:

#### Backend Setup
- [ ] Virtual environment creation works
- [ ] Dependencies install without errors
- [ ] Environment variables are correctly configured
- [ ] Database migrations run successfully
- [ ] Backend server starts on port 8001
- [ ] Health check endpoint returns `{"status": "healthy"}`

#### Frontend Setup
- [ ] Dependencies install without errors
- [ ] Environment variables are correctly configured
- [ ] Development server starts on port 3000
- [ ] Application loads in browser

#### Chat Feature Testing
- [ ] User can log in successfully
- [ ] Chat interface is accessible from navigation
- [ ] Message "Add a task to buy milk" creates task and AI confirms
- [ ] Message "Show me all my tasks" displays task list
- [ ] Message "Mark the milk task as complete" updates task status
- [ ] Conversation history persists after page refresh
- [ ] "New Conversation" button creates separate thread
- [ ] Switching between conversations maintains independent context

#### Common Issues
- [ ] Windows DNS workaround handles OpenRouter API calls
- [ ] Streaming responses appear progressively (not all at once)
- [ ] Rate limiting returns 429 after 20 messages/minute
- [ ] AI calls list_tasks before attempting updates/deletes

**How to Test**:
1. Follow quickstart.md step-by-step
2. Document any deviations from expected behavior
3. Verify all example commands work as described
4. Test all troubleshooting scenarios

---

### T079: Verify All Acceptance Scenarios from spec.md

**Status**: Ready for manual testing

**Objective**: Verify all acceptance criteria from spec.md are met

**Test Checklist**:

#### User Story 1: Natural Language Task Management
- [ ] AS1.1: "Add a task to buy groceries" creates task and confirms
- [ ] AS1.2: "Show me all my tasks" displays all tasks with status
- [ ] AS1.3: "Mark the milk task as complete" updates status and confirms
- [ ] AS1.4: "Delete the grocery task" requests confirmation before deleting
- [ ] AS1.5: Ambiguous commands trigger clarifying questions

#### User Story 2: Persistent Conversation History
- [ ] AS2.1: Conversation history persists after browser close/reopen
- [ ] AS2.2: AI understands references to previous messages ("that task")
- [ ] AS2.3: Multiple conversations maintain independent context

#### User Story 3: Real-Time Streaming Responses
- [ ] AS3.1: AI responses stream progressively (not all at once)
- [ ] AS3.2: Typing indicator shows while AI is generating response
- [ ] AS3.3: Network interruptions display error and allow retry
- [ ] AS3.4: Streaming works consistently across different message types

#### User Story 4: Multi-Conversation Management
- [ ] AS4.1: Users can create multiple conversation threads
- [ ] AS4.2: Conversation list shows all conversations with timestamps
- [ ] AS4.3: Users can rename conversations
- [ ] AS4.4: Switching conversations loads correct history
- [ ] AS4.5: Each conversation maintains independent task context

#### Cross-Cutting Concerns
- [ ] Rate limiting enforces 20 messages/minute, 200/hour
- [ ] User isolation prevents cross-user data access
- [ ] JWT authentication required for all endpoints
- [ ] Error messages are clear and actionable
- [ ] Mobile responsive design works on small screens
- [ ] Loading states provide feedback during operations

**How to Test**:
1. Create test user accounts
2. Execute each acceptance scenario exactly as written
3. Document actual vs expected behavior
4. Take screenshots of any issues
5. Verify edge cases and error conditions

---

### T080: Performance Test with 100 Concurrent Users

**Status**: Requires performance testing infrastructure

**Objective**: Verify system handles concurrent load without degradation

**Prerequisites**:
- Load testing tool (e.g., Locust, k6, JMeter)
- Test environment (staging/production-like)
- Monitoring tools (CPU, memory, database connections)

**Test Scenarios**:

#### Scenario 1: Concurrent Message Sending
```python
# Locust example
from locust import HttpUser, task, between

class ChatUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        # Login and get JWT token
        response = self.client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "password"
        })
        self.token = response.json()["token"]
        self.user_id = response.json()["user_id"]

    @task
    def send_message(self):
        self.client.post(
            f"/api/{self.user_id}/chat",
            headers={"Authorization": f"Bearer {self.token}"},
            json={
                "content": "Show me my tasks",
                "role": "user"
            }
        )
```

**Metrics to Monitor**:
- Response time (p50, p95, p99)
- Error rate (should be < 1%)
- Database connection pool usage
- OpenRouter API latency
- Memory usage
- CPU usage

**Success Criteria**:
- [ ] 100 concurrent users can send messages
- [ ] p95 response time < 2 seconds
- [ ] Error rate < 1%
- [ ] No database connection exhaustion
- [ ] Rate limiting works correctly under load
- [ ] Streaming responses work with concurrent users

**How to Test**:
1. Set up load testing tool (Locust recommended)
2. Create test user accounts (100+)
3. Configure test scenarios
4. Run tests with gradual ramp-up (0 → 100 users over 5 minutes)
5. Monitor system metrics
6. Document bottlenecks and performance issues

---

## Test Environment Setup

### Local Testing
```bash
# Backend
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python main.py

# Frontend
cd frontend
npm run dev
```

### Staging Environment
- Deploy to staging environment
- Use production-like database (Neon)
- Configure OpenRouter API with production keys
- Enable monitoring and logging

---

## Test Data

### Sample Test Users
Create test users with different scenarios:
- User with no tasks
- User with 10 tasks (various statuses)
- User with multiple conversations
- User with long conversation history (50+ messages)

### Sample Test Messages
```
# Task Creation
"Add a task to buy milk"
"Create a todo to call mom"
"Remind me to finish the report"

# Task Viewing
"Show me all my tasks"
"What do I need to do?"
"List my todos"

# Task Completion
"Mark the milk task as complete"
"I finished calling mom"
"Complete the report task"

# Task Updates
"Change the milk task to buy groceries"
"Update the report task description to include charts"

# Task Deletion
"Delete the milk task"
"Remove the call mom todo"

# Ambiguous Commands (should trigger clarification)
"Complete it"
"Delete that"
"Update the task"
```

---

## Bug Reporting Template

When issues are found, document them using this template:

```markdown
## Bug Report

**Title**: [Brief description]

**Severity**: Critical / High / Medium / Low

**Steps to Reproduce**:
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Expected Behavior**:
[What should happen]

**Actual Behavior**:
[What actually happened]

**Screenshots/Logs**:
[Attach relevant screenshots or log excerpts]

**Environment**:
- OS: [Windows/Mac/Linux]
- Browser: [Chrome/Firefox/Safari]
- Backend version: [commit hash]
- Frontend version: [commit hash]

**Related Files**:
- [List relevant files]
```

---

## Test Results Documentation

After completing tests, document results in:
`specs/001-ai-chatbot-persistence/TEST_RESULTS.md`

Include:
- Date of testing
- Test environment details
- Pass/fail status for each scenario
- Performance metrics
- Issues found
- Recommendations for improvements

---

## Next Steps After Testing

1. **Fix Critical Issues**: Address any blocking bugs
2. **Performance Optimization**: Optimize bottlenecks found in load testing
3. **Documentation Updates**: Update quickstart.md if any steps are incorrect
4. **User Acceptance Testing**: Have real users test the feature
5. **Production Deployment**: Deploy to production after all tests pass
