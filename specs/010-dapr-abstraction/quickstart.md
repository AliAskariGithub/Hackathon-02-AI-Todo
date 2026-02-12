# Quickstart Guide: Advanced Task Management with Dapr Abstraction

**Feature**: 010-dapr-abstraction
**Date**: 2026-02-11
**Purpose**: Local development setup for Dapr-based event-driven architecture

## Prerequisites

- Docker Desktop v4.53+ (running)
- Kubernetes (Minikube) with Dapr initialized
- Python 3.13+
- Node.js 18+ and npm
- Dapr CLI v1.14+
- kubectl CLI
- Helm v3+

## 1. Dapr Initialization

### Install Dapr CLI (if not already installed)

```bash
# macOS/Linux
curl -fsSL https://raw.githubusercontent.com/dapr/cli/master/install/install.sh | /bin/bash

# Windows (PowerShell)
powershell -Command "iwr -useb https://raw.githubusercontent.com/dapr/cli/master/install/install.ps1 | iex"
```

### Initialize Dapr in Kubernetes (Minikube)

```bash
# Start Minikube
minikube start --cpus=4 --memory=8192

# Initialize Dapr in Kubernetes mode
dapr init -k

# Verify Dapr installation
dapr status -k

# Expected output:
# NAME                   NAMESPACE    HEALTHY  STATUS   REPLICAS  VERSION  AGE  CREATED
# dapr-sidecar-injector  dapr-system  True     Running  1         1.14.0   1m   2026-02-11 10:00.00
# dapr-sentry            dapr-system  True     Running  1         1.14.0   1m   2026-02-11 10:00.00
# dapr-operator          dapr-system  True     Running  1         1.14.0   1m   2026-02-11 10:00.00
# dapr-placement         dapr-system  True     Running  1         1.14.0   1m   2026-02-11 10:00.00
```

## 2. Backend Setup (FastAPI + Dapr)

### Install Python Dependencies

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Expected packages:
# - fastapi
# - uvicorn[standard]
# - dapr
# - dapr-ext-fastapi
# - sqlmodel
# - pydantic
# - python-jose[cryptography]
# - passlib[bcrypt]
```

### Create Dapr Component Files

```bash
# Create components directory
mkdir -p backend/components

# Create PostgreSQL State Store component
cat > backend/components/statestore-postgresql.yaml <<EOF
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
  namespace: default
spec:
  type: state.postgresql
  version: v1
  metadata:
  - name: connectionString
    secretKeyRef:
      name: dapr-secrets
      key: DATABASE_URL
  - name: tableName
    value: "dapr_state"
  - name: keyPrefix
    value: "todo"
EOF

# Create Kafka Pub/Sub component (mock for local dev)
cat > backend/components/pubsub-kafka.yaml <<EOF
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub
  namespace: default
spec:
  type: pubsub.in-memory  # Use in-memory for local dev without Kafka
  version: v1
  metadata: []
EOF

# Create Kubernetes Secrets component
cat > backend/components/secretstore-kubernetes.yaml <<EOF
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: secretstore
  namespace: default
spec:
  type: secretstores.kubernetes
  version: v1
  metadata:
  - name: vaultName
    value: "default"
EOF
```

### Create Kubernetes Secret

```bash
# Create secret with database URL and other credentials
kubectl create secret generic dapr-secrets \
  --from-literal=DATABASE_URL="postgresql://user:password@neon-host:5432/dbname" \
  --from-literal=BETTER_AUTH_SECRET="your-secret-key" \
  --from-literal=JWT_SECRET="your-jwt-secret" \
  --from-literal=KAFKA_BOOTSTRAP_SERVERS="kafka:9092"
```

### Run Backend with Dapr Sidecar

```bash
# Option 1: Run with Dapr CLI (local development)
dapr run \
  --app-id backend \
  --app-port 8000 \
  --dapr-http-port 3500 \
  --dapr-grpc-port 50001 \
  --components-path ./components \
  -- uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# Option 2: Deploy to Kubernetes with Dapr sidecar injection
kubectl apply -f charts/ai-todo/templates/backend-deployment.yaml
```

### Verify Backend + Dapr Integration

```bash
# Check Dapr sidecar is running
curl http://localhost:3500/v1.0/metadata

# Test State Store
curl -X POST http://localhost:3500/v1.0/state/statestore \
  -H "Content-Type: application/json" \
  -d '[{"key":"test-key","value":"test-value"}]'

# Retrieve from State Store
curl http://localhost:3500/v1.0/state/statestore/test-key

# Test Pub/Sub
curl -X POST http://localhost:3500/v1.0/publish/pubsub/test-topic \
  -H "Content-Type: application/json" \
  -d '{"event_type":"test","payload":{}}'
```

## 3. Frontend Setup (Next.js 16 + Dapr Service Invocation)

### Install Node Dependencies

```bash
cd frontend

# Install dependencies
npm install

# Expected packages:
# - next@16.1.2
# - react@18
# - typescript
# - @types/node
# - @types/react
```

### Configure Dapr Service Invocation

```bash
# Create .env.local file
cat > .env.local <<EOF
NEXT_PUBLIC_DAPR_SIDECAR_URL=http://localhost:3500
NEXT_PUBLIC_BACKEND_APP_ID=backend
EOF
```

### Run Frontend

```bash
# Development mode
npm run dev

