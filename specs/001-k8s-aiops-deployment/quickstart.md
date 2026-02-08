# Quickstart: Local Kubernetes Deployment

**Feature**: 001-k8s-aiops-deployment
**Date**: 2026-02-08
**Purpose**: Step-by-step guide for deploying AI Todo application to local Minikube cluster

## Prerequisites

Before starting, ensure you have the following installed and configured:

### Required Software

- **Docker Desktop 4.53+**: Container runtime (required for Gordon compatibility)
  - Download: https://www.docker.com/products/docker-desktop
  - Verify: `docker --version`

- **Minikube**: Local Kubernetes cluster
  - Install: https://minikube.sigs.k8s.io/docs/start/
  - Verify: `minikube version`

- **Helm 3+**: Kubernetes package manager
  - Install: https://helm.sh/docs/intro/install/
  - Verify: `helm version`

- **kubectl**: Kubernetes CLI
  - Install: https://kubernetes.io/docs/tasks/tools/
  - Verify: `kubectl version --client`

### AI Agents (Optional but Recommended)

- **Gordon (Docker AI)**: For Dockerfile generation and auditing
  - Install: https://www.docker.com/products/docker-ai
  - Verify: `docker ai --version`

- **kubectl-ai**: For Kubernetes manifest generation
  - Install: Follow kubectl-ai documentation
  - Verify: `kubectl-ai --version`

- **Kagent**: For cluster health analysis
  - Install: Follow Kagent documentation
  - Verify: `kagent --version`

### System Requirements

- **CPU**: Minimum 2 cores (4 cores recommended)
- **RAM**: Minimum 4GB (8GB recommended)
- **Disk**: Minimum 20GB free space
- **OS**: Windows 10+, macOS 10.15+, or Linux

---

## Step 1: Start Minikube Cluster

### 1.1 Start Minikube with Docker Driver

```bash
# Start Minikube with recommended resources
minikube start --driver=docker --cpus=4 --memory=8192

# Verify cluster is running
minikube status
```

**Expected Output**:
```
minikube
type: Control Plane
host: Running
kubelet: Running
apiserver: Running
kubeconfig: Configured
```

### 1.2 Enable Minikube Addons (Optional)

```bash
# Enable metrics-server for resource monitoring
minikube addons enable metrics-server

# Enable dashboard for web UI
minikube addons enable dashboard
```

### 1.3 Verify kubectl Context

```bash
# Check current context
kubectl config current-context

# Should output: minikube

# Verify cluster access
kubectl get nodes
```

**Expected Output**:
```
NAME       STATUS   ROLES           AGE   VERSION
minikube   Ready    control-plane   1m    v1.28.x
```

---

## Step 2: Prepare Environment Configuration

### 2.1 Create Kubernetes Secrets

Create a file named `secrets.yaml` (DO NOT commit to git):

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: ai-todo-secrets
  namespace: default
type: Opaque
stringData:
  DATABASE_URL: "postgresql+asyncpg://user:password@host:port/database"
  BETTER_AUTH_SECRET: "your-better-auth-secret-key-here"
  JWT_SECRET: "your-jwt-secret-key-here"
  GROQ_API_KEY: "your-groq-api-key-here"
```

**Important**: Replace placeholder values with actual credentials.

### 2.2 Apply Secrets to Cluster

```bash
# Apply secrets
kubectl apply -f secrets.yaml

# Verify secrets created
kubectl get secrets
```

### 2.3 Create ConfigMap (Optional)

If you need non-sensitive configuration:

```bash
kubectl create configmap ai-todo-config \
  --from-literal=LOG_LEVEL=info \
  --from-literal=DEBUG=true \
  --from-literal=ALLOWED_ORIGINS=http://localhost:3000 \
  --from-literal=ENABLE_RATE_LIMITING=false
```

---

## Step 3: Build Container Images

### 3.1 Build Frontend Image

```bash
# Navigate to frontend directory
cd frontend

# Build Docker image
docker build -t ai-todo-frontend:v1.0.0 .

