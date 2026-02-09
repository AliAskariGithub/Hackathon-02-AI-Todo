# AI Todo Application - Minikube Deployment Guide

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Detailed Deployment Steps](#detailed-deployment-steps)
- [Configuration](#configuration)
- [Accessing the Application](#accessing-the-application)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)
- [Maintenance](#maintenance)
- [Cleanup](#cleanup)

---

## Overview

This guide provides step-by-step instructions for deploying the AI Todo application to a local Minikube Kubernetes cluster using Helm.

### What Gets Deployed

- **Frontend:** Next.js 16.1.2 application (2 replicas)
- **Backend:** FastAPI Python application (1 replica)
- **Services:** NodePort (frontend) and ClusterIP (backend)
- **Configuration:** ConfigMaps and Secrets
- **Health Checks:** Liveness and readiness probes

### Deployment Time

- Initial setup: ~10 minutes
- Subsequent deployments: ~2 minutes

---

## Prerequisites

### Required Software

Ensure you have the following installed:

```bash
# Check versions
minikube version    # v1.38.0 or later
kubectl version     # v1.28.0 or later
helm version        # v3.12.0 or later
docker --version    # 20.10.0 or later
```

### Required Resources

- **CPU:** 4 cores minimum
- **Memory:** 8GB minimum
- **Disk:** 20GB free space
- **Network:** Internet connection for pulling images

### Project Requirements

1. **Docker Images Built:**
   ```bash
   docker images | grep ai-todo
   # Should show:
   # ai-todo-frontend:latest
   # ai-todo-backend:latest
   ```

2. **Environment Variables:**
   - Database URL (Neon PostgreSQL)
   - JWT Secret
   - Better Auth Secret
   - Groq API Key

---

## Architecture

### Deployment Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Your Browser                          │
│              http://localhost:8080                       │
└────────────────────┬────────────────────────────────────┘
                     │ Port Forwarding
┌────────────────────▼────────────────────────────────────┐
│                Minikube Cluster                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │  Frontend Service (NodePort)                       │ │
│  │  Port: 80 → NodePort: 31752                        │ │
│  │  ┌──────────────────┐  ┌──────────────────┐       │ │
│  │  │  Frontend Pod 1  │  │  Frontend Pod 2  │       │ │
│  │  │  Next.js:3000    │  │  Next.js:3000    │       │ │
│  │  └──────────────────┘  └──────────────────┘       │ │
│  └────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────┐ │
│  │  Backend Service (ClusterIP)                       │ │
│  │  Port: 8000                                        │ │
│  │  ┌──────────────────┐                              │ │
│  │  │  Backend Pod     │                              │ │
│  │  │  FastAPI:8000    │                              │ │
│  │  └──────────────────┘                              │ │
│  └────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────┐ │
│  │  ConfigMaps & Secrets                              │ │
│  │  - ai-todo-config                                  │ │
│  │  - ai-todo-backend-config                          │ │
│  │  - ai-todo-secrets                                 │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              External Services                           │
│  - Neon PostgreSQL (Database)                           │
│  - Groq API (AI Chat)                                   │
└─────────────────────────────────────────────────────────┘
```

### Resource Allocation

| Component | Replicas | CPU Request | CPU Limit | Memory Request | Memory Limit |
|-----------|----------|-------------|-----------|----------------|--------------|
| Frontend  | 2        | 250m        | 500m      | 256Mi          | 512Mi        |
| Backend   | 1        | 500m        | 1000m     | 512Mi          | 1Gi          |

---

## Quick Start

For experienced users, here's the quick deployment:

```bash
# 1. Start Minikube
minikube start --driver=docker --cpus=4 --memory=8192

# 2. Build Docker images
docker-compose build

# 3. Load images into Minikube
minikube image load ai-todo-frontend:latest
minikube image load ai-todo-backend:latest

# 4. Deploy with Helm
helm install ai-todo ./charts/ai-todo \
  --set image.frontend.tag=latest \
  --set image.backend.tag=latest \
  --set secrets.databaseUrl="your-database-url" \
  --set secrets.betterAuthSecret="your-auth-secret" \
  --set secrets.jwtSecret="your-jwt-secret" \
  --set secrets.groqApiKey="your-groq-api-key"

# 5. Set up port forwarding
kubectl port-forward service/ai-todo-frontend 8080:80 &
kubectl port-forward service/backend-service 8000:8000 &

# 6. Access application
# Frontend: http://localhost:8080
# Backend: http://localhost:8000
```

---

## Detailed Deployment Steps

### Step 1: Start Minikube

Start a Minikube cluster with appropriate resources:

```bash
# Start Minikube with Docker driver
minikube start --driver=docker --cpus=4 --memory=8192 --disk-size=50g

# Verify Minikube is running
minikube status

# Expected output:
# minikube
# type: Control Plane
# host: Running
# kubelet: Running
# apiserver: Running
# kubeconfig: Configured
```

**Troubleshooting:**
- If Minikube fails to start, try: `minikube delete && minikube start`
- On Windows, ensure Docker Desktop is running
- Check available resources: `docker info`

### Step 2: Configure kubectl

Ensure kubectl is configured to use Minikube:

```bash
# Set context to Minikube
kubectl config use-context minikube

# Verify connection
kubectl cluster-info

# Check nodes
kubectl get nodes

# Expected output:
# NAME       STATUS   ROLES           AGE   VERSION
# minikube   Ready    control-plane   1m    v1.28.3
```

### Step 3: Build Docker Images

Build the frontend and backend Docker images:

```bash
# Navigate to project root
cd /path/to/hackathon-ai-todo

# Build using docker-compose
docker-compose build

# Verify images are built
docker images | grep ai-todo

# Expected output:
# ai-todo-frontend   latest   <image-id>   <size>
# ai-todo-backend    latest   <image-id>   <size>
```

**Alternative: Build individually**
```bash
# Build frontend
cd frontend
docker build -t ai-todo-frontend:latest .

# Build backend
cd ../backend
docker build -t ai-todo-backend:latest .
```

### Step 4: Load Images into Minikube

Transfer Docker images to Minikube's Docker daemon:

```bash
# Load frontend image
minikube image load ai-todo-frontend:latest

# Load backend image
minikube image load ai-todo-backend:latest

# Verify images are loaded
minikube image ls | grep ai-todo

# Expected output:
# docker.io/library/ai-todo-frontend:latest
# docker.io/library/ai-todo-backend:latest
```

**Note:** This step is crucial because Minikube runs in its own Docker environment.

### Step 5: Prepare Configuration

Create a custom values file for your deployment:

```bash
# Copy example values
cp charts/ai-todo/values.yaml charts/ai-todo/values-local.yaml

# Edit the file with your configuration
# Update the following sections:
# - secrets.databaseUrl
# - secrets.betterAuthSecret
# - secrets.jwtSecret
# - secrets.groqApiKey
```

**Example values-local.yaml:**
```yaml
image:
  frontend:
    repository: ai-todo-frontend
    tag: latest
    pullPolicy: IfNotPresent
  backend:
    repository: ai-todo-backend
    tag: latest
    pullPolicy: IfNotPresent

secrets:
  databaseUrl: "postgresql://user:pass@host:5432/db"
  betterAuthSecret: "your-32-char-secret-here"
  jwtSecret: "your-jwt-secret-here"
  groqApiKey: "your-groq-api-key-here"

config:
  allowedOrigins: "http://localhost:3000,http://localhost:8080"
  siteUrl: "http://localhost:3000"
```

### Step 6: Deploy with Helm

Deploy the application using Helm:

```bash
# Install the Helm chart
helm install ai-todo ./charts/ai-todo \
  --set image.frontend.tag=latest \
  --set image.backend.tag=latest \
  --set secrets.databaseUrl="postgresql://user:pass@host:5432/db" \
  --set secrets.betterAuthSecret="your-auth-secret" \
  --set secrets.jwtSecret="your-jwt-secret" \
  --set secrets.groqApiKey="your-groq-api-key"

# Or use the values file
helm install ai-todo ./charts/ai-todo -f charts/ai-todo/values-local.yaml

# Check deployment status
helm status ai-todo

# Expected output:
# NAME: ai-todo
# LAST DEPLOYED: <timestamp>
# NAMESPACE: default
# STATUS: deployed
# REVISION: 1
```

### Step 7: Verify Deployment

Wait for all pods to be ready:

```bash
# Watch pod status
kubectl get pods -l app.kubernetes.io/instance=ai-todo --watch

# Expected output (after ~1-2 minutes):
# NAME                                READY   STATUS    RESTARTS   AGE
# ai-todo-backend-xxxxxxxxxx-xxxxx    1/1     Running   0          2m
# ai-todo-frontend-xxxxxxxxxx-xxxxx   1/1     Running   0          2m
# ai-todo-frontend-xxxxxxxxxx-xxxxx   1/1     Running   0          2m

# Press Ctrl+C to stop watching

# Check all resources
kubectl get all -l app.kubernetes.io/instance=ai-todo
```

**Troubleshooting:**
- If pods are in `ImagePullBackOff`: Verify images are loaded in Minikube
- If pods are in `CrashLoopBackOff`: Check logs with `kubectl logs <pod-name>`
- If pods are `Pending`: Check resource availability with `kubectl describe pod <pod-name>`

### Step 8: Set Up Port Forwarding

Forward ports to access the application from your host machine:

```bash
# Forward frontend service (in background)
kubectl port-forward service/ai-todo-frontend 8080:80 &

# Forward backend service (in background)
kubectl port-forward service/backend-service 8000:8000 &

# Verify port forwarding
netstat -ano | findstr ":8080"  # Windows
lsof -i :8080                    # Linux/Mac

netstat -ano | findstr ":8000"  # Windows
lsof -i :8000                    # Linux/Mac
```

**Alternative: Use minikube service**
```bash
# This automatically creates a tunnel and opens in browser
minikube service ai-todo-frontend
```

**Note:** Port forwarding processes run in the background. To stop them:
```bash
# Find process ID
ps aux | grep "kubectl port-forward"

# Kill process
kill <pid>
```

---

## Configuration

### ConfigMaps

The deployment uses two ConfigMaps:

**1. ai-todo-config (Shared Configuration)**
```yaml
NEXT_PUBLIC_API_BASE_URL: http://localhost:8000
NEXT_PUBLIC_SITE_URL: http://localhost:3000
NEXT_PUBLIC_DEBUG: "true"
ALLOWED_ORIGINS: http://localhost:3000,http://localhost:8080
LOG_LEVEL: info
```

**2. ai-todo-backend-config (Backend-Specific)**
```yaml
HOST: 0.0.0.0
PORT: "8000"
DEBUG: "false"
```

**Update ConfigMap:**
```bash
# Edit ConfigMap
kubectl edit configmap ai-todo-config

# Or patch specific value
kubectl patch configmap ai-todo-config \
  --type merge \
  -p '{"data":{"ALLOWED_ORIGINS":"http://localhost:3000,http://localhost:8080"}}'

# Restart pods to apply changes
kubectl rollout restart deployment/ai-todo-frontend
kubectl rollout restart deployment/ai-todo-backend
```

### Secrets

Secrets are stored in `ai-todo-secrets`:

```bash
# View secret (base64 encoded)
kubectl get secret ai-todo-secrets -o yaml

# Decode secret value
kubectl get secret ai-todo-secrets -o jsonpath='{.data.DATABASE_URL}' | base64 --decode

# Update secret
kubectl create secret generic ai-todo-secrets \
  --from-literal=DATABASE_URL="new-database-url" \
  --from-literal=BETTER_AUTH_SECRET="new-auth-secret" \
  --from-literal=JWT_SECRET="new-jwt-secret" \
  --from-literal=GROQ_API_KEY="new-groq-key" \
  --dry-run=client -o yaml | kubectl apply -f -

# Restart pods to use new secrets
kubectl rollout restart deployment/ai-todo-backend
```

### Resource Limits

Adjust resource limits in `values.yaml`:

```yaml
resources:
  frontend:
    requests:
      memory: "256Mi"
      cpu: "250m"
    limits:
      memory: "512Mi"
      cpu: "500m"
  backend:
    requests:
      memory: "512Mi"
      cpu: "500m"
    limits:
      memory: "1Gi"
      cpu: "1000m"
```

**Update resources:**
```bash
# Upgrade with new values
helm upgrade ai-todo ./charts/ai-todo -f charts/ai-todo/values.yaml
```

---

## Accessing the Application

The application can be accessed using three different methods:

### Method 1: Port Forwarding (Recommended for Development)

**Frontend:** http://localhost:8080
**Backend:** http://localhost:8000

**Setup:**
```bash
# Forward frontend service
kubectl port-forward service/ai-todo-frontend 8080:80 &

# Forward backend service
kubectl port-forward service/backend-service 8000:8000 &
```

**Features:**
- Homepage with statistics
- User authentication (signup/login)
- Task dashboard
- AI chat interface
- Testimonials
- Settings

**Backend Endpoints:**
- Health check: http://localhost:8000/health
- API documentation: http://localhost:8000/docs
- OpenAPI spec: http://localhost:8000/openapi.json

### Method 2: NodePort (Direct Minikube Access)

**Frontend:** http://192.168.49.2:31752

**Setup:**
```bash
# Get Minikube IP
minikube ip

# Get NodePort
kubectl get svc ai-todo-frontend -o jsonpath='{.spec.ports[0].nodePort}'

# Access at: http://<minikube-ip>:<nodeport>
```

### Method 3: Ingress (Production-like Setup)

**Frontend:** http://ai-todo.local
**Backend API:** http://ai-todo.local/api
**API Docs:** http://ai-todo.local/docs
**Health Check:** http://ai-todo.local/health

**Setup:**

1. Enable Ingress addon:
```bash
minikube addons enable ingress
```

2. Apply Ingress configuration:
```bash
kubectl apply -f k8s/ingress.yaml
```

3. Add to hosts file:
   - **Windows:** `C:\Windows\System32\drivers\etc\hosts`
   - **Linux/Mac:** `/etc/hosts`

   Add this line:
   ```
   192.168.49.2 ai-todo.local
   ```

4. Access the application at http://ai-todo.local

**Note:** See `docs/INGRESS_SETUP.md` for detailed Ingress configuration and troubleshooting.

### Kubernetes Dashboard

```bash
# Open Kubernetes dashboard
minikube dashboard

# Or get URL
minikube dashboard --url
```

---

## Verification

### 1. Check Pod Status

```bash
# All pods should be Running
kubectl get pods -l app.kubernetes.io/instance=ai-todo

# Check pod details
kubectl describe pod <pod-name>

# View pod logs
kubectl logs <pod-name>

# Follow logs
kubectl logs -f <pod-name>
```

### 2. Check Services

```bash
# List services
kubectl get services -l app.kubernetes.io/instance=ai-todo

# Check service endpoints
kubectl get endpoints

# Describe service
kubectl describe service ai-todo-frontend
kubectl describe service backend-service
```

### 3. Test Backend Health

```bash
# Test health endpoint
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","timestamp":"2026-02-10T...","version":"1.0.8"}

# Test API documentation
curl -I http://localhost:8000/docs

# Expected: HTTP/1.1 200 OK
```

### 4. Test Frontend

```bash
# Test frontend homepage
curl -I http://localhost:8080

# Expected: HTTP/1.1 200 OK

# Open in browser
# Windows: start http://localhost:8080
# Mac: open http://localhost:8080
# Linux: xdg-open http://localhost:8080
```

### 5. Test Frontend-Backend Connection

```bash
# Check backend logs for incoming requests
kubectl logs -f deployment/ai-todo-backend

# Open frontend in browser and perform actions
# You should see API requests in the backend logs
```

### 6. Check Resource Usage

```bash
# Enable metrics server (if not already enabled)
minikube addons enable metrics-server

# Wait a minute for metrics to be collected

# Check pod resource usage
kubectl top pods -l app.kubernetes.io/instance=ai-todo

# Check node resource usage
kubectl top nodes
```

---

## Troubleshooting

### Common Issues and Solutions

#### 1. Pods Not Starting

**Symptom:** Pods stuck in `Pending`, `ImagePullBackOff`, or `CrashLoopBackOff`

**Solutions:**

```bash
# Check pod status
kubectl describe pod <pod-name>

# Common issues:

# A. ImagePullBackOff - Image not found
# Solution: Load image into Minikube
minikube image load ai-todo-frontend:latest
minikube image load ai-todo-backend:latest

# B. CrashLoopBackOff - Application crashing
# Solution: Check logs
kubectl logs <pod-name>
kubectl logs <pod-name> --previous  # Previous container logs

# C. Pending - Insufficient resources
# Solution: Check node resources
kubectl describe nodes
# Increase Minikube resources:
minikube delete
minikube start --cpus=4 --memory=8192
```

#### 2. Frontend Cannot Connect to Backend

**Symptom:** Frontend loads but shows no data, CORS errors in browser console

**Solutions:**

```bash
# A. Check CORS configuration
kubectl get configmap ai-todo-config -o yaml | grep ALLOWED_ORIGINS

# B. Update CORS to include frontend URL
kubectl patch configmap ai-todo-config \
  --type merge \
  -p '{"data":{"ALLOWED_ORIGINS":"http://localhost:3000,http://localhost:8080"}}'

# C. Restart backend
kubectl rollout restart deployment/ai-todo-backend

# D. Verify backend is accessible
curl http://localhost:8000/health

# E. Check backend logs for CORS errors
kubectl logs -f deployment/ai-todo-backend | grep -i "cors\|origin"
```

#### 3. Port Forwarding Not Working

**Symptom:** Cannot access application at localhost:8080 or localhost:8000

**Solutions:**

```bash
# A. Check if ports are in use
netstat -ano | findstr ":8080"  # Windows
lsof -i :8080                    # Linux/Mac

# B. Kill existing port forwarding
# Find process ID and kill it
kill <pid>

# C. Restart port forwarding
kubectl port-forward service/ai-todo-frontend 8080:80 &
kubectl port-forward service/backend-service 8000:8000 &

# D. Use different ports
kubectl port-forward service/ai-todo-frontend 8081:80 &
kubectl port-forward service/backend-service 8001:8000 &

# E. Use minikube service instead
minikube service ai-todo-frontend
```

#### 4. Database Connection Errors

**Symptom:** Backend logs show database connection errors

**Solutions:**

```bash
# A. Check database URL secret
kubectl get secret ai-todo-secrets -o jsonpath='{.data.DATABASE_URL}' | base64 --decode

# B. Update database URL
kubectl create secret generic ai-todo-secrets \
  --from-literal=DATABASE_URL="correct-database-url" \
  --dry-run=client -o yaml | kubectl apply -f -

# C. Restart backend
kubectl rollout restart deployment/ai-todo-backend

# D. Check backend logs
kubectl logs -f deployment/ai-todo-backend | grep -i "database\|connection"
```

#### 5. Helm Deployment Fails

**Symptom:** `helm install` or `helm upgrade` fails

**Solutions:**

```bash
# A. Check Helm chart syntax
helm lint ./charts/ai-todo

# B. Dry run to see what would be deployed
helm install ai-todo ./charts/ai-todo --dry-run --debug

# C. Check existing release
helm list

# D. Uninstall and reinstall
helm uninstall ai-todo
helm install ai-todo ./charts/ai-todo -f values-local.yaml

# E. Check Helm release status
helm status ai-todo

# F. View Helm release history
helm history ai-todo
```

#### 6. Minikube Cluster Issues

**Symptom:** Minikube not responding, kubectl commands failing

**Solutions:**

```bash
# A. Check Minikube status
minikube status

# B. Restart Minikube
minikube stop
minikube start

# C. Delete and recreate cluster
minikube delete
minikube start --driver=docker --cpus=4 --memory=8192

# D. Check Docker is running
docker ps

# E. View Minikube logs
minikube logs

# F. SSH into Minikube to debug
minikube ssh
```

### Debug Commands

```bash
# Get all resources
kubectl get all -l app.kubernetes.io/instance=ai-todo

# Get events (sorted by time)
kubectl get events --sort-by=.metadata.creationTimestamp

# Describe all pods
kubectl describe pods -l app.kubernetes.io/instance=ai-todo

# Get pod logs (all containers)
kubectl logs <pod-name> --all-containers=true

# Execute command in pod
kubectl exec -it <pod-name> -- /bin/sh

# Check ConfigMaps
kubectl get configmaps -l app.kubernetes.io/instance=ai-todo

# Check Secrets
kubectl get secrets -l app.kubernetes.io/instance=ai-todo

# Check Services
kubectl get services -l app.kubernetes.io/instance=ai-todo

# Check Endpoints
kubectl get endpoints

# Port forward for debugging
kubectl port-forward <pod-name> 8080:3000  # Frontend
kubectl port-forward <pod-name> 8000:8000  # Backend
```

---

## Maintenance

### Updating the Application

#### Update Docker Images

```bash
# 1. Rebuild Docker images
docker-compose build

# 2. Load new images into Minikube
minikube image load ai-todo-frontend:latest
minikube image load ai-todo-backend:latest

# 3. Restart deployments to use new images
kubectl rollout restart deployment/ai-todo-frontend
kubectl rollout restart deployment/ai-todo-backend

# 4. Monitor rollout
kubectl rollout status deployment/ai-todo-frontend
kubectl rollout status deployment/ai-todo-backend
```

#### Update Configuration

```bash
# 1. Edit values file
nano charts/ai-todo/values.yaml

# 2. Upgrade Helm release
helm upgrade ai-todo ./charts/ai-todo -f charts/ai-todo/values.yaml

# 3. Verify upgrade
helm status ai-todo
kubectl get pods -l app.kubernetes.io/instance=ai-todo
```

#### Rollback Deployment

```bash
# View release history
helm history ai-todo

# Rollback to previous version
helm rollback ai-todo

# Rollback to specific revision
helm rollback ai-todo <revision-number>

# Verify rollback
helm status ai-todo
```

### Scaling

```bash
# Scale frontend
kubectl scale deployment ai-todo-frontend --replicas=3

# Scale backend
kubectl scale deployment ai-todo-backend --replicas=2

# Verify scaling
kubectl get pods -l app.kubernetes.io/instance=ai-todo

# Update Helm values for persistent scaling
# Edit values.yaml:
# replicaCount:
#   frontend: 3
#   backend: 2

# Apply changes
helm upgrade ai-todo ./charts/ai-todo -f charts/ai-todo/values.yaml
```

### Monitoring

```bash
# Enable metrics server
minikube addons enable metrics-server

# View resource usage
kubectl top pods -l app.kubernetes.io/instance=ai-todo
kubectl top nodes

# Stream logs
kubectl logs -f deployment/ai-todo-frontend
kubectl logs -f deployment/ai-todo-backend

# View events
kubectl get events --watch
```

### Backup

```bash
# Backup Helm values
helm get values ai-todo > backup-values.yaml

# Backup Kubernetes resources
kubectl get all -l app.kubernetes.io/instance=ai-todo -o yaml > backup-resources.yaml

# Backup ConfigMaps
kubectl get configmaps -l app.kubernetes.io/instance=ai-todo -o yaml > backup-configmaps.yaml

# Backup Secrets
kubectl get secrets -l app.kubernetes.io/instance=ai-todo -o yaml > backup-secrets.yaml
```

---

## Cleanup

### Remove Application

```bash
# Uninstall Helm release
helm uninstall ai-todo

# Verify removal
kubectl get all -l app.kubernetes.io/instance=ai-todo

# Remove any remaining resources
kubectl delete all -l app.kubernetes.io/instance=ai-todo
kubectl delete configmaps -l app.kubernetes.io/instance=ai-todo
kubectl delete secrets -l app.kubernetes.io/instance=ai-todo
```

### Stop Minikube

```bash
# Stop Minikube (preserves cluster state)
minikube stop

# Delete Minikube cluster (removes everything)
minikube delete

# Remove all Minikube profiles
minikube delete --all
```

### Clean Docker Images

```bash
# Remove Docker images
docker rmi ai-todo-frontend:latest
docker rmi ai-todo-backend:latest

# Clean up unused Docker resources
docker system prune -a
```

---

## Next Steps

### Production Deployment

Once you've tested the application on Minikube, consider:

1. **Deploy to Cloud Kubernetes:**
   - AWS EKS
   - Google Cloud GKE
   - Azure AKS

2. **Set Up CI/CD:**
   - GitHub Actions
   - GitLab CI
   - Jenkins

3. **Add Monitoring:**
   - Prometheus
   - Grafana
   - ELK Stack

4. **Configure Ingress:**
   - NGINX Ingress Controller
   - Traefik
   - Custom domain and SSL

5. **Implement Security:**
   - Network Policies
   - RBAC
   - Pod Security Policies
   - Secrets Management (Vault, Sealed Secrets)

6. **Add Persistence:**
   - Persistent Volumes
   - StatefulSets
   - Database backups

### Additional Resources

- **Helm Chart:** `charts/ai-todo/`
- **Docker Compose:** `docker-compose.yml`
- **Kubernetes Manifests:** `charts/ai-todo/templates/`
- **General Guide:** `docs/MINIKUBE_GUIDE.md`

---

## Support

### Getting Help

- **Check Logs:** `kubectl logs <pod-name>`
- **Describe Resources:** `kubectl describe <resource-type> <resource-name>`
- **View Events:** `kubectl get events`
- **Minikube Logs:** `minikube logs`

### Useful Links

- **Kubernetes Documentation:** https://kubernetes.io/docs/
- **Helm Documentation:** https://helm.sh/docs/
- **Minikube Documentation:** https://minikube.sigs.k8s.io/docs/
- **Project Repository:** https://github.com/your-repo/hackathon-ai-todo

---

**Last Updated:** February 2026
**Version:** 1.0.0
**Deployment Target:** Minikube v1.38.0, Kubernetes v1.28.3, Helm v3.12.0
