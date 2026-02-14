# Quickstart Guide: Local Event-Driven Backbone

**Feature**: Local Event-Driven Backbone
**Date**: 2026-02-13
**Status**: Ready for Implementation

## Overview

This guide provides step-by-step instructions for setting up the event-driven architecture with Kafka, Dapr, and real-time UI updates on your local Minikube cluster.

**Estimated Setup Time**: 30-45 minutes

---

## Prerequisites

### Required Software

| Tool | Version | Installation |
|------|---------|--------------|
| Docker Desktop | 4.53+ | https://www.docker.com/products/docker-desktop |
| Minikube | 1.32+ | `brew install minikube` (macOS) or https://minikube.sigs.k8s.io/docs/start/ |
| kubectl | 1.28+ | `brew install kubectl` (macOS) or https://kubernetes.io/docs/tasks/tools/ |
| Helm | 3.13+ | `brew install helm` (macOS) or https://helm.sh/docs/intro/install/ |
| Dapr CLI | 1.14+ | `brew install dapr/tap/dapr-cli` (macOS) or https://docs.dapr.io/getting-started/install-dapr-cli/ |

### System Requirements

- **RAM**: Minimum 8GB (4GB allocated to Minikube)
- **CPU**: Minimum 4 cores (2 cores allocated to Minikube)
- **Disk**: Minimum 20GB free space

### Verify Installations

```bash
# Check Docker
docker --version
# Expected: Docker version 24.0.0 or higher

# Check Minikube
minikube version
# Expected: minikube version: v1.32.0 or higher

# Check kubectl
kubectl version --client
# Expected: Client Version: v1.28.0 or higher

# Check Helm
helm version
# Expected: version.BuildInfo{Version:"v3.13.0" or higher}

# Check Dapr CLI
dapr --version
# Expected: CLI version: 1.14.0 or higher
```

---

## Step 1: Start Minikube Cluster

### 1.1 Start Minikube with Resource Limits

```bash
# Start Minikube with 4GB RAM and 2 CPUs
minikube start --memory=4096 --cpus=2 --driver=docker

# Verify cluster is running
minikube status
# Expected output:
# minikube
# type: Control Plane
# host: Running
# kubelet: Running
# apiserver: Running
# kubeconfig: Configured
```

### 1.2 Enable Required Addons

```bash
# Enable metrics server for resource monitoring
minikube addons enable metrics-server

# Enable ingress for external access (optional)
minikube addons enable ingress

# Verify addons
minikube addons list | grep enabled
```

### 1.3 Verify Cluster Access

```bash
# Check cluster info
kubectl cluster-info

# Check nodes
kubectl get nodes
# Expected: 1 node in Ready state
```

---

## Step 2: Install Strimzi Kafka Operator

### 2.1 Add Strimzi Helm Repository

```bash
# Add Strimzi Helm repo
helm repo add strimzi https://strimzi.io/charts/

# Update Helm repos
helm repo update

# Verify Strimzi repo
helm search repo strimzi
```

### 2.2 Install Strimzi Operator

```bash
# Create namespace for Strimzi
kubectl create namespace kafka

# Install Strimzi Operator
helm install strimzi-kafka-operator strimzi/strimzi-kafka-operator \
  --namespace kafka \
  --set watchNamespaces="{default,kafka}" \
  --wait

# Verify Strimzi Operator is running
kubectl get pods -n kafka
# Expected: strimzi-cluster-operator pod in Running state
```

### 2.3 Deploy Kafka Cluster (KRaft Mode)

Create `kafka-cluster.yaml`:

```yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: Kafka
metadata:
  name: ai-todo-kafka
  namespace: default
spec:
  kafka:
    version: 3.6.0
    replicas: 1
    listeners:
      - name: plain
        port: 9092
        type: internal
        tls: false
    config:
      offsets.topic.replication.factor: 1
      transaction.state.log.replication.factor: 1
      transaction.state.log.min.isr: 1
      default.replication.factor: 1
      min.insync.replicas: 1
      log.retention.hours: 168
    storage:
      type: ephemeral
    resources:
      requests:
        memory: 512Mi
        cpu: 250m
      limits:
        memory: 1Gi
        cpu: 500m
    jvmOptions:
      -Xms: 256m
      -Xmx: 512m
  entityOperator:
    topicOperator: {}
    userOperator: {}
```

