#!/bin/bash

# Docker Build Script for AI Todo Application
# Builds all Docker images for the complete event-driven architecture

set -e

echo "=========================================="
echo "Building AI Todo Docker Images"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Build Backend
echo -e "${BLUE}Building Backend API...${NC}"
docker build -t ai-todo-backend:latest ./backend
echo -e "${GREEN}✓ Backend built successfully${NC}"
echo ""

# Build Frontend
echo -e "${BLUE}Building Frontend...${NC}"
docker build -t ai-todo-frontend:latest ./frontend
echo -e "${GREEN}✓ Frontend built successfully${NC}"
echo ""

# Build Audit Service
echo -e "${BLUE}Building Audit Microservice...${NC}"
docker build -t ai-todo/audit-service:latest ./services/audit
echo -e "${GREEN}✓ Audit service built successfully${NC}"
echo ""

# Build Notification Service
echo -e "${BLUE}Building Notification Microservice...${NC}"
docker build -t ai-todo/notification-service:latest ./services/notification
echo -e "${GREEN}✓ Notification service built successfully${NC}"
echo ""

# Build Recurring Service
echo -e "${BLUE}Building Recurring Task Microservice...${NC}"
docker build -t ai-todo/recurring-service:latest ./services/recurring
echo -e "${GREEN}✓ Recurring service built successfully${NC}"
echo ""

echo "=========================================="
echo -e "${GREEN}All Docker images built successfully!${NC}"
echo "=========================================="
echo ""
echo "Available images:"
docker images | grep -E "ai-todo|REPOSITORY"
echo ""
echo "To start all services, run:"
echo "  docker-compose up -d"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f"
echo ""
echo "To stop all services:"
echo "  docker-compose down"