# Verify image built
docker images | grep ai-todo-frontend
```

**Expected Output**:
```
ai-todo-frontend   v1.0.0   abc123def456   2 minutes ago   450MB
```

### 3.2 Build Backend Image

```bash
# Navigate to backend directory
cd ../backend

# Build Docker image
docker build -t ai-todo-backend:v1.0.0 .

# Verify image built
docker images | grep ai-todo-backend
```

**Expected Output**:
```
ai-todo-backend   v1.0.0   def456ghi789   2 minutes ago   280MB
```

---

## Step 4: Load Images into Minikube

Minikube runs in its own Docker environment, so images must be loaded explicitly.

### 4.1 Load Frontend Image

```bash
minikube image load ai-todo-frontend:v1.0.0
```

### 4.2 Load Backend Image

```bash
minikube image load ai-todo-backend:v1.0.0
```

### 4.3 Verify Images in Minikube

```bash
minikube image ls | grep ai-todo
```

**Expected Output**:
```
docker.io/library/ai-todo-frontend:v1.0.0
docker.io/library/ai-todo-backend:v1.0.0
```

---

## Step 5: Deploy with Helm

### 5.1 Install Helm Chart

```bash
# Navigate to repository root
cd ..

# Install Helm chart
helm install ai-todo ./charts/ai-todo

# Verify installation
helm list
```

**Expected Output**:
```
NAME     NAMESPACE  REVISION  UPDATED                                STATUS    CHART          APP VERSION
ai-todo  default    1         2026-02-08 10:30:00.000000 -0800 PST  deployed  ai-todo-1.0.0  v1.0.0
```

### 5.2 Watch Deployment Progress

```bash
# Watch pods starting
kubectl get pods -w

# Press Ctrl+C to stop watching
```

**Expected Output** (after ~2 minutes):
```
NAME                        READY   STATUS    RESTARTS   AGE
frontend-xxxxxxxxxx-xxxxx   1/1     Running   0          2m
frontend-xxxxxxxxxx-xxxxx   1/1     Running   0          2m
backend-xxxxxxxxxx-xxxxx    1/1     Running   0          2m
```

### 5.3 Verify Deployment Health

```bash
# Check deployment status
kubectl get deployments

# Check service endpoints
kubectl get services

# Check pod logs (if needed)
kubectl logs -l app.kubernetes.io/name=frontend
kubectl logs -l app.kubernetes.io/name=backend
```

---

## Step 6: Access the Application

### Option A: NodePort Access (Recommended for Local)

```bash
# Get Minikube IP
minikube ip

# Get frontend NodePort
kubectl get service frontend-service -o jsonpath='{.spec.ports[0].nodePort}'

# Access application
# Open browser to: http://<minikube-ip>:<nodePort>
```

**Example**:
```bash
# If Minikube IP is 192.168.49.2 and NodePort is 30080
# Open: http://192.168.49.2:30080
```

### Option B: LoadBalancer with Minikube Tunnel

```bash
# Start Minikube tunnel (requires sudo/admin)
minikube tunnel

# In another terminal, get external IP
kubectl get service frontend-service

# Access application at: http://localhost:80
```

### Option C: Port Forwarding (Simplest)

```bash
# Forward local port to frontend service
kubectl port-forward service/frontend-service 3000:80

# Access application at: http://localhost:3000
```

---

## Step 7: Verify Application Functionality

### 7.1 Test Frontend Access

1. Open browser to application URL
2. Verify home page loads
3. Check that UI renders correctly

### 7.2 Test Authentication

1. Navigate to signup page
2. Create a new account
3. Log in with credentials
4. Verify redirect to dashboard

### 7.3 Test Task Management

1. Create a new task
2. Update task status
3. Delete a task
4. Verify all operations work

### 7.4 Test AI Chat

1. Navigate to chat page
2. Send a message to AI assistant
3. Verify response is received
4. Test task creation via chat

---

## Step 8: Monitor Cluster Health (with Kagent)

### 8.1 Analyze Cluster Health

```bash
kagent "analyze the cluster health"
```

**Expected Output**: Healthy status with all pods running

### 8.2 Check Resource Utilization

```bash
# View resource usage
kubectl top nodes
kubectl top pods
```

### 8.3 Optimize Resources (if needed)

```bash
kagent "optimize resource allocation"
```

---

## Troubleshooting

### Issue: Pods in ImagePullBackOff

**Cause**: Images not loaded into Minikube

**Solution**:
```bash
# Load images into Minikube
minikube image load ai-todo-frontend:v1.0.0
minikube image load ai-todo-backend:v1.0.0