Apply the configuration:

```bash
# Deploy Kafka cluster
kubectl apply -f kafka-cluster.yaml

# Wait for Kafka cluster to be ready (may take 3-5 minutes)
kubectl wait kafka/ai-todo-kafka --for=condition=Ready --timeout=300s -n default

# Verify Kafka pods are running
kubectl get pods -l strimzi.io/cluster=ai-todo-kafka
# Expected: ai-todo-kafka-kafka-0 and ai-todo-kafka-entity-operator pods in Running state
```

### 2.4 Create Kafka Topics

Create `kafka-topics.yaml`:

```yaml
---
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: todo.task.events
  labels:
    strimzi.io/cluster: ai-todo-kafka
spec:
  partitions: 3
  replicas: 1
  config:
    retention.ms: 604800000  # 7 days
    segment.bytes: 1073741824
    cleanup.policy: delete
---
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: todo.reminders
  labels:
    strimzi.io/cluster: ai-todo-kafka
spec:
  partitions: 1
  replicas: 1
  config:
    retention.ms: 86400000  # 1 day
    cleanup.policy: delete
---
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: todo.notifications
  labels:
    strimzi.io/cluster: ai-todo-kafka
spec:
  partitions: 1
  replicas: 1
  config:
    retention.ms: 604800000  # 7 days
    cleanup.policy: delete
---
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: todo.audit.events
  labels:
    strimzi.io/cluster: ai-todo-kafka
spec:
  partitions: 1
  replicas: 1
  config:
    retention.ms: 2592000000  # 30 days
    cleanup.policy: delete
---
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: todo.task.events.dlq
  labels:
    strimzi.io/cluster: ai-todo-kafka
spec:
  partitions: 1
  replicas: 1
  config:
    retention.ms: 604800000  # 7 days
    cleanup.policy: delete
```

Apply the topics:

```bash
# Create Kafka topics
kubectl apply -f kafka-topics.yaml

# Verify topics are created
kubectl get kafkatopics
# Expected: All 5 topics in Ready state
```

---

## Step 3: Install Dapr

### 3.1 Initialize Dapr on Kubernetes

```bash
# Initialize Dapr in Kubernetes mode
dapr init --kubernetes --wait

# Verify Dapr installation
dapr status -k
# Expected: dapr-operator, dapr-sidecar-injector, dapr-sentry, dapr-placement-server all Running

# Verify Dapr pods
kubectl get pods -n dapr-system
# Expected: All Dapr system pods in Running state
```

### 3.2 Create Dapr Components

Create `dapr-components.yaml`:

```yaml
---
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
  namespace: default
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "ai-todo-kafka-kafka-bootstrap.default.svc.cluster.local:9092"
    - name: consumerGroup
      value: "ai-todo-group"
    - name: authType
      value: "none"
---
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
        name: postgres-secret
        key: connectionString
---
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
---
apiVersion: dapr.io/v1alpha1
kind: Configuration
metadata:
  name: tracing-config
  namespace: default
spec:
  tracing:
    samplingRate: "1"
    otel:
      endpointAddress: "http://zipkin.default.svc.cluster.local:9411/api/v2/spans"
      isSecure: false
      protocol: http
  metric:
    enabled: true
```

Apply Dapr components:

```bash
# Create Dapr components
kubectl apply -f dapr-components.yaml

# Verify Dapr components
kubectl get components
# Expected: kafka-pubsub, statestore, secretstore components
```

### 3.3 Create Kubernetes Secrets

