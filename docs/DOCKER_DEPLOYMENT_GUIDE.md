# Docker Deployment Guide

## Overview

This guide covers deploying the complete AI Todo application using Docker and Docker Compose, including all microservices, Kafka, PostgreSQL, and monitoring.

## Architecture

The Docker setup includes:
- **Backend API** (FastAPI) - Port 8000
- **Frontend** (Next.js) - Port 3000
- **Audit Microservice** - Port 8003
- **Notification Microservice** - Port 8004
- **Recurring Task Microservice** - Port 8002
- **PostgreSQL Database** - Port 5432
- **Kafka Broker** - Ports 9092, 9093
- **Zookeeper** - Port 2181
- **Zipkin Tracing** - Port 9411

## Prerequisites

- Docker Desktop installed (with at least 4GB RAM allocated)
- Docker Compose v3.9 or higher
- Network connectivity for pulling base images

## Quick Start

### 1. Build All Docker Images

```bash
# Build all images at once
docker-compose build

# Or build individually
docker build -t ai-todo-backend:latest ./backend
docker build -t ai-todo-frontend:latest ./frontend
docker build -t ai-todo/audit-service:latest ./services/audit
docker build -t ai-todo/notification-service:latest ./services/notification
docker build -t ai-todo/recurring-service:latest ./services/recurring
```

### 2. Start All Services

```bash
# Start all services in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f backend
```

### 3. Verify Services

```bash
# Check all containers are running
docker-compose ps

# Check health status
docker-compose ps --format "table {{.Name}}\t{{.Status}}"

# Test backend API
curl http://localhost:8000/health

# Test frontend
curl http://localhost:3000
```

## Service URLs

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Backend Docs**: http://localhost:8000/docs
- **Audit Service**: http://localhost:8003
- **Notification Service**: http://localhost:8004
- **Recurring Service**: http://localhost:8002
- **Zipkin UI**: http://localhost:9411

## Environment Configuration

### Backend (.env.docker)
```env
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/ai_todo
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
ZIPKIN_ENDPOINT=http://zipkin:9411/api/v2/spans
JWT_SECRET_KEY=your-secret-key-change-in-production
```

### Frontend (.env.docker)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NODE_ENV=production
```

## Kafka Topics

The following topics are automatically created on startup:

| Topic | Partitions | Retention | Purpose |
|-------|-----------|-----------|---------|
| todo.task.events | 3 | 7 days | Task CRUD events |
| todo.reminders | 1 | 1 day | Reminder notifications |
| todo.notifications | 1 | 7 days | Notification events |
| todo.audit.events | 1 | 30 days | Audit trail |
| todo.task.events.dlq | 1 | 7 days | Dead letter queue |

## Service Dependencies

```
postgres (database)
  ↓
zookeeper
  ↓
kafka (message broker)
  ↓
kafka-init (topic creation)
  ↓
backend, audit-service, notification-service, recurring-service
  ↓
frontend
```

## Health Checks

All services include health checks:

- **PostgreSQL**: `pg_isready` every 10s
- **Kafka**: `kafka-broker-api-versions` every 30s
- **Backend**: HTTP GET `/health` every 30s
- **Microservices**: HTTP GET `/health` every 30s
- **Frontend**: HTTP GET `/` every 30s
- **Zipkin**: HTTP GET `/health` every 30s

## Troubleshooting

### Services Not Starting

```bash
# Check logs for errors
docker-compose logs

# Check specific service
docker-compose logs backend

# Restart specific service
docker-compose restart backend
```

### Database Connection Issues

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check database logs
docker-compose logs postgres

# Connect to database
docker-compose exec postgres psql -U postgres -d ai_todo
```

### Kafka Connection Issues

```bash
# Check Kafka is running
docker-compose ps kafka

# List Kafka topics
docker-compose exec kafka kafka-topics --bootstrap-server localhost:9092 --list

# Check topic details
docker-compose exec kafka kafka-topics --bootstrap-server localhost:9092 --describe --topic todo.task.events
```

### Network Issues

```bash
# Check network
docker network ls | grep ai-todo

# Inspect network
docker network inspect ai-todo-network

# Test connectivity between services
docker-compose exec backend ping postgres
docker-compose exec backend ping kafka
```

### Port Conflicts

If ports are already in use, modify `docker-compose.yml`:

```yaml
services:
  backend:
    ports:
      - "8001:8000"  # Change host port
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

## Scaling Services

```bash
# Scale microservices
docker-compose up -d --scale audit-service=2
docker-compose up -d --scale notification-service=2
docker-compose up -d --scale recurring-service=2
```

## Production Considerations

### 1. Security

- Change default passwords in `docker-compose.yml`
- Use Docker secrets for sensitive data
- Enable TLS for Kafka
- Use environment-specific `.env` files

### 2. Performance

- Increase PostgreSQL shared_buffers
- Tune Kafka broker settings
- Add resource limits to services
- Use persistent volumes for data

### 3. Monitoring

- Enable Prometheus metrics collection
- Set up Grafana dashboards
- Configure alerting rules
- Monitor Zipkin traces

### 4. Backup

```bash
# Backup PostgreSQL database
docker-compose exec postgres pg_dump -U postgres ai_todo > backup.sql

# Restore database
docker-compose exec -T postgres psql -U postgres ai_todo < backup.sql
```

## Development vs Production

### Development
```bash
# Use docker-compose.yml as-is
docker-compose up
```

### Production
```bash
# Use production override
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Useful Commands

```bash
# View resource usage
docker stats

# Clean up unused resources
docker system prune -a

# View all images
docker images | grep ai-todo

# Remove all ai-todo images
docker images | grep ai-todo | awk '{print $3}' | xargs docker rmi

# Export logs
docker-compose logs > logs.txt

# Follow logs with timestamps
docker-compose logs -f -t
```

## Next Steps

1. Build all Docker images
2. Start services with `docker-compose up -d`
3. Verify all services are healthy
4. Access frontend at http://localhost:3000
5. Check Zipkin traces at http://localhost:9411
6. Monitor logs with `docker-compose logs -f`

## Support

For issues or questions:
- Check logs: `docker-compose logs`
- Verify health: `docker-compose ps`
- Review documentation in `docs/` directory
