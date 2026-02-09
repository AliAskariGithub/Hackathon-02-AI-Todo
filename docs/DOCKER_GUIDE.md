# Docker Compose Guide - AI Todo Application

**Last Updated**: 2026-02-08
**Status**: Production Ready ✅

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Environment Configuration](#environment-configuration)
4. [Docker Compose Commands](#docker-compose-commands)
5. [Container Management](#container-management)
6. [Logs and Debugging](#logs-and-debugging)
7. [Health Checks](#health-checks)
8. [Troubleshooting](#troubleshooting)
9. [Advanced Usage](#advanced-usage)
10. [Production Deployment](#production-deployment)

---

## Prerequisites

### Required Software

1. **Docker Desktop** (Windows/Mac) or **Docker Engine** (Linux)
   - Version: 20.10.0 or higher
   - Download: https://www.docker.com/products/docker-desktop

2. **Docker Compose**
   - Version: 2.0.0 or higher
   - Included with Docker Desktop
   - Linux: `sudo apt-get install docker-compose-plugin`

### System Requirements

- **RAM**: Minimum 4GB, Recommended 8GB
- **Disk Space**: Minimum 10GB free
- **CPU**: 2+ cores recommended
- **Network**: Internet connection for initial image builds

### Verify Installation

```bash
# Check Docker version
docker --version
# Expected: Docker version 20.10.0 or higher

# Check Docker Compose version
docker-compose --version
# Expected: Docker Compose version 2.0.0 or higher

# Verify Docker is running
docker ps
# Should return empty list or running containers
```

---

## Quick Start

### 1. Clone and Navigate

```bash
cd C:\Hackathons\hackathon-ai-todo
```

### 2. Configure Environment

```bash
# Copy environment files
cp frontend/.env.example frontend/.env
cp backend/.env.example backend/.env

# Edit with your values (optional for local development)
# Frontend: NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
# Backend: DATABASE_URL, GROQ_API_KEY, etc.
```

### 3. Build and Start

```bash
# Build images and start containers
docker-compose up -d

# Wait for containers to be healthy (30-60 seconds)
docker-compose ps
```

### 4. Access Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### 5. Stop Application

```bash
# Stop containers (preserves data)
docker-compose down

# Stop and remove volumes (deletes data)
docker-compose down -v
```

---

## Environment Configuration

### Frontend Environment (.env)

```env
# API Configuration
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000

# Optional: Analytics, monitoring, etc.
```

### Backend Environment (.env)

```env
# Database Configuration
DATABASE_URL=postgresql://user:password@host:5432/dbname

# API Keys
GROQ_API_KEY=your_groq_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Server Configuration
HOST=0.0.0.0
PORT=8000
ALLOWED_ORIGINS=["http://localhost:3000"]

# Security
SECRET_KEY=your_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Rate Limiting
RATE_LIMIT_PER_DAY=100
```

### Docker-Specific Environment (.env.docker)

These files are used inside Docker containers:

- `frontend/.env.docker` - Frontend container environment
- `backend/.env.docker` - Backend container environment

**Note**: These are automatically loaded by Docker Compose.

---

## Docker Compose Commands

### Basic Commands

#### Build Images

```bash
# Build all images
docker-compose build

# Build specific service
docker-compose build frontend
docker-compose build backend

# Build without cache (clean build)
docker-compose build --no-cache

# Build with progress output
docker-compose build --progress=plain
```

#### Start Containers

```bash
# Start in detached mode (background)
docker-compose up -d

# Start in foreground (see logs)
docker-compose up

# Start specific service
docker-compose up -d frontend
docker-compose up -d backend

# Start and rebuild if needed
docker-compose up -d --build
```

#### Stop Containers

```bash
# Stop all containers
docker-compose stop

# Stop specific service
docker-compose stop frontend
docker-compose stop backend

# Stop and remove containers
docker-compose down

# Stop, remove containers and volumes
docker-compose down -v

# Stop, remove containers, volumes, and images
docker-compose down -v --rmi all
```

#### Restart Containers

```bash
# Restart all containers
docker-compose restart

# Restart specific service
docker-compose restart frontend
docker-compose restart backend
```

---

## Container Management

### View Container Status

```bash
# List running containers
docker-compose ps

# List all containers (including stopped)
docker-compose ps -a

# View container details
docker inspect ai-todo-frontend
docker inspect ai-todo-backend
```

### Execute Commands in Containers

```bash
# Open shell in frontend container
docker-compose exec frontend sh

# Open shell in backend container
docker-compose exec backend bash

# Run specific command
docker-compose exec frontend npm run build
docker-compose exec backend python -c "print('Hello')"

# Run as root user
docker-compose exec -u root frontend sh
```

### View Resource Usage

```bash
# View CPU, memory, network usage
docker stats ai-todo-frontend ai-todo-backend

# View disk usage
docker system df

# View detailed disk usage
docker system df -v
```

### Copy Files

```bash
# Copy from container to host
docker cp ai-todo-frontend:/app/package.json ./package.json

# Copy from host to container
docker cp ./file.txt ai-todo-frontend:/app/file.txt
```

---

## Logs and Debugging

### View Logs

```bash
# View all logs
docker-compose logs

# View logs for specific service
docker-compose logs frontend
docker-compose logs backend

# Follow logs (real-time)
docker-compose logs -f
docker-compose logs -f frontend

# View last N lines
docker-compose logs --tail=50 frontend
docker-compose logs --tail=100 backend

# View logs with timestamps
docker-compose logs -t frontend

# View logs since specific time
docker-compose logs --since 2026-02-08T10:00:00
docker-compose logs --since 1h
```

### Debug Container Issues

```bash
# Check container health
docker-compose ps

# Inspect container
docker inspect ai-todo-frontend

# View container processes
docker-compose top frontend

# Check container events
docker events --filter container=ai-todo-frontend

# View container resource limits
docker inspect ai-todo-frontend | grep -A 10 "Memory"
```

### Common Debug Commands

```bash
# Check if containers can communicate
docker-compose exec frontend ping backend
docker-compose exec backend ping frontend

# Test backend from frontend container
docker-compose exec frontend wget -qO- http://backend:8000/health

# Check environment variables
docker-compose exec frontend env
docker-compose exec backend env | grep DATABASE_URL

# Check network connectivity
docker network ls
docker network inspect hackathon-ai-todo_ai-todo-network
```

---

## Health Checks

### Manual Health Checks

```bash
# Check backend health
curl http://localhost:8000/health
# Expected: {"status":"healthy"}

# Check frontend
curl -I http://localhost:3000
# Expected: HTTP/1.1 200 OK

# Check API documentation
curl http://localhost:8000/docs
# Expected: HTML page

# Check backend root
curl http://localhost:8000/
# Expected: {"message":"Welcome to the Todo Backend API"}
```

### Automated Health Check Script

Create `scripts/health-check.sh`:

```bash
#!/bin/bash

echo "Checking Docker containers..."

# Check if containers are running
if ! docker-compose ps | grep -q "Up"; then
    echo "❌ Containers are not running"
    exit 1
fi

# Check backend health
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend health check failed"
    exit 1
fi

# Check frontend
if curl -f -I http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend is accessible"
else
    echo "❌ Frontend is not accessible"
    exit 1
fi

echo "✅ All health checks passed"
```

Run with:
```bash
chmod +x scripts/health-check.sh
./scripts/health-check.sh
```

---

## Troubleshooting

### Container Won't Start

```bash
# Check logs for errors
docker-compose logs backend
docker-compose logs frontend

# Check if port is already in use
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # Mac/Linux

# Remove and recreate containers
docker-compose down
docker-compose up -d

# Rebuild images
docker-compose build --no-cache
docker-compose up -d
```

### Frontend Can't Connect to Backend

```bash
# Check backend is running
docker-compose ps backend

# Check backend health
curl http://localhost:8000/health

# Check frontend environment
docker-compose exec frontend env | grep NEXT_PUBLIC_API_BASE_URL

# Check network connectivity
docker-compose exec frontend ping backend
docker-compose exec frontend wget -qO- http://backend:8000/health

# Restart frontend
docker-compose restart frontend
```

### Database Connection Issues

```bash
# Check backend logs
docker-compose logs backend | grep -i database

# Check environment variables
docker-compose exec backend env | grep DATABASE_URL

# Test database connection
docker-compose exec backend python -c "from src.utils.db_utils import test_connection; test_connection()"
```

### Build Failures

```bash
# Clean Docker cache
docker builder prune -a

# Remove all images and rebuild
docker-compose down --rmi all
docker-compose build --no-cache
docker-compose up -d

# Check disk space
docker system df
docker system prune -a  # Clean up unused data
```

### Performance Issues

```bash
# Check resource usage
docker stats

# Increase Docker resources (Docker Desktop)
# Settings > Resources > Advanced
# - CPUs: 4+
# - Memory: 8GB+
# - Swap: 2GB+

# Restart Docker Desktop
```

### Network Issues

```bash
# Check network
docker network ls
docker network inspect hackathon-ai-todo_ai-todo-network

# Recreate network
docker-compose down
docker network prune
docker-compose up -d

# Check DNS resolution
docker-compose exec frontend nslookup backend
docker-compose exec backend nslookup frontend
```

---

## Advanced Usage

### Custom Docker Compose File

Create `docker-compose.override.yml` for local customizations:

```yaml
version: '3.8'

services:
  frontend:
    ports:
      - "3001:3000"  # Use different port
    environment:
      - NODE_ENV=development
    volumes:
      - ./frontend:/app  # Mount source for hot reload

  backend:
    ports:
      - "8001:8000"  # Use different port
    environment:
      - DEBUG=true
    volumes:
      - ./backend:/app  # Mount source for hot reload
```

Use with:
```bash
docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d
```

### Development Mode with Hot Reload

```bash
# Mount source code as volumes
docker-compose -f docker-compose.dev.yml up -d

# Or modify docker-compose.yml to add volumes:
# volumes:
#   - ./frontend:/app
#   - /app/node_modules
#   - /app/.next
```

### Production Optimizations

```bash
# Build with production optimizations
docker-compose -f docker-compose.prod.yml build

# Use multi-stage builds (already configured)
# Use non-root users (already configured)
# Use health checks (already configured)
```

### Scaling Services

```bash
# Scale frontend to 3 instances
docker-compose up -d --scale frontend=3

# Note: Requires load balancer configuration
```

### Using Docker Secrets

```bash
# Create secrets
echo "my_secret_key" | docker secret create jwt_secret -

# Use in docker-compose.yml:
# secrets:
#   - jwt_secret
```

---

## Production Deployment

### Pre-Deployment Checklist

- [ ] Environment variables configured
- [ ] Database connection tested
- [ ] API keys added
- [ ] CORS origins configured
- [ ] Health checks passing
- [ ] Logs reviewed
- [ ] Resource limits set
- [ ] Backup strategy in place

### Build for Production

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Tag images
docker tag ai-todo-frontend:latest your-registry/ai-todo-frontend:v1.0.0
docker tag ai-todo-backend:latest your-registry/ai-todo-backend:v1.0.0

# Push to registry
docker push your-registry/ai-todo-frontend:v1.0.0
docker push your-registry/ai-todo-backend:v1.0.0
```

### Deploy to Production

```bash
# Pull images on production server
docker pull your-registry/ai-todo-frontend:v1.0.0
docker pull your-registry/ai-todo-backend:v1.0.0

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Verify deployment
./scripts/health-check.sh
```

### Monitoring

```bash
# View logs
docker-compose logs -f --tail=100

# Monitor resources
docker stats

# Set up log aggregation (ELK, Splunk, etc.)
# Set up monitoring (Prometheus, Grafana, etc.)
```

### Backup and Restore

```bash
# Backup volumes
docker run --rm -v hackathon-ai-todo_data:/data -v $(pwd):/backup alpine tar czf /backup/data-backup.tar.gz /data

# Restore volumes
docker run --rm -v hackathon-ai-todo_data:/data -v $(pwd):/backup alpine tar xzf /backup/data-backup.tar.gz -C /
```

---

## Quick Reference

### Essential Commands

```bash
# Start application
docker-compose up -d

# Stop application
docker-compose down

# View logs
docker-compose logs -f

# Restart service
docker-compose restart frontend

# Rebuild and restart
docker-compose up -d --build

# Check status
docker-compose ps

# Clean up everything
docker-compose down -v --rmi all
```

### Port Mappings

| Service  | Container Port | Host Port | URL                      |
|----------|---------------|-----------|--------------------------|
| Frontend | 3000          | 3000      | http://localhost:3000    |
| Backend  | 8000          | 8000      | http://localhost:8000    |
| API Docs | 8000          | 8000      | http://localhost:8000/docs |

### Container Names

- Frontend: `ai-todo-frontend`
- Backend: `ai-todo-backend`
- Network: `hackathon-ai-todo_ai-todo-network`

### Useful Aliases

Add to your `.bashrc` or `.zshrc`:

```bash
alias dc='docker-compose'
alias dcu='docker-compose up -d'
alias dcd='docker-compose down'
alias dcl='docker-compose logs -f'
alias dcp='docker-compose ps'
alias dcr='docker-compose restart'
alias dcb='docker-compose build'
```

---

## Additional Resources

### Documentation

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Next.js Docker Documentation](https://nextjs.org/docs/deployment#docker-image)
- [FastAPI Docker Documentation](https://fastapi.tiangolo.com/deployment/docker/)

### Project Documentation

- `README.md` - Main project documentation
- `TESTING_GUIDE.md` - Testing procedures
- `DEPLOYMENT_READY.md` - Kubernetes deployment
- `TROUBLESHOOTING.md` - Detailed troubleshooting guide
- `DOCKER_PORT_8000_MIGRATION.md` - Port migration guide

### Support

For issues or questions:
1. Check logs: `docker-compose logs`
2. Review troubleshooting section above
3. Check GitHub issues
4. Contact development team

---

**Version**: 1.0.0
**Last Updated**: 2026-02-08
**Maintained By**: AI Todo Development Team