```bash
# Create PostgreSQL connection secret (replace with your Neon connection string)
kubectl create secret generic postgres-secret \
  --from-literal=connectionString="postgresql://user:password@host:5432/database?sslmode=require"

# Verify secret
kubectl get secret postgres-secret
```

---

## Step 4: Deploy Microservices

### 4.1 Build Docker Images

```bash
# Navigate to services directory
cd services

# Build Notification Service
cd notification
docker build -t ai-todo/notification-service:v1.0.0 .
minikube image load ai-todo/notification-service:v1.0.0

# Build Recurring Task Service
cd ../recurring
docker build -t ai-todo/recurring-service:v1.0.0 .
minikube image load ai-todo/recurring-service:v1.0.0

# Build Audit Service
cd ../audit
docker build -t ai-todo/audit-service:v1.0.0 .
minikube image load ai-todo/audit-service:v1.0.0

cd ../..
```

### 4.2 Deploy Microservices

Create `microservices-deployment.yaml`:

```yaml
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: notification-service
  labels:
    app: notification-service
spec:
  replicas: 1
  selector:
    matchLabels:
      app: notification-service
  template:
    metadata:
      labels:
        app: notification-service
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "notification-service"
        dapr.io/app-port: "8001"
        dapr.io/config: "tracing-config"
    spec:
      containers:
      - name: notification-service
        image: ai-todo/notification-service:v1.0.0
        imagePullPolicy: Never
        ports:
        - containerPort: 8001
        env:
        - name: DAPR_HTTP_PORT
          value: "3500"
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
---
apiVersion: v1
kind: Service
metadata:
  name: notification-service
spec:
  selector:
    app: notification-service
  ports:
  - port: 8001
    targetPort: 8001
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: recurring-service
  labels:
    app: recurring-service
spec:
  replicas: 1
  selector:
    matchLabels:
      app: recurring-service
  template:
    metadata:
      labels:
        app: recurring-service
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "recurring-service"
        dapr.io/app-port: "8002"
        dapr.io/config: "tracing-config"
    spec:
      containers:
      - name: recurring-service
        image: ai-todo/recurring-service:v1.0.0
        imagePullPolicy: Never
        ports:
        - containerPort: 8002
        env:
        - name: DAPR_HTTP_PORT
          value: "3500"
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
---
apiVersion: v1
kind: Service
metadata:
  name: recurring-service
spec:
  selector:
    app: recurring-service
  ports:
  - port: 8002
    targetPort: 8002
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: audit-service
  labels:
    app: audit-service
spec:
  replicas: 1
  selector:
    matchLabels:
      app: audit-service
  template:
    metadata:
      labels:
        app: audit-service
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "audit-service"
        dapr.io/app-port: "8003"
        dapr.io/config: "tracing-config"
    spec:
      containers:
      - name: audit-service
        image: ai-todo/audit-service:v1.0.0
        imagePullPolicy: Never
        ports:
        - containerPort: 8003
        env:
        - name: DAPR_HTTP_PORT
          value: "3500"
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
---
apiVersion: v1
kind: Service
metadata:
  name: audit-service
spec:
  selector:
    app: audit-service
  ports:
  - port: 8003
    targetPort: 8003
```

Deploy microservices:

```bash
# Deploy all microservices
kubectl apply -f microservices-deployment.yaml

# Wait for deployments to be ready
kubectl wait --for=condition=available --timeout=300s deployment/notification-service
kubectl wait --for=condition=available --timeout=300s deployment/recurring-service
kubectl wait --for=condition=available --timeout=300s deployment/audit-service

# Verify all pods are running with Dapr sidecars
kubectl get pods
# Expected: Each service pod should show 2/2 containers (app + dapr sidecar)
```

---

## Step 5: Update Backend API for Event Publishing

### 5.1 Install Dapr Python SDK

```bash
# Navigate to backend directory
cd backend

# Install Dapr SDK
pip install dapr dapr-ext-fastapi

# Update requirements.txt
echo "dapr==1.14.0" >> requirements.txt
echo "dapr-ext-fastapi==1.14.0" >> requirements.txt
```