# Restart deployment
kubectl rollout restart deployment/frontend
kubectl rollout restart deployment/backend
```

---

### Issue: Pods in CrashLoopBackOff

**Cause**: Application startup failure, missing environment variables

**Solution**:
```bash
# Check pod logs
kubectl logs <pod-name>

# Verify secrets exist
kubectl get secrets

# Verify environment variables
kubectl exec <pod-name> -- env | grep DATABASE_URL
```

---

### Issue: Service Has No Endpoints

**Cause**: Pods not ready or label mismatch

**Solution**:
```bash
# Check pod readiness
kubectl get pods

# Verify service selector matches pod labels
kubectl describe service frontend-service
kubectl get pods --show-labels
```

---

### Issue: Cannot Access Application

**Cause**: Service not exposed or firewall blocking

**Solution**:
```bash
# Verify service type
kubectl get service frontend-service

# Try port forwarding instead
kubectl port-forward service/frontend-service 3000:80

# Check Minikube tunnel is running (if using LoadBalancer)
minikube tunnel
```

---

### Issue: High Memory Usage / OOMKilled

**Cause**: Memory limits too low

**Solution**:
```bash
# Check resource limits
kubectl describe pod <pod-name>

# Update Helm values and upgrade
helm upgrade ai-todo ./charts/ai-todo \
  --set frontend.resources.limits.memory=1Gi
```

---

## Cleanup

### Uninstall Application

```bash
# Uninstall Helm release
helm uninstall ai-todo

# Verify pods are terminated
kubectl get pods
```

### Delete Secrets and ConfigMaps

```bash
# Delete secrets
kubectl delete secret ai-todo-secrets

# Delete configmap
kubectl delete configmap ai-todo-config
```

### Stop Minikube

```bash
# Stop Minikube cluster
minikube stop

# Delete Minikube cluster (optional)
minikube delete
```

---

## Automated Deployment Script

For convenience, use the automated deployment script:

```bash
# Make script executable
chmod +x scripts/deploy.sh

# Run deployment
./scripts/deploy.sh

