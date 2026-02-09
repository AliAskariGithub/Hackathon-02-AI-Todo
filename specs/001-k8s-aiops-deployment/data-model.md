# Data Model: Infrastructure Entities

**Feature**: 001-k8s-aiops-deployment
**Date**: 2026-02-08
**Purpose**: Define infrastructure entities and their relationships for Kubernetes deployment

## Overview

This document defines the infrastructure entities (not application data models) required for containerizing and deploying the AI Todo application to Kubernetes. These entities represent the cloud-native infrastructure components that will be created and managed.

---

## Entity Definitions

### 1. Container Image

**Description**: Packaged application artifact containing code, dependencies, and runtime environment.

**Attributes**:
- `name`: Image name (e.g., "ai-todo-frontend", "ai-todo-backend")
- `tag`: Semantic version + git SHA (e.g., "v1.0.0-abc1234")
- `registry`: Image registry location (local for Minikube)
- `size`: Image size in MB (target: frontend <500MB, backend <300MB)
- `baseImage`: Parent image (node:20-alpine, python:3.11-slim)
- `buildStage`: Multi-stage build configuration (builder, runtime)
- `securityContext`: User ID, non-root execution settings
- `layers`: Number of image layers (minimize for efficiency)

**Relationships**:
- Built FROM base image
- Referenced BY Kubernetes Deployment
- Loaded INTO Minikube image cache

**Validation Rules**:
- Tag MUST follow semver format (no "latest")
- Size MUST be under constitutional limits
- MUST run as non-root user
- MUST use multi-stage builds

**State Transitions**:
1. **Building**: Docker build in progress
2. **Built**: Image exists in local Docker cache
3. **Loaded**: Image loaded into Minikube
4. **Running**: Container instantiated from image

---

### 2. Dockerfile

**Description**: Build instructions for creating container images.

**Attributes**:
- `path`: File location (frontend/Dockerfile, backend/Dockerfile)
- `stages`: Build stages (builder, runtime)
- `baseImage`: Starting image for each stage
- `workdir`: Working directory inside container
- `user`: Non-root user for execution
- `port`: Exposed port (3000 for frontend, 8001 for backend)
- `entrypoint`: Container startup command
- `healthcheck`: Docker-level health check (optional)

**Relationships**:
- Generates Container Image
- References base images FROM Docker Hub
- Excludes files via .dockerignore

**Validation Rules**:
- MUST use multi-stage builds
- MUST create and switch to non-root user
- MUST expose only necessary ports
- MUST use COPY (not ADD) for application files

**Generation**:
- Created BY Gordon (Docker AI agent)
- Audited BY Gordon for security vulnerabilities
- Reviewed BY Technical Lead before use

---

### 3. Helm Chart

**Description**: Kubernetes package definition containing templates, values, and metadata.

**Attributes**:
- `name`: Chart name ("ai-todo")
- `version`: Chart version (semver)
- `appVersion`: Application version being deployed
- `description`: Human-readable description
- `type`: Chart type (application)
- `dependencies`: Subchart dependencies (if any)

**Relationships**:
- Contains Kubernetes manifest templates
- References Container Images
- Configured BY values.yaml
- Installed INTO Kubernetes cluster

**Validation Rules**:
- Chart version MUST follow semver
- MUST include all required labels
- MUST define resource limits
- MUST include health check probes

**Structure**:
```
charts/ai-todo/
├── Chart.yaml          # Metadata
├── values.yaml         # Configuration
├── templates/          # Kubernetes manifests
│   ├── _helpers.tpl
│   ├── frontend-deployment.yaml
│   ├── frontend-service.yaml
│   ├── backend-deployment.yaml
│   ├── backend-service.yaml
│   ├── configmap.yaml
│   └── secrets.yaml
└── charts/             # Subcharts (if needed)
```

---

### 4. Kubernetes Deployment

**Description**: Declarative specification of desired pod state and replica management.

**Attributes**:
- `name`: Deployment name (frontend, backend)
- `namespace`: Kubernetes namespace (default)
- `replicas`: Desired number of pod replicas (1-2 for local)
- `selector`: Label selector for pods
- `template`: Pod template specification
- `strategy`: Update strategy (RollingUpdate)
- `revisionHistoryLimit`: Number of old ReplicaSets to retain (3)

