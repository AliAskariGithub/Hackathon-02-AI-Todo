# Docker Deployment Testing Guide

## Overview

This guide provides step-by-step instructions to test the complete AI Todo application deployed with Docker, including all event-driven features.

## Prerequisites

- All Docker images built (backend, frontend, 3 microservices)
- Docker Compose installed
- At least 4GB RAM allocated to Docker Desktop

## Complete Deployment Test

### Step 1: Start All Services

```bash
# Start all services in detached mode
docker-compose up -d

# Wait for all services to be healthy (takes ~2-3 minutes)
# Watch the startup process
docker-compose logs -f
```

**Expected Output:**
```
Creating network "ai-todo-network"
Creating ai-todo-postgres ... done
Creating ai-todo-zookeeper ... done
Creating ai-todo-kafka ... done
Creating ai-todo-zipkin ... done
Creating ai-todo-kafka-init ... done
Creating ai-todo-backend ... done
Creating ai-todo-audit-service ... done
Creating ai-todo-notification-service ... done
Creating ai-todo-recurring-service ... done
Creating ai-todo-frontend ... done
```

### Step 2: Verify All Services Are Running

```bash
# Check service status
docker-compose ps

# All services should show "Up" or "Up (healthy)"
```

**Expected Services:**
- ✅ postgres (healthy)
- ✅ zookeeper (Up)
- ✅ kafka (healthy)
- ✅ zipkin (healthy)
- ✅ backend (healthy)
- ✅ audit-service (healthy)
- ✅ notification-service (healthy)
- ✅ recurring-service (healthy)
- ✅ frontend (healthy)

### Step 3: Verify Kafka Topics

```bash
# List all Kafka topics
docker-compose exec kafka kafka-topics --bootstrap-server localhost:9092 --list
```

**Expected Topics:**
```
todo.audit.events
todo.notifications
todo.reminders
todo.task.events
todo.task.events.dlq
```

### Step 4: Test Backend API

```bash
# Test health endpoint
curl http://localhost:8000/health

# Expected: {"status":"healthy"}

# Test API documentation
curl http://localhost:8000/docs
# Should return HTML for Swagger UI

# Test OpenAPI schema
curl http://localhost:8000/openapi.json
# Should return JSON schema
```

### Step 5: Test Microservices

```bash
# Test Audit Service
curl http://localhost:8003/health
# Expected: {"status":"healthy","service":"audit-service"}

# Test Notification Service
curl http://localhost:8004/health
# Expected: {"status":"healthy","service":"notification-service"}

# Test Recurring Service
curl http://localhost:8002/health
# Expected: {"status":"healthy","service":"recurring-service"}
```

### Step 6: Test Frontend

```bash
# Test frontend is accessible
curl -I http://localhost:3000

# Expected: HTTP/1.1 200 OK
```

**Browser Test:**
1. Open http://localhost:3000 in your browser
2. You should see the AI Todo homepage
3. Click "Sign Up" to create an account
4. Fill in the form and submit
5. You should be redirected to the dashboard

### Step 7: Test Event-Driven Features

#### 7.1 Real-Time Task Synchronization

**Test Setup:**
1. Open http://localhost:3000 in two different browser tabs (Tab A and Tab B)
2. Log in with the same account in both tabs
3. Navigate to the dashboard in both tabs

**Test Execution:**
1. In Tab A: Create a new task
2. In Tab B: Verify the task appears automatically (within 2 seconds)
3. In Tab A: Mark the task as complete
4. In Tab B: Verify the task status updates automatically
5. In Tab A: Delete the task
6. In Tab B: Verify the task disappears automatically

**Expected Result:**
- ✅ All changes in Tab A appear in Tab B within 2 seconds
- ✅ Connection status indicator shows "Connected"
- ✅ No page refresh required

#### 7.2 SSE Connection Status

**Test Execution:**
1. Open browser DevTools (F12)
2. Go to Network tab
3. Filter by "events"
4. Navigate to dashboard
5. Look for SSE connection to `/api/events`

**Expected Result:**
- ✅ SSE connection established
- ✅ Heartbeat messages every 30 seconds
- ✅ Connection status indicator shows green/connected

#### 7.3 Kafka Event Publishing

**Test Execution:**
```bash
# Monitor Kafka messages in real-time
docker-compose exec kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic todo.task.events \
  --from-beginning

# In another terminal, create a task via API
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"title":"Test Task","description":"Testing Kafka"}'
```

**Expected Result:**
- ✅ Event appears in Kafka consumer output
- ✅ Event contains task data and correlation_id
- ✅ Event type is "task.created"

#### 7.4 Audit Trail

**Test Execution:**
```bash
# Check audit logs
curl http://localhost:8003/audit/logs?limit=10

# Expected: JSON array of audit events
```