### 5.2 Add Event Publishing to Task Endpoints

Update `backend/app/api/routes/tasks.py` to publish events:

```python
from dapr.clients import DaprClient
import json
import uuid
from datetime import datetime

async def publish_task_event(event_type: str, task_data: dict, user_id: str):
    """Publish task event to Kafka via Dapr"""
    with DaprClient() as client:
        event = {
            "event_type": event_type,
            "payload": task_data,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "correlation_id": str(uuid.uuid4())
        }

        client.publish_event(
            pubsub_name="kafka-pubsub",
            topic_name="todo.task.events",
            data=json.dumps(event),
            data_content_type="application/json"
        )

# Add event publishing to create_task endpoint
@router.post("/", response_model=TaskResponse)
async def create_task(task: TaskCreate, current_user: User = Depends(get_current_user)):
    # ... existing task creation logic ...

    # Publish task.created event
    await publish_task_event("task.created", task_dict, current_user.id)

    return new_task

# Add event publishing to update_task endpoint
@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: str, task: TaskUpdate, current_user: User = Depends(get_current_user)):
    # ... existing task update logic ...

    # Publish task.updated event
    await publish_task_event("task.updated", {"task_id": task_id, "changes": changes}, current_user.id)

    return updated_task

# Add event publishing to complete_task endpoint
@router.post("/{task_id}/complete", response_model=TaskResponse)
async def complete_task(task_id: str, current_user: User = Depends(get_current_user)):
    # ... existing task completion logic ...

    # Publish task.completed event
    await publish_task_event("task.completed", task_dict, current_user.id)

    return completed_task

# Add event publishing to delete_task endpoint
@router.delete("/{task_id}")
async def delete_task(task_id: str, current_user: User = Depends(get_current_user)):
    # ... existing task deletion logic ...

    # Publish task.deleted event
    await publish_task_event("task.deleted", {"task_id": task_id, "title": task.title}, current_user.id)

    return {"message": "Task deleted"}
```

---

## Step 6: Implement Frontend SSE Integration

### 6.1 Create SSE Route Handler

Create `frontend/app/api/events/route.ts`:

```typescript
import { NextRequest } from 'next/server';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function GET(request: NextRequest) {
  const token = request.nextUrl.searchParams.get('token');

  if (!token) {
    return new Response('Unauthorized', { status: 401 });
  }

  // TODO: Verify JWT token

  const stream = new ReadableStream({
    start(controller) {
      controller.enqueue(`data: ${JSON.stringify({ type: 'connected' })}\n\n`);

      // TODO: Subscribe to Kafka events via backend API

      const interval = setInterval(() => {
        controller.enqueue(`data: ${JSON.stringify({ type: 'heartbeat' })}\n\n`);
      }, 30000);

      request.signal.addEventListener('abort', () => {
        clearInterval(interval);
        controller.close();
      });
    }
  });

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
    },
  });
}
```

### 6.2 Create useTaskEvents Hook

Create `frontend/hooks/useTaskEvents.ts`:

```typescript
import { useEffect, useState } from 'react';

export function useTaskEvents(token: string) {
  const [events, setEvents] = useState<any[]>([]);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    const eventSource = new EventSource(
      `/api/events?token=${encodeURIComponent(token)}`
    );

    eventSource.onopen = () => {
      setIsConnected(true);
      console.log('SSE connection established');
    };

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setEvents((prev) => [...prev, data]);
    };

    eventSource.onerror = () => {
      setIsConnected(false);
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  }, [token]);

  return { events, isConnected };
}
```

---

## Step 7: Testing the System

### 7.1 Verify All Components

```bash
# Check all pods are running
kubectl get pods --all-namespaces

# Check Dapr sidecars are injected
kubectl get pods -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[*].name}{"\n"}{end}'
# Expected: Each microservice pod should have 2 containers (app + daprd)

# Check Kafka topics
kubectl get kafkatopics
# Expected: All 5 topics in Ready state

# Check Dapr components
kubectl get components
# Expected: kafka-pubsub, statestore, secretstore
```