**Pod Template Attributes**:
- `image`: Container image reference
- `imagePullPolicy`: IfNotPresent
- `ports`: Container ports
- `env`: Environment variables
- `envFrom`: ConfigMap/Secret references
- `resources`: CPU/memory requests and limits
- `livenessProbe`: Health check for restart decisions
- `readinessProbe`: Health check for traffic routing
- `securityContext`: Non-root user, capabilities

**Relationships**:
- Manages ReplicaSet
- Creates Pods from template
- References Container Images
- Uses ConfigMaps and Secrets
- Exposed BY Service

**Validation Rules**:
- MUST define resource requests and limits
- MUST include liveness and readiness probes
- MUST use non-root security context
- MUST use RollingUpdate strategy

**State Transitions**:
1. **Pending**: Deployment created, pods not yet scheduled
2. **Progressing**: Pods being created/updated
3. **Available**: Desired replicas are running and ready
4. **Failed**: Deployment cannot progress (image pull errors, etc.)

---

### 5. Kubernetes Service

**Description**: Network abstraction providing stable endpoints for pod communication.

**Attributes**:
- `name`: Service name (frontend-service, backend-service)
- `type`: Service type (NodePort, ClusterIP, LoadBalancer)
- `selector`: Label selector for target pods
- `ports`: Port mappings (port, targetPort, nodePort)
- `sessionAffinity`: Session stickiness (None, ClientIP)

**Service Types**:
- **Frontend Service**: NodePort (external access)
  - Port: 80 (service port)
  - TargetPort: 3000 (container port)
  - NodePort: 30080 (node port, auto-assigned)

- **Backend Service**: ClusterIP (internal only)
  - Port: 8001 (service port)
  - TargetPort: 8001 (container port)
  - DNS: backend-service.default.svc.cluster.local

**Relationships**:
- Routes traffic TO Pods (via selector)
- Provides DNS name for service discovery
- Exposed externally (NodePort) or internally (ClusterIP)

**Validation Rules**:
- MUST match pod labels with selector
- MUST define port mappings
- Backend MUST use ClusterIP (internal only)
- Frontend MAY use NodePort or LoadBalancer

---

### 6. Kubernetes Pod

**Description**: Smallest deployable unit containing one or more containers.

**Attributes**:
- `name`: Pod name (generated with random suffix)
- `namespace`: Kubernetes namespace
- `labels`: Key-value labels for selection
- `annotations`: Metadata annotations
- `phase`: Pod lifecycle phase (Pending, Running, Succeeded, Failed, Unknown)
- `conditions`: Pod conditions (PodScheduled, Initialized, ContainersReady, Ready)
- `containerStatuses`: Status of each container

**Relationships**:
- Created BY Deployment
- Runs Container Image
- Receives traffic FROM Service
- Accesses ConfigMaps and Secrets

**Validation Rules**:
- MUST include required labels
- MUST pass readiness probe before receiving traffic
- MUST restart on liveness probe failure
- MUST respect resource limits

**State Transitions**:
1. **Pending**: Pod accepted, containers not yet created
2. **Running**: Pod bound to node, containers running
3. **Succeeded**: All containers terminated successfully
4. **Failed**: All containers terminated, at least one failed
5. **Unknown**: Pod state cannot be determined

---

### 7. ConfigMap

**Description**: Non-sensitive configuration data stored as key-value pairs.

**Attributes**:
- `name`: ConfigMap name (ai-todo-config)
- `namespace`: Kubernetes namespace
- `data`: Key-value configuration pairs
- `immutable`: Whether ConfigMap can be modified (false for local dev)

**Configuration Data**:
- `LOG_LEVEL`: Logging verbosity (info, debug)
- `DEBUG`: Debug mode flag (true/false)
- `ALLOWED_ORIGINS`: CORS allowed origins
- `ENABLE_RATE_LIMITING`: Rate limiting flag
- `RATE_LIMIT_PER_MINUTE`: Rate limit threshold

**Relationships**:
- Referenced BY Deployment (envFrom)
- Mounted AS environment variables or files

**Validation Rules**:
- MUST NOT contain sensitive data
- MUST be referenced by at least one Deployment
- Keys MUST follow naming conventions (UPPER_SNAKE_CASE)

---

### 8. Secret

**Description**: Sensitive configuration data stored with base64 encoding.

**Attributes**:
- `name`: Secret name (ai-todo-secrets)
- `namespace`: Kubernetes namespace
- `type`: Secret type (Opaque)
- `data`: Base64-encoded key-value pairs
- `immutable`: Whether Secret can be modified (false for local dev)

