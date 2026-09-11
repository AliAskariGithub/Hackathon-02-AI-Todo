# Event-Driven Architecture Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying the AI Todo Event-Driven Backbone to Minikube.

**Estimated Deployment Time**: 30-45 minutes

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (Next.js)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Dashboard   │  │  SSE Client  │  │  Task Forms  │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
│         │                  │                  │                  │
│         └──────────────────┴──────────────────┘                 │
└─────────────────────────────┬───────────────────────────────────┘
                              │ HTTP/SSE
┌─────────────────────────────┴───────────────────────────────────┐
│                      Backend API (FastAPI)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Task Router │  │ Events Router│  │Reminder Router│         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
│         │                  │                  │                  │
│         └──────────────────┴──────────────────┘                 │
│                            │                                     │
│                    ┌───────┴────────┐                           │
│                    │  Dapr Sidecar  │                           │
│                    └───────┬────────┘                           │
└────────────────────────────┼──────────────────────────────────┘
                             │
                    ┌────────┴─────────┐
                    │  Kafka (KRaft)   │
                    │  ┌────────────┐  │
                    │  │   Topics   │  │
                    │  │ - tasks    │  │
                    │  │ - reminders│  │
                    │  │ - notifs   │  │
                    │  │ - audit    │  │
                    │  │ - dlq      │  │
                    │  └────────────┘  │
                    └────────┬─────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────┴────────┐  ┌────────┴────────┐  ┌──────┴──────┐
│  Notification  │  │   Recurring     │  │    Audit    │
│    Service     │  │    Service      │  │   Service   │
│  ┌──────────┐  │  │  ┌──────────┐  │  │ ┌─────────┐ │
│  │  Dapr    │  │  │  │  Dapr    │  │  │ │  Dapr   │ │
│  │ Sidecar  │  │  │  │ Sidecar  │  │  │ │Sidecar  │ │
│  └──────────┘  │  │  └──────────┘  │  │ └─────────┘ │
└────────────────┘  └─────────────────┘  └─────────────┘
```

## Prerequisites

### Required Software

| Tool | Version | Status |
|------|---------|--------|
| Docker Desktop | 4.53+ | ⚠️ Required |
| Minikube | 1.32+ | ⚠️ Required |
| kubectl | 1.28+ | ⚠️ Required |
| Helm | 3.13+ | ⚠️ Required |
| Dapr CLI | 1.14+ | ⚠️ Required |

### Verify Installations

```bash
# Check all prerequisites
docker --version && \
minikube version && \
kubectl version --client && \
helm version && \
dapr --version
```

## Deployment Steps

### Step 1: Start Minikube

```bash
# Start Minikube with 4GB RAM and 2 CPUs
minikube start --memory=4096 --cpus=2 --driver=docker

# Enable required addons
minikube addons enable metrics-server
minikube addons enable ingress

# Verify cluster
kubectl cluster-info
kubectl get nodes
```

### Step 2: Install Strimzi Kafka Operator

```bash
# Add Strimzi Helm repository
helm repo add strimzi https://strimzi.io/charts/
helm repo update

# Create Kafka namespace
kubectl create namespace kafka

# Install Strimzi Operator
helm install strimzi-kafka-operator strimzi/strimzi-kafka-operator \
  --namespace kafka \
  --set watchNamespaces="{default,kafka}" \
  --wait

# Verify operator is running
kubectl get pods -n kafka
```

### Step 3: Deploy Kafka Cluster

```bash
# Deploy Kafka cluster using our Helm chart
cd charts/kafka-cluster
helm install kafka-cluster . --namespace default --wait

# Wait for Kafka to be ready (3-5 minutes)
kubectl wait kafka/ai-todo-kafka --for=condition=Ready --timeout=300s -n default

# Verify Kafka pods
kubectl get pods -l strimzi.io/cluster=ai-todo-kafka
```

### Step 4: Initialize Dapr

```bash
# Initialize Dapr on Kubernetes
dapr init --kubernetes --wait

# Verify Dapr installation
dapr status -k

# Check Dapr pods
kubectl get pods -n dapr-system
```

### Step 5: Deploy Dapr Components

```bash
# Deploy Dapr components using our Helm chart
cd charts/dapr-components
helm install dapr-components . --namespace default --wait

# Verify components
kubectl get components
```

### Step 6: Build and Push Docker Images

```bash
# Set Minikube Docker environment
eval $(minikube docker-env)

# Build backend image
cd backend
docker build -t ai-todo/backend-api:v1.0.0 .

# Build frontend image
cd ../frontend
docker build -t ai-todo/frontend:v1.0.0 .

# Build microservices
cd ../services/notification
docker build -t ai-todo/notification-service:v1.0.0 .

cd ../recurring
docker build -t ai-todo/recurring-service:v1.0.0 .

cd ../audit
docker build -t ai-todo/audit-service:v1.0.0 .

# Verify images
docker images | grep ai-todo
```

### Step 7: Deploy Microservices

```bash
# Deploy microservices using our Helm chart
cd charts/microservices
helm install microservices . --namespace default --wait