**Expected Result:**
- ✅ All task operations are logged
- ✅ Each event has timestamp, user_id, correlation_id
- ✅ Events are in chronological order

### Step 8: Test Distributed Tracing

**Test Execution:**
1. Open http://localhost:9411 in your browser (Zipkin UI)
2. Click "Run Query" to see recent traces
3. Perform some task operations in the frontend
4. Refresh Zipkin and look for new traces

**Expected Result:**
- ✅ Traces appear in Zipkin
- ✅ Traces show request flow through services
- ✅ Correlation IDs link related operations

### Step 9: Test Database Persistence

**Test Execution:**
```bash
# Create some tasks in the frontend
# Then restart all services
docker-compose restart

# Wait for services to come back up
docker-compose ps

# Check if tasks are still there
# Open frontend and verify tasks persist
```

**Expected Result:**
- ✅ All tasks persist after restart
- ✅ User accounts persist
- ✅ No data loss

### Step 10: Test Error Handling

#### 10.1 Kafka Unavailable

**Test Execution:**
```bash
# Stop Kafka
docker-compose stop kafka

# Try to create a task in the frontend
# Task should still be created (graceful degradation)

# Check backend logs
docker-compose logs backend | grep -i "kafka\|queue"

# Restart Kafka
docker-compose start kafka
```

**Expected Result:**
- ✅ Tasks can still be created when Kafka is down
- ✅ Events are queued locally
- ✅ Events are published when Kafka comes back up

#### 10.2 Database Connection Loss

**Test Execution:**
```bash
# Stop PostgreSQL
docker-compose stop postgres

# Try to access dashboard
# Should show error message

# Restart PostgreSQL
docker-compose start postgres

# Refresh dashboard
# Should work again
```

**Expected Result:**
- ✅ Graceful error handling
- ✅ Clear error messages
- ✅ Automatic recovery when database returns

## Performance Tests

### Load Test

```bash
# Install Apache Bench (if not installed)
# apt-get install apache2-utils  # Linux
# brew install httpd  # macOS

# Test backend API
ab -n 1000 -c 10 http://localhost:8000/health

# Expected: >100 requests/second
```

### Memory Usage

```bash
# Check memory usage of all containers
docker stats --no-stream

# Expected total: <4GB RAM
```

### Response Times

```bash
# Test API response time
time curl http://localhost:8000/health

# Expected: <100ms
```

## Monitoring

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f kafka
docker-compose logs -f audit-service

# Last 100 lines
docker-compose logs --tail=100

# Follow with timestamps
docker-compose logs -f -t
```

### Check Resource Usage

```bash
# Real-time stats
docker stats

# Container details
docker-compose ps -a

# Network inspection
docker network inspect ai-todo-network
```

### Database Queries

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U postgres -d ai_todo

# List tables
\dt

# Count tasks
SELECT COUNT(*) FROM tasks;

# View recent tasks
SELECT id, title, created_at FROM tasks ORDER BY created_at DESC LIMIT 10;

# Exit
\q
```

## Troubleshooting

### Services Not Starting

```bash
# Check logs for errors
docker-compose logs | grep -i error

# Restart specific service
docker-compose restart backend

# Rebuild and restart
docker-compose up -d --build backend
```

### Port Conflicts

```bash
# Check what's using a port
# Windows
netstat -ano | findstr :8000

# Linux/Mac
lsof -i :8000

# Change port in docker-compose.yml if needed
```

### Network Issues

```bash
# Recreate network
docker-compose down
docker network prune
docker-compose up -d
```

### Clean Slate

```bash
# Stop and remove everything
docker-compose down -v

# Remove all images
docker images | grep ai-todo | awk '{print $3}' | xargs docker rmi

# Rebuild everything
docker-compose build
docker-compose up -d
```

## Success Criteria

All tests should pass:

- ✅ All 9 services running and healthy
- ✅ All 5 Kafka topics created
- ✅ Backend API responding
- ✅ All microservices responding
- ✅ Frontend accessible
- ✅ Real-time task synchronization working
- ✅ SSE connection established
- ✅ Kafka events publishing
- ✅ Audit trail logging
- ✅ Distributed tracing working
- ✅ Database persistence working
- ✅ Error handling graceful
- ✅ Performance acceptable (<100ms response time)
- ✅ Memory usage reasonable (<4GB total)

## Next Steps

After successful testing:

1. Document any issues found
2. Configure production environment variables
3. Set up monitoring and alerting
4. Configure backup strategy
5. Deploy to production environment

## Support

For issues:
- Check logs: `docker-compose logs`
- Verify health: `docker-compose ps`
- Review documentation in `docs/` directory
- Check DOCKER_QUICK_START.md for common issues