### 7.2 Test Event Flow (E2E)

```bash
# Port forward backend API
kubectl port-forward svc/backend-api 8000:8000 &

# Port forward frontend
kubectl port-forward svc/frontend 3000:3000 &

# Open browser to http://localhost:3000
# Login and create a task
# Verify task appears in UI

# Check Kafka messages
kubectl exec -it ai-todo-kafka-kafka-0 -- bin/kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic todo.task.events \
  --from-beginning

# Expected: See task.created event in JSON format
```

### 7.3 Test Recurring Task Generation

```bash
# Create a recurring task (daily) via UI
# Mark the task as complete
# Wait 5 seconds

# Check recurring service logs
kubectl logs -f deployment/recurring-service -c recurring-service

# Expected: See log showing new task instance created

# Verify new task appears in UI automatically
```

### 7.4 Test Real-Time Synchronization

```bash
# Open two browser tabs to http://localhost:3000
# Login in both tabs
# Create/update/complete a task in tab 1
# Verify changes appear in tab 2 within 2 seconds
```

---

## Step 8: Monitoring and Troubleshooting

### 8.1 View Logs

```bash
# View Kafka logs
kubectl logs -f ai-todo-kafka-kafka-0

# View Notification Service logs
kubectl logs -f deployment/notification-service -c notification-service

# View Recurring Service logs
kubectl logs -f deployment/recurring-service -c recurring-service

# View Audit Service logs
kubectl logs -f deployment/audit-service -c audit-service

# View Dapr sidecar logs
kubectl logs -f deployment/notification-service -c daprd
```

### 8.2 Check Resource Usage

```bash
# Check cluster resource usage
kubectl top nodes

# Check pod resource usage
kubectl top pods

# Expected: Total usage under 4GB RAM and 2 CPU
```

### 8.3 Common Issues

**Issue**: Kafka pods stuck in Pending state
- **Solution**: Check Minikube has sufficient resources: `minikube status`

**Issue**: Dapr sidecars not injected
- **Solution**: Verify Dapr annotations on deployments: `kubectl describe pod <pod-name>`

**Issue**: Events not flowing to microservices
- **Solution**: Check Dapr Pub/Sub component: `kubectl describe component kafka-pubsub`

**Issue**: SSE connection fails
- **Solution**: Check CORS settings in backend API and verify JWT token is valid

---

## Step 9: Cleanup

```bash
# Delete all microservices
kubectl delete -f microservices-deployment.yaml

# Delete Dapr components
kubectl delete -f dapr-components.yaml

# Delete Kafka topics
kubectl delete -f kafka-topics.yaml

# Delete Kafka cluster
kubectl delete -f kafka-cluster.yaml

# Uninstall Dapr
dapr uninstall --kubernetes

# Uninstall Strimzi
helm uninstall strimzi-kafka-operator -n kafka
kubectl delete namespace kafka

# Stop Minikube
minikube stop

# Delete Minikube cluster (optional)
minikube delete
```

---

## Next Steps

1. ✅ Local setup complete
2. Implement microservice business logic (Notification, Recurring, Audit)
3. Implement SSE bridge in backend API
4. Add distributed tracing with Zipkin
5. Create Helm charts for production deployment
6. Run full E2E test suite

---

## Additional Resources

- **Strimzi Documentation**: https://strimzi.io/docs/
- **Dapr Documentation**: https://docs.dapr.io/
- **Kafka Documentation**: https://kafka.apache.org/documentation/
- **Next.js SSE Guide**: https://nextjs.org/docs/app/building-your-application/routing/route-handlers
- **Minikube Documentation**: https://minikube.sigs.k8s.io/docs/

---

**Quickstart Status**: Complete
**Ready for Implementation**: Yes
**Estimated Setup Time**: 30-45 minutes
