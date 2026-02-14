# Docker Images - Quick Reference

## Available Images

All Docker images are built and ready for deployment:

| Image | Tag | Size | Purpose |
|-------|-----|------|---------|
| ai-todo-backend | latest | 422MB | FastAPI backend with Kafka integration |
| ai-todo-frontend | latest | 1.11GB | Next.js frontend with SSE support |
| ai-todo/audit-service | latest | 374MB | Audit microservice for event logging |
| ai-todo/notification-service | latest | 377MB | Notification microservice with Dapr Jobs |
| ai-todo/recurring-service | latest | 377MB | Recurring task microservice |

## Quick Start

### 1. Start All Services

```bash
# Start all services in detached mode
docker-compose up -d

# Expected output:
# Creating network "ai-todo-network"
# Creating ai-todo-postgres
# Creating ai-todo-zookeeper
# Creating ai-todo-kafka
# Creating ai-todo-zipkin
# Creating ai-todo-kafka-init
# Creating ai-todo-backend
# Creating ai-todo-audit-service
# Creating ai-todo-notification-service
# Creating ai-todo-recurring-service
# Creating ai-todo-frontend
```

### 2. Verify Services

```bash
# Check all containers are running
docker-compose ps

# Expected: All services should show "Up" status
# - postgres (healthy)
# - zookeeper (Up)
# - kafka (healthy)
# - zipkin (healthy)
# - backend (healthy)
# - audit-service (healthy)
# - notification-service (healthy)
# - recurring-service (healthy)
# - frontend (healthy)
```

### 3. View Logs

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f kafka
docker-compose logs -f audit-service
```

### 4. Test Services

```bash
# Test backend health
curl http://localhost:8000/health

# Test frontend
curl http://localhost:3000

# Test microservices
curl http://localhost:8003/health  # Audit
curl http://localhost:8004/health  # Notification
curl http://localhost:8002/health  # Recurring

# Check Zipkin UI
open http://localhost:9411
```

## Service Startup Order

The services start in the following order (managed by docker-compose dependencies):

1. **postgres** - Database starts first
2. **zookeeper** - Kafka coordination
3. **kafka** - Message broker (waits for zookeeper)
4. **kafka-init** - Creates topics (waits for kafka healthy)
5. **zipkin** - Tracing service
6. **backend** - API server (waits for postgres + kafka healthy)
7. **audit-service** - Microservice (waits for postgres + kafka + topics)
8. **notification-service** - Microservice (waits for postgres + kafka + topics)
9. **recurring-service** - Microservice (waits for postgres + kafka + topics + backend)
10. **frontend** - Web UI (waits for backend healthy)

## Kafka Topics Created

The kafka-init service automatically creates these topics:

```bash
# List topics
docker-compose exec kafka kafka-topics --bootstrap-server localhost:9092 --list

# Expected topics:
# - todo.task.events (3 partitions, 7-day retention)
# - todo.reminders (1 partition, 1-day retention)
# - todo.notifications (1 partition, 7-day retention)
# - todo.audit.events (1 partition, 30-day retention)
# - todo.task.events.dlq (1 partition, 7-day retention)
```

## Environment Variables

### Backend
- `DATABASE_URL`: PostgreSQL connection string
- `KAFKA_BOOTSTRAP_SERVERS`: Kafka broker address
- `ZIPKIN_ENDPOINT`: Zipkin tracing endpoint
- `JWT_SECRET_KEY`: JWT signing key

### Microservices
- `DATABASE_URL`: PostgreSQL connection string
- `KAFKA_BOOTSTRAP_SERVERS`: Kafka broker address
- `ZIPKIN_ENDPOINT`: Zipkin tracing endpoint
- `SERVICE_NAME`: Service identifier
- `SERVICE_PORT`: Service port number

### Frontend
- `NEXT_PUBLIC_API_URL`: Backend API URL
- `NODE_ENV`: Environment (production)

## Troubleshooting

### Services Not Starting

```bash
# Check logs for errors
docker-compose logs

# Restart all services
docker-compose restart

# Rebuild and restart
docker-compose up -d --build
```

### Database Issues

```bash
# Check PostgreSQL logs
docker-compose logs postgres

# Connect to database
docker-compose exec postgres psql -U postgres -d ai_todo

# Check tables
docker-compose exec postgres psql -U postgres -d ai_todo -c "\dt"
```

### Kafka Issues

```bash
# Check Kafka logs
docker-compose logs kafka

# List topics
docker-compose exec kafka kafka-topics --bootstrap-server localhost:9092 --list

# Describe topic
docker-compose exec kafka kafka-topics --bootstrap-server localhost:9092 --describe --topic todo.task.events
```

### Network Issues

```bash
# Check network
docker network inspect ai-todo-network

# Test connectivity
docker-compose exec backend ping postgres
docker-compose exec backend ping kafka
```

## Stopping Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes data)
docker-compose down -v

# Stop specific service
docker-compose stop backend
```

## Rebuilding Images

```bash
# Rebuild all images
docker-compose build

# Rebuild specific service
docker-compose build backend

# Rebuild and restart
docker-compose up -d --build
```

## Production Deployment

For production deployment:

1. Update environment variables in `.env` files
2. Change default passwords
3. Enable TLS for Kafka
4. Configure persistent volumes
5. Set up monitoring and alerting
6. Configure backup strategy

See `docs/DOCKER_DEPLOYMENT_GUIDE.md` for detailed production setup.

## Next Steps

1. Start services: `docker-compose up -d`
2. Verify health: `docker-compose ps`
3. Check logs: `docker-compose logs -f`
4. Access frontend: http://localhost:3000
5. View traces: http://localhost:9411
6. Test API: http://localhost:8000/docs