# Verify deployments
kubectl get deployments
kubectl get pods
```

### Step 8: Deploy Backend and Frontend

```bash
# Deploy backend
kubectl apply -f backend/k8s/deployment.yaml
kubectl apply -f backend/k8s/service.yaml

# Deploy frontend
kubectl apply -f frontend/k8s/deployment.yaml
kubectl apply -f frontend/k8s/service.yaml

# Verify all pods are running
kubectl get pods
```

### Step 9: Access the Application

```bash
# Port forward frontend
kubectl port-forward svc/frontend 3000:3000 &

# Port forward backend
kubectl port-forward svc/backend-api 8000:8000 &

# Access application
open http://localhost:3000
```

## Verification Tests

### Test 1: Real-Time Task Synchronization

1. Open two browser tabs to http://localhost:3000
2. Login to both tabs with the same user
3. Create a task in tab 1
4. Verify task appears in tab 2 within 2 seconds
5. Complete the task in tab 2
6. Verify task status updates in tab 1 within 2 seconds

**Expected Result**: ✅ Tasks sync across tabs in real-time

### Test 2: Recurring Task Generation

1. Create a task with daily recurrence
2. Set due date to today
3. Complete the task
4. Wait 5 seconds
5. Refresh the task list
6. Verify new task instance created with tomorrow's due date

**Expected Result**: ✅ Next recurring instance generated automatically

### Test 3: Reminder Notifications

1. Create a task with reminder scheduled for 1 minute in future
2. Wait for reminder time
3. Check notification service logs: `kubectl logs -l app=notification-service`
4. Verify notification logged with timestamp within 1 second of scheduled time

**Expected Result**: ✅ Reminder fires at exact scheduled time

### Test 4: Audit Trail

1. Perform various task operations (create, update, complete, delete)
2. Query audit logs: `kubectl port-forward svc/audit-service 8003:8003`
3. Access http://localhost:8003/audit/logs
4. Verify all events captured with correct timestamps

**Expected Result**: ✅ All events logged chronologically

## Monitoring

### View Logs

```bash
# Backend logs
kubectl logs -l app=backend-api -f

# Microservice logs
kubectl logs -l app=notification-service -f
kubectl logs -l app=recurring-service -f
kubectl logs -l app=audit-service -f

# Kafka logs
kubectl logs -l strimzi.io/cluster=ai-todo-kafka -f
```

### Check Metrics

```bash
# Pod resource usage
kubectl top pods

# Node resource usage
kubectl top nodes

# Dapr metrics
kubectl port-forward svc/dapr-dashboard 8080:8080 -n dapr-system
open http://localhost:8080
```

### View Kafka Topics

```bash
# List topics
kubectl exec -it ai-todo-kafka-kafka-0 -- bin/kafka-topics.sh \
  --bootstrap-server localhost:9092 --list

# View topic details
kubectl exec -it ai-todo-kafka-kafka-0 -- bin/kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --describe --topic todo.task.events
```

## Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl get pods

# Describe pod for events
kubectl describe pod <pod-name>

# Check logs
kubectl logs <pod-name>
```

### Kafka Connection Issues

```bash
# Verify Kafka is ready
kubectl get kafka

# Check Kafka logs
kubectl logs -l strimzi.io/cluster=ai-todo-kafka

# Test Kafka connectivity
kubectl run kafka-test --image=strimzi/kafka:latest-kafka-3.6.0 \
  --rm -it --restart=Never -- \
  bin/kafka-console-producer.sh \
  --bootstrap-server ai-todo-kafka-kafka-bootstrap:9092 \
  --topic test
```

### Dapr Issues

```bash
# Check Dapr status
dapr status -k

# View Dapr logs
kubectl logs -l app=dapr-sidecar-injector -n dapr-system

# Restart Dapr
dapr uninstall -k
dapr init -k --wait
```

### SSE Connection Issues

```bash
# Check backend logs for SSE errors
kubectl logs -l app=backend-api | grep SSE

# Verify events router is registered
kubectl exec -it <backend-pod> -- curl localhost:8000/api/events/health
```

## Cleanup

```bash
# Delete all deployments
helm uninstall microservices
helm uninstall dapr-components
helm uninstall kafka-cluster
helm uninstall strimzi-kafka-operator -n kafka

# Delete namespace
kubectl delete namespace kafka

# Stop Minikube
minikube stop

# Delete Minikube cluster (optional)
minikube delete
```

## Next Steps

1. **Production Deployment**: Adapt for production Kubernetes cluster
2. **Monitoring**: Add Prometheus and Grafana for metrics
3. **Tracing**: Configure Zipkin for distributed tracing
4. **Security**: Add TLS, network policies, and RBAC
5. **Scaling**: Configure horizontal pod autoscaling
6. **Backup**: Set up Kafka topic backups and disaster recovery

## Support

For issues or questions:
- Check logs: `kubectl logs <pod-name>`
- View events: `kubectl get events --sort-by='.lastTimestamp'`
- Describe resources: `kubectl describe <resource-type> <resource-name>`