# Script performs:
# 1. Build Docker images
# 2. Load images into Minikube
# 3. Install/upgrade Helm chart
# 4. Wait for pods to be ready
# 5. Display access instructions
```

---

## Known Limitations

This section documents current limitations and constraints of the Kubernetes deployment.

### Infrastructure Limitations

#### 1. Local Development Only
- **Current State**: Deployment is optimized for Minikube (local Kubernetes)
- **Impact**: Not production-ready without modifications
- **Workaround**: For production deployment, update:
  - Service types (use LoadBalancer or Ingress)
  - Resource limits (increase for production workloads)
  - Image registry (push to container registry)
  - Secrets management (use external secret manager)

#### 2. Image Pull Policy
- **Current State**: `imagePullPolicy: IfNotPresent`
- **Impact**: Images must be pre-loaded into Minikube
- **Workaround**: Run `./scripts/load-images.sh` after building images
- **Why**: Prevents pulling from Docker Hub (images are local-only)

#### 3. Network Connectivity Requirements
- **Current State**: Docker Hub DNS resolution may fail on some networks
- **Impact**: Cannot pull base images (node:20-alpine, python:3.11-slim)
- **Workaround**:
  - Configure Docker DNS settings (8.8.8.8, 1.1.1.1)
  - Disable VPN temporarily
  - Use alternative registry mirrors
- **Status**: Known issue documented in TROUBLESHOOTING.md

#### 4. Resource Requirements
- **Minimum**: 2 CPUs, 4GB RAM, 20GB disk
- **Recommended**: 4 CPUs, 8GB RAM, 40GB disk
- **Impact**: Lower resources may cause:
  - Slow pod startup
  - OOMKilled errors
  - Deployment timeouts
- **Workaround**: Reduce replica counts or resource limits

### Application Limitations

#### 5. Backend Scaling
- **Current State**: Backend limited to 1 replica
- **Impact**: No horizontal scaling for backend
- **Reason**: Potential database connection pool issues
- **Workaround**: Increase resource limits instead of replicas
- **Future**: Implement connection pooling (PgBouncer)

#### 6. Database Connectivity
- **Current State**: Uses external database (Neon PostgreSQL)
- **Impact**: Requires network connectivity from cluster
- **Workaround**: Ensure Minikube can reach external database
- **Alternative**: Deploy PostgreSQL in cluster (not recommended for local dev)

#### 7. No Persistent Storage
- **Current State**: No PersistentVolumes configured
- **Impact**:
  - Application state lost on pod restart
  - Logs not persisted
  - No local file storage
- **Workaround**: Use external database for all persistent data
- **Future**: Add PVC for logs and temporary files

#### 8. Service Access
- **Current State**: Frontend uses NodePort (30000-32767 range)
- **Impact**: Must access via Minikube IP, not localhost
- **Workaround**: Use `kubectl port-forward` for localhost access
- **Alternative**: Use `minikube tunnel` for LoadBalancer support

### Security Limitations

#### 9. Secrets Management
- **Current State**: Manual secret creation from .env.k8s file
- **Impact**:
  - Secrets stored in cluster (base64 encoded, not encrypted)
  - No automatic rotation
  - Manual updates required
- **Workaround**: Use `kubectl create secret` carefully
- **Future**: Integrate with external secret manager (Vault, AWS Secrets Manager)

#### 10. No TLS/HTTPS
- **Current State**: HTTP only (no SSL certificates)
- **Impact**: Unencrypted traffic between browser and application
- **Acceptable**: For local development only
- **Future**: Add cert-manager and Ingress with TLS for production

#### 11. No Network Policies
- **Current State**: No NetworkPolicy resources defined
- **Impact**: All pods can communicate with all other pods
- **Acceptable**: For local development
- **Future**: Add NetworkPolicies to restrict pod-to-pod communication

### Monitoring & Observability Limitations

#### 12. No Built-in Monitoring
- **Current State**: No Prometheus, Grafana, or metrics collection
- **Impact**: Limited visibility into application performance
- **Workaround**: Use `kubectl top pods` and `kubectl logs`
- **Future**: Deploy monitoring stack (Prometheus Operator)

#### 13. No Distributed Tracing
- **Current State**: No Jaeger or OpenTelemetry integration
- **Impact**: Cannot trace requests across services
- **Workaround**: Use application logs
- **Future**: Add OpenTelemetry instrumentation

#### 14. No Centralized Logging
- **Current State**: Logs only accessible via `kubectl logs`
- **Impact**:
  - Logs lost when pods restart
  - No log aggregation
  - Difficult to search across pods
- **Workaround**: Use `kubectl logs -f` for real-time logs
- **Future**: Deploy EFK stack (Elasticsearch, Fluentd, Kibana)

### AI Agent Limitations

#### 15. AI Agents Optional
- **Current State**: Gordon, kubectl-ai, and Kagent not required
- **Impact**: Manual infrastructure creation and troubleshooting
- **Workaround**: All infrastructure pre-created and documented
- **Note**: AI agents enhance workflow but are not blocking

#### 16. No Automated Health Analysis
- **Current State**: Kagent not installed
- **Impact**: Manual health checks and optimization
- **Workaround**: Use `./scripts/health-check.sh` script
- **Future**: Install Kagent for AI-powered diagnostics

### Development Workflow Limitations

#### 17. Manual Image Rebuild
- **Current State**: Must manually rebuild and reload images
- **Impact**: Slower development iteration
- **Workaround**: Use `./scripts/build-images.sh` and `./scripts/load-images.sh`
- **Future**: Implement CI/CD pipeline with automated builds

#### 18. No Hot Reload
- **Current State**: Code changes require full rebuild and redeploy
- **Impact**: Slower development feedback loop
- **Workaround**: Use local development (npm run dev) for rapid iteration
- **Note**: Kubernetes deployment is for integration testing

#### 19. No Automated Testing
- **Current State**: No automated test execution in cluster
- **Impact**: Manual testing required after deployment
- **Workaround**: Run tests locally before deploying
- **Future**: Add test jobs to Helm chart

### Configuration Limitations

#### 20. Static Configuration
- **Current State**: ConfigMap and Secrets are static
- **Impact**: Changes require pod restart
- **Workaround**: Use `kubectl rollout restart deployment/<name>`
- **Future**: Implement dynamic configuration reloading

#### 21. No Feature Flags
- **Current State**: No feature flag system
- **Impact**: Cannot toggle features without redeployment
- **Workaround**: Use environment variables
- **Future**: Integrate feature flag service (LaunchDarkly, Unleash)

### Performance Limitations

#### 22. No CDN
- **Current State**: Frontend assets served directly from pods
- **Impact**: Slower asset loading, no edge caching
- **Acceptable**: For local development
- **Future**: Use CDN for production (Cloudflare, CloudFront)

#### 23. No Caching Layer
- **Current State**: No Redis or Memcached
- **Impact**: All requests hit database
- **Workaround**: Database query optimization
- **Future**: Add Redis for session and query caching

#### 24. Single Region
- **Current State**: Local deployment only
- **Impact**: No geographic distribution
- **Acceptable**: For local development
- **Future**: Multi-region deployment for production

### Documentation Limitations

#### 25. No Runbooks
- **Current State**: Limited operational procedures documented
- **Impact**: Unclear how to handle specific scenarios
- **Workaround**: Use TROUBLESHOOTING.md for common issues
- **Future**: Create comprehensive runbooks for operations

---

## Mitigation Strategies

### For Development
1. **Use Local Development First**: Run `npm run dev` and `python main.py` for rapid iteration
2. **Deploy to Kubernetes for Integration Testing**: Use Kubernetes to test full stack integration
3. **Automate Common Tasks**: Use provided scripts (`deploy.sh`, `health-check.sh`, `cleanup.sh`)

### For Production Readiness
1. **External Secret Management**: Integrate Vault or cloud provider secret manager
2. **Monitoring Stack**: Deploy Prometheus, Grafana, and alerting
3. **Ingress Controller**: Replace NodePort with Ingress + TLS
4. **CI/CD Pipeline**: Automate build, test, and deployment
5. **Database Migration**: Implement proper migration strategy
6. **Backup Strategy**: Implement automated backups for database and configurations

### For Performance
1. **Add Caching**: Deploy Redis for session and query caching
2. **CDN Integration**: Use CDN for static assets
3. **Database Optimization**: Add indexes, connection pooling
4. **Horizontal Scaling**: Increase replica counts for frontend

### For Security
1. **Network Policies**: Restrict pod-to-pod communication
2. **Pod Security Standards**: Enforce restricted PSS
3. **Image Scanning**: Scan images for vulnerabilities
4. **RBAC**: Implement proper role-based access control
5. **TLS Everywhere**: Enable TLS for all communication

---

## Next Steps

1. **Optimize Resources**: Run `kagent "optimize resource allocation"` after application runs for a while
2. **Monitor Performance**: Use `kubectl top pods` to track resource usage
3. **Scale Deployment**: Use `kubectl scale deployment/frontend --replicas=3` to test scaling
4. **Update Application**: Build new images, load into Minikube, and run `helm upgrade`
5. **Explore Kubernetes Dashboard**: Run `minikube dashboard` for web UI

---

## Additional Resources

- **Minikube Documentation**: https://minikube.sigs.k8s.io/docs/
- **Helm Documentation**: https://helm.sh/docs/
- **Kubernetes Documentation**: https://kubernetes.io/docs/
- **Docker Documentation**: https://docs.docker.com/

---

## Support

For issues or questions:
1. Check pod logs: `kubectl logs <pod-name>`
2. Describe pod: `kubectl describe pod <pod-name>`
3. Use Kagent: `kagent "why is the pod failing?"`
4. Review this quickstart guide
5. Consult project documentation in `/specs/001-k8s-aiops-deployment/`
