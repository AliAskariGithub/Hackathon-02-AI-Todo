#!/bin/bash

# Docker Health Check Script
# Verifies that all Docker containers are running and healthy

set -e

echo "🔍 Checking Docker containers..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running${NC}"
    echo "Please start Docker Desktop and try again"
    exit 1
fi

echo -e "${GREEN}✅ Docker is running${NC}"

# Check if containers are running
echo ""
echo "📦 Checking container status..."

FRONTEND_STATUS=$(docker-compose ps -q frontend 2>/dev/null)
BACKEND_STATUS=$(docker-compose ps -q backend 2>/dev/null)

if [ -z "$FRONTEND_STATUS" ] || [ -z "$BACKEND_STATUS" ]; then
    echo -e "${RED}❌ Containers are not running${NC}"
    echo "Run: docker-compose up -d"
    exit 1
fi

echo -e "${GREEN}✅ Containers are running${NC}"

# Check container health
echo ""
echo "🏥 Checking container health..."

FRONTEND_HEALTH=$(docker inspect --format='{{.State.Health.Status}}' ai-todo-frontend 2>/dev/null || echo "unknown")
BACKEND_HEALTH=$(docker inspect --format='{{.State.Health.Status}}' ai-todo-backend 2>/dev/null || echo "unknown")

if [ "$FRONTEND_HEALTH" = "healthy" ]; then
    echo -e "${GREEN}✅ Frontend container is healthy${NC}"
else
    echo -e "${YELLOW}⚠️  Frontend container health: $FRONTEND_HEALTH${NC}"
fi

if [ "$BACKEND_HEALTH" = "healthy" ]; then
    echo -e "${GREEN}✅ Backend container is healthy${NC}"
else
    echo -e "${YELLOW}⚠️  Backend container health: $BACKEND_HEALTH${NC}"
fi

# Check backend API
echo ""
echo "🔌 Checking backend API..."

if curl -f -s http://localhost:8000/health > /dev/null 2>&1; then
    HEALTH_RESPONSE=$(curl -s http://localhost:8000/health)
    echo -e "${GREEN}✅ Backend API is responding${NC}"
    echo "   Response: $HEALTH_RESPONSE"
else
    echo -e "${RED}❌ Backend API health check failed${NC}"
    echo "   URL: http://localhost:8000/health"
    exit 1
fi

# Check backend root endpoint
if curl -f -s http://localhost:8000/ > /dev/null 2>&1; then
    ROOT_RESPONSE=$(curl -s http://localhost:8000/)
    echo -e "${GREEN}✅ Backend root endpoint is responding${NC}"
    echo "   Response: $ROOT_RESPONSE"
else
    echo -e "${RED}❌ Backend root endpoint failed${NC}"
    exit 1
fi

# Check frontend
echo ""
echo "🌐 Checking frontend..."

if curl -f -s -I http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Frontend is accessible${NC}"
    echo "   URL: http://localhost:3000"
else
    echo -e "${RED}❌ Frontend is not accessible${NC}"
    echo "   URL: http://localhost:3000"
    exit 1
fi

# Check API documentation
echo ""
echo "📚 Checking API documentation..."

if curl -f -s http://localhost:8000/docs > /dev/null 2>&1; then
    echo -e "${GREEN}✅ API documentation is accessible${NC}"
    echo "   URL: http://localhost:8000/docs"
else
    echo -e "${YELLOW}⚠️  API documentation check failed${NC}"
fi

# Check network connectivity
echo ""
echo "🌐 Checking network connectivity..."

if docker-compose exec -T frontend wget -q --spider http://backend:8000/health 2>/dev/null; then
    echo -e "${GREEN}✅ Frontend can communicate with backend${NC}"
else
    echo -e "${RED}❌ Frontend cannot communicate with backend${NC}"
    exit 1
fi

# Display container logs summary
echo ""
echo "📋 Recent container logs:"
echo ""
echo "Backend (last 5 lines):"
docker-compose logs --tail=5 backend 2>/dev/null | sed 's/^/   /'
echo ""
echo "Frontend (last 5 lines):"
docker-compose logs --tail=5 frontend 2>/dev/null | sed 's/^/   /'

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ All health checks passed!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🚀 Application is ready:"
echo "   Frontend:  http://localhost:3000"
echo "   Backend:   http://localhost:8000"
echo "   API Docs:  http://localhost:8000/docs"
echo ""
echo "📊 View logs:     docker-compose logs -f"
echo "🔄 Restart:       docker-compose restart"
echo "🛑 Stop:          docker-compose down"
echo ""

exit 0
