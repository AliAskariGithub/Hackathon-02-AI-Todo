# kubectl-ai Agent Contract

**Agent**: kubectl-ai
**Role**: Kubernetes Deployer
**Responsibility**: Generate Kubernetes manifests, execute deployments, and manage cluster resources

## Agent Capabilities

kubectl-ai is a specialized AI agent for Kubernetes operations with the following capabilities:
- Generate Kubernetes manifest templates (Deployments, Services, ConfigMaps, Secrets)
- Execute kubectl commands with natural language
- Diagnose pod failures and deployment issues
- Scale deployments and manage replicas
- Provide Kubernetes best practices recommendations

## Invocation Patterns

### 1. Generate Deployment Manifest

**Command**:
```bash
kubectl-ai "generate a deployment with 2 replicas for the frontend image ai-todo-frontend:v1.0.0"
```

**Context Required**:
- Image name and tag
- Desired replica count
- Resource limits (CPU, memory)
- Port configuration
- Environment variables
- Health check endpoints

**Expected Output**:
- Kubernetes Deployment YAML with:
  - Proper labels and selectors
  - Resource requests and limits
  - Liveness and readiness probes
  - Non-root security context
  - Rolling update strategy

**Validation**:
- Manifest applies successfully (`kubectl apply -f`)
- Pods reach Running state
- Health checks pass
- Constitutional requirements met

---

### 2. Generate Service Manifest

**Command**:
```bash
kubectl-ai "create a NodePort service for the frontend deployment exposing port 3000"
```

**Context Required**:
- Service type (NodePort, ClusterIP, LoadBalancer)
- Target deployment/pod selector
- Port mappings (port, targetPort, nodePort)
- Service name

**Expected Output**:
- Kubernetes Service YAML with:
  - Proper selector matching deployment labels
  - Port configuration
  - Service type specification
  - Standard labels

**Validation**:
- Service created successfully
- Endpoints populated with pod IPs
- Service accessible via DNS
- External access works (for NodePort/LoadBalancer)

---

### 3. Diagnose Pod Failures

**Command**:
```bash
kubectl-ai "check why the pods are failing"
```

**Context Required**:
- Current kubectl context (Minikube)
- Namespace (default or specified)
- Access to cluster state

**Expected Output**:
- Analysis of pod failures:
  - CrashLoopBackOff causes
  - ImagePullBackOff issues
  - Resource constraint problems
  - Configuration errors
- Actionable recommendations for fixes

**Validation**:
- Root cause identified correctly
- Recommendations are specific and actionable
- Fixes resolve the issue when applied

---

### 4. Scale Deployment

**Command**:
```bash
kubectl-ai "scale the frontend deployment to 3 replicas"
```

**Context Required**:
- Deployment name
- Target replica count
- Current cluster capacity

**Expected Output**:
- Scaling command executed
- Confirmation of new replica count
- Status of new pods

**Validation**:
- Deployment scaled successfully
- New pods reach Running state
- Service load balances across all replicas

---

### 5. Generate ConfigMap

**Command**:
```bash
kubectl-ai "create a ConfigMap with LOG_LEVEL=info and DEBUG=true"
```

**Context Required**:
- ConfigMap name
- Key-value pairs for configuration
- Namespace

**Expected Output**:
- Kubernetes ConfigMap YAML with:
  - Proper naming
  - All key-value pairs
  - Standard labels

**Validation**:
- ConfigMap created successfully
- Referenced by deployments correctly
- Values accessible in pods

---

## Input Requirements

### Deployment Manifest Generation

**Required Information**:
- **Image**: Full image name with tag (e.g., ai-todo-frontend:v1.0.0)
- **Replicas**: Number of pod replicas (1-2 for local dev)
- **Resources**:
  - Frontend: requests 256Mi/0.25 CPU, limits 512Mi/0.5 CPU
  - Backend: requests 512Mi/0.5 CPU, limits 1Gi/1 CPU
- **Ports**: Container ports to expose
- **Environment**: ConfigMap and Secret references
- **Health Checks**:
  - Liveness: /health endpoint, 30s initial delay
  - Readiness: /ready endpoint, 10s initial delay

**Expected Deployment Structure**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  labels:
    app.kubernetes.io/name: frontend
    app.kubernetes.io/instance: ai-todo
    app.kubernetes.io/version: v1.0.0
    app.kubernetes.io/component: frontend
    app.kubernetes.io/part-of: ai-todo
    app.kubernetes.io/managed-by: Helm
spec:
  replicas: 2
  selector:
    matchLabels:
      app.kubernetes.io/name: frontend
      app.kubernetes.io/instance: ai-todo
  template:
    metadata:
      labels:
        app.kubernetes.io/name: frontend
        app.kubernetes.io/instance: ai-todo
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1001
      containers:
      - name: frontend
        image: ai-todo-frontend:v1.0.0
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 3000
          name: http
        envFrom:
        - configMapRef:
            name: ai-todo-config
        - secretRef:
            name: ai-todo-secrets
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /ready
            port: 3000
          initialDelaySeconds: 10
          periodSeconds: 5
          failureThreshold: 3