# Frontend will be available at http://localhost:3000
```

### Test Dapr Service Invocation

```bash
# From frontend, test backend invocation via Dapr
curl http://localhost:3500/v1.0/invoke/backend/method/api/tasks \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 4. End-to-End Testing

### Test Task Creation with Event Publishing

```bash
# Create a task (should publish todo.task.created event)
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test recurring task",
    "priority": "High",
    "recurrence": "Daily",
    "due_date": "2026-02-12T10:00:00Z"
  }'
```

### Test Recurring Task Generation

```bash
# Complete the task (should trigger recurring instance generation)
curl -X POST http://localhost:8000/api/tasks/{task_id}/complete \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Verify next instance was created
curl http://localhost:8000/api/tasks \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Test Reminder Scheduling

```bash
# Schedule a reminder (should create Dapr Job)
curl -X POST http://localhost:8000/api/reminders \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "task-uuid",
    "scheduled_time": "2026-02-11T15:00:00Z"
  }'

# Check Dapr Jobs
curl http://localhost:3500/v1.0-alpha1/jobs
```

### Test Search and Filtering

```bash
# Search tasks by keyword
curl "http://localhost:8000/api/search/tasks?q=groceries" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Filter by priority
curl "http://localhost:8000/api/search/tasks?priority=High" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Natural language search
curl -X POST http://localhost:8000/api/search/natural-language \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me high priority tasks due tomorrow"}'
```

## 5. Monitoring and Debugging

### View Dapr Logs

```bash
# Backend Dapr sidecar logs
dapr logs --app-id backend

# Kubernetes Dapr sidecar logs
kubectl logs -l app=backend -c daprd
```

### Dapr Dashboard

```bash
# Start Dapr dashboard
dapr dashboard -k

# Access at http://localhost:8080
```

### Distributed Tracing (Zipkin)

```bash
# Port-forward Zipkin service
kubectl port-forward svc/zipkin 9411:9411 -n dapr-system

# Access Zipkin UI at http://localhost:9411
```

### Check Dapr Component Status

```bash
# List all Dapr components
kubectl get components

# Describe specific component
kubectl describe component statestore
```

## 6. Common Issues and Solutions

### Issue: Dapr sidecar not injecting

**Solution**:
```bash
# Verify Dapr sidecar injector is running
kubectl get pods -n dapr-system

# Check deployment annotations
kubectl get deployment backend -o yaml | grep dapr.io/enabled

# Ensure annotation is set to "true"
kubectl patch deployment backend -p '{"spec":{"template":{"metadata":{"annotations":{"dapr.io/enabled":"true"}}}}}'
```

### Issue: State Store connection failed

**Solution**:
```bash
# Verify secret exists
kubectl get secret dapr-secrets

# Check secret contents
kubectl get secret dapr-secrets -o yaml

# Verify component configuration
kubectl describe component statestore
```

### Issue: Events not being published

**Solution**:
```bash
# Check Pub/Sub component status
kubectl describe component pubsub

# Verify Kafka is running (if using Kafka)
kubectl get pods -l app=kafka

# Check backend logs for errors
kubectl logs -l app=backend -c backend
```

### Issue: Reminders not firing

**Solution**:
```bash
# Verify Dapr Jobs API is available
curl http://localhost:3500/v1.0-alpha1/jobs

# Check callback endpoint is accessible
curl http://localhost:8000/api/reminders/callback

# Verify job was created
dapr jobs list --app-id backend
```

## 7. Development Workflow

### Making Changes

1. **Update code** in `backend/src/` or `frontend/src/`
2. **Restart Dapr application** (auto-reload enabled for FastAPI)
3. **Test changes** using curl or frontend UI
4. **Check Dapr logs** for errors
5. **Verify events** in Dapr dashboard

### Running Tests

```bash
# Backend unit tests
cd backend
pytest tests/unit/

# Backend integration tests (requires Dapr)
pytest tests/integration/

# Frontend tests
cd frontend
npm test
```

### Debugging Tips

- Use `dapr logs --app-id backend` to see real-time logs
- Enable verbose logging: `dapr run --log-level debug ...`
- Use Zipkin to trace request flows across services
- Check Dapr dashboard for component health
- Verify correlation IDs in logs for event tracing

## 8. Next Steps

After local development is working:

1. **Deploy to Minikube** using Helm charts
2. **Configure Kafka** (Strimzi) for production-like event streaming
3. **Set up monitoring** with Prometheus and Grafana
4. **Run load tests** to verify performance targets
5. **Document ADRs** for significant architectural decisions

## 9. Useful Commands Reference

```bash
# Dapr
dapr --version                    # Check Dapr version
dapr list                         # List running Dapr apps
dapr stop --app-id backend        # Stop Dapr app
dapr uninstall -k                 # Uninstall Dapr from Kubernetes

# Kubernetes
kubectl get pods                  # List pods
kubectl logs <pod-name> -c daprd  # View Dapr sidecar logs
kubectl port-forward <pod> 8000   # Port forward to pod

# Minikube
minikube status                   # Check Minikube status
minikube dashboard                # Open Kubernetes dashboard
minikube tunnel                   # Expose LoadBalancer services
```

## 10. Resources

- [Dapr Documentation](https://docs.dapr.io/)
- [Dapr Python SDK](https://github.com/dapr/python-sdk)
- [Next.js 16 Documentation](https://nextjs.org/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