**Secret Data**:
- `DATABASE_URL`: PostgreSQL connection string
- `BETTER_AUTH_SECRET`: Authentication secret key
- `JWT_SECRET`: JWT signing key
- `GROQ_API_KEY`: GROQ API key for AI features

**Relationships**:
- Referenced BY Deployment (envFrom)
- Mounted AS environment variables or files

**Validation Rules**:
- MUST be base64 encoded
- MUST NOT be committed to version control
- MUST be created before Deployment
- MUST be referenced by at least one Deployment

**Security Notes**:
- Secrets are base64 encoded, NOT encrypted at rest in Minikube
- Suitable for local development only
- Production requires external secret manager (out of scope)

---

### 9. Health Check Probe

**Description**: Configuration for monitoring pod health and readiness.

**Attributes**:
- `type`: Probe type (liveness, readiness)
- `handler`: Probe handler (httpGet, tcpSocket, exec)
- `path`: HTTP path for httpGet probes
- `port`: Port to probe
- `initialDelaySeconds`: Delay before first probe
- `periodSeconds`: Probe frequency
- `timeoutSeconds`: Probe timeout
- `successThreshold`: Consecutive successes required
- `failureThreshold`: Consecutive failures before action

**Probe Configurations**:

**Liveness Probe** (restart unhealthy containers):
- Path: `/health`
- Initial Delay: 30s
- Period: 10s
- Failure Threshold: 3

**Readiness Probe** (route traffic to ready pods):
- Path: `/ready`
- Initial Delay: 10s
- Period: 5s
- Failure Threshold: 3

**Relationships**:
- Configured IN Deployment pod template
- Executed BY kubelet on each node
- Affects Pod status and Service routing

**Validation Rules**:
- MUST define both liveness and readiness probes
- Initial delay MUST allow for startup time
- Failure threshold MUST be reasonable (3-5)

---

### 10. Resource Quota

**Description**: CPU and memory limits and requests for containers.

**Attributes**:
- `requests`: Minimum guaranteed resources
  - `cpu`: CPU cores (e.g., "250m" = 0.25 cores)
  - `memory`: RAM (e.g., "256Mi" = 256 megabytes)
- `limits`: Maximum allowed resources
  - `cpu`: CPU cores (e.g., "500m" = 0.5 cores)
  - `memory`: RAM (e.g., "512Mi" = 512 megabytes)

**Resource Allocations**:

**Frontend**:
- Requests: 256Mi memory, 250m CPU
- Limits: 512Mi memory, 500m CPU

**Backend**:
- Requests: 512Mi memory, 500m CPU
- Limits: 1Gi memory, 1000m CPU

**Relationships**:
- Defined IN Deployment pod template
- Enforced BY Kubernetes scheduler and kubelet
- Affects pod scheduling and eviction

**Validation Rules**:
- Requests MUST be less than or equal to limits
- MUST be defined for all containers
- MUST fit within Minikube cluster capacity

---

## Entity Relationship Diagram

```
┌─────────────────┐
│  Dockerfile     │──generates──▶│ Container Image │
└─────────────────┘               └─────────────────┘
                                          │
                                          │ referenced by
                                          ▼
┌─────────────────┐               ┌─────────────────┐
│  Helm Chart     │──contains────▶│  Deployment     │──creates──▶│ Pod │
└─────────────────┘               └─────────────────┘             └─────┘
        │                                 │                          │
        │ configured by                   │ uses                     │ runs
        ▼                                 ▼                          ▼
┌─────────────────┐               ┌─────────────────┐       ┌─────────────┐
│  values.yaml    │               │ ConfigMap       │       │ Container   │
└─────────────────┘               │ Secret          │       └─────────────┘
                                  └─────────────────┘
                                          │
                                          │ mounted as env
                                          ▼
                                  ┌─────────────────┐
                                  │  Service        │──routes──▶│ Pod │
                                  └─────────────────┘            └─────┘
```

---

## Summary

This data model defines 10 infrastructure entities required for Kubernetes deployment:

1. **Container Image**: Packaged application artifact
2. **Dockerfile**: Build instructions
3. **Helm Chart**: Kubernetes package
4. **Deployment**: Pod replica management
5. **Service**: Network abstraction
6. **Pod**: Smallest deployable unit
7. **ConfigMap**: Non-sensitive configuration
8. **Secret**: Sensitive configuration
9. **Health Check Probe**: Health monitoring
10. **Resource Quota**: CPU/memory limits

All entities follow constitutional requirements for cloud-native deployment with proper security, observability, and resource management.