```

---

### Service Manifest Generation

**Required Information**:
- **Service Name**: frontend-service, backend-service
- **Service Type**:
  - Frontend: NodePort (external access)
  - Backend: ClusterIP (internal only)
- **Selector**: Labels matching target pods
- **Ports**:
  - Frontend: port 80 → targetPort 3000
  - Backend: port 8001 → targetPort 8001

**Expected Service Structure**:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: frontend-service
  labels:
    app.kubernetes.io/name: frontend
    app.kubernetes.io/instance: ai-todo
spec:
  type: NodePort
  selector:
    app.kubernetes.io/name: frontend
    app.kubernetes.io/instance: ai-todo
  ports:
  - port: 80
    targetPort: 3000
    protocol: TCP
    name: http
```

---

## Output Specifications

### Manifest Requirements

**Constitutional Compliance**:
- ✅ All required labels (app.kubernetes.io/*)
- ✅ Resource requests and limits defined
- ✅ Health checks configured (liveness + readiness)
- ✅ Non-root security context
- ✅ Rolling update strategy
- ✅ Image pull policy: IfNotPresent

**Best Practices**:
- Proper label selectors
- Meaningful resource names
- Standard port names (http, https)
- Appropriate probe timings
- Reasonable replica counts

---

## Error Handling

### Common Issues and Resolutions

**Issue**: ImagePullBackOff
**Cause**: Image not present in Minikube
**Resolution**: Load image with `minikube image load <image-name>`

**Issue**: CrashLoopBackOff
**Cause**: Application startup failure, missing environment variables
**Resolution**: Check logs with `kubectl logs`, verify ConfigMap/Secret

**Issue**: Pods not ready
**Cause**: Readiness probe failing
**Resolution**: Verify health endpoint is accessible, adjust probe timing

**Issue**: Service has no endpoints
**Cause**: Selector doesn't match pod labels
**Resolution**: Verify label consistency between Service and Deployment

---

## Integration with Workflow

### Step 1: Generate Kubernetes Manifests
```bash
# Generate frontend deployment
kubectl-ai "generate a deployment for ai-todo-frontend:v1.0.0 with 2 replicas, 256Mi/0.25 CPU requests, 512Mi/0.5 CPU limits, health checks on /health and /ready"

# Generate backend deployment
kubectl-ai "generate a deployment for ai-todo-backend:v1.0.0 with 1 replica, 512Mi/0.5 CPU requests, 1Gi/1 CPU limits, health checks on /health and /ready"

# Generate frontend service
kubectl-ai "create a NodePort service for frontend deployment exposing port 3000"

# Generate backend service
kubectl-ai "create a ClusterIP service for backend deployment exposing port 8001"
```

### Step 2: Apply Manifests (via Helm)
```bash
# Manifests integrated into Helm chart templates
helm install ai-todo ./charts/ai-todo
```

### Step 3: Diagnose Issues
```bash
# If pods fail to start
kubectl-ai "check why the pods are failing"

# Get specific pod logs
kubectl-ai "show me the logs for the frontend pod"
```

### Step 4: Scale if Needed
```bash
kubectl-ai "scale the frontend deployment to 3 replicas"
```

---

## Success Criteria

**Manifest Generation**:
- ✅ Valid Kubernetes YAML syntax
- ✅ All constitutional requirements met
- ✅ Manifests apply without errors
- ✅ Pods reach Running state within 2 minutes

**Deployment Success**:
- ✅ All pods Running and Ready
- ✅ Health checks passing
- ✅ Services have endpoints
- ✅ Application accessible via service

**Diagnostics**:
- ✅ Root cause identified for failures
- ✅ Recommendations resolve issues
- ✅ Clear, actionable guidance provided

---

## Agent Limitations

**What kubectl-ai CAN Do**:
- Generate Kubernetes manifests
- Execute kubectl commands
- Diagnose deployment issues
- Scale deployments
- Provide Kubernetes best practices

**What kubectl-ai CANNOT Do**:
- Generate Dockerfiles (use Gordon)
- Optimize container images (use Gordon)
- Perform cluster health analysis (use Kagent)
- Create Helm charts (use Claude Code)
- Modify application source code

---

## Review and Approval Process

**Before Deployment**:
1. kubectl-ai generates Kubernetes manifests
2. Manifests integrated into Helm chart templates
3. Technical Lead reviews generated manifests
4. Constitutional compliance verified
5. Test deployment to Minikube
6. Technical Lead approves for use
7. Manifests committed to repository

**Constitutional Safeguard**: All kubectl-ai generated manifests must be reviewed by Technical Lead before deployment to Minikube cluster.
