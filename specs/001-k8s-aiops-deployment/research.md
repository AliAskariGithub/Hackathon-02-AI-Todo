# Research: Local Kubernetes & AIOps Deployment

**Feature**: 001-k8s-aiops-deployment
**Date**: 2026-02-08
**Purpose**: Resolve technical unknowns and establish best practices for containerization and Kubernetes deployment

## Research Questions & Findings

### 1. Container Base Image Selection

**Question**: What are the optimal base images for Next.js and FastAPI containers?

**Research Findings**:
- **Frontend (Next.js)**: Node.js 20-alpine recommended
  - Alpine Linux provides minimal attack surface (~5MB base)
  - Node.js 20 LTS supported until April 2026
  - Official image: `node:20-alpine`
  - Multi-stage build: Use full node image for build, alpine for runtime

- **Backend (FastAPI)**: Python 3.11-slim recommended
  - Slim variant balances size (~45MB) vs compatibility
  - Python 3.11 provides performance improvements over 3.10
  - Official image: `python:3.11-slim`
  - Includes necessary system libraries for asyncpg and cryptography

**Decision**: Use `node:20-alpine` for frontend, `python:3.11-slim` for backend

**Rationale**: Official images, security updates, optimal size/compatibility balance

**Alternatives Considered**:
- `node:20-slim`: Larger (~70MB more), no significant benefit
- `python:3.11-alpine`: Compilation issues with asyncpg and bcrypt
- Distroless images: Too restrictive for debugging in local development

---

### 2. Image Pull Policy for Minikube

**Question**: How should Kubernetes pull container images in a local Minikube environment?

**Research Findings**:
- **IfNotPresent**: Pulls image only if not already present locally
  - Best for local development with `minikube image load`
  - Avoids unnecessary registry pulls
  - Faster deployment iterations

- **Always**: Pulls image on every pod creation
  - Useful for testing registry integration
  - Slower, requires registry setup
  - Not suitable for local-only images

- **Never**: Only uses local images
  - Fails if image not present
  - Too restrictive for dependencies

**Decision**: Use `imagePullPolicy: IfNotPresent` for all deployments

**Rationale**: Optimal for local development workflow where images are loaded into Minikube manually

**Alternatives Considered**:
- `Always`: Requires container registry setup (out of scope)
- `Never`: Too restrictive, fails on missing images

---

### 3. Kubernetes Service Types for Local Access

**Question**: How should frontend and backend services be exposed in Minikube?

**Research Findings**:
- **Frontend Service**:
  - **NodePort**: Exposes service on static port (30000-32767) on each node
    - Simple, no additional setup required
    - Access via `minikube ip:nodePort`
    - Standard for local development
  - **LoadBalancer**: Requires `minikube tunnel` to allocate external IP
    - More production-like
    - Requires background tunnel process
    - Access via `localhost:port`

- **Backend Service**:
  - **ClusterIP**: Internal-only service (default)
    - Not accessible from outside cluster
    - Frontend accesses via Kubernetes DNS
    - Secure, follows microservices pattern

**Decision**:
- Frontend: NodePort (with LoadBalancer as optional alternative via minikube tunnel)
- Backend: ClusterIP (internal only)

**Rationale**: NodePort is simplest for local access; ClusterIP enforces proper service boundaries

**Alternatives Considered**:
- Frontend LoadBalancer: Requires tunnel, adds complexity
- Backend NodePort: Exposes backend unnecessarily, violates architecture boundaries

---

### 4. Resource Allocation for Local Development

**Question**: What CPU and memory limits are appropriate for local Minikube deployment?

**Research Findings**:
- **Minikube Minimum**: 4GB RAM, 2 CPU cores
- **Frontend (Next.js)**:
  - Build: ~1GB RAM, 1 CPU (temporary)
  - Runtime: ~256-512MB RAM, 0.25-0.5 CPU
  - Recommendation: Request 256Mi/0.25 CPU, Limit 512Mi/0.5 CPU

- **Backend (FastAPI)**:
  - Runtime: ~512MB-1GB RAM, 0.5-1 CPU
  - Database connections: ~100MB overhead
  - Recommendation: Request 512Mi/0.5 CPU, Limit 1Gi/1 CPU

**Decision**:
- Frontend: requests 256Mi/0.25 CPU, limits 512Mi/0.5 CPU
- Backend: requests 512Mi/0.5 CPU, limits 1Gi/1 CPU

**Rationale**: Conservative limits for local development, prevents resource exhaustion

**Alternatives Considered**:
- Higher limits: Unnecessary for local dev, wastes resources
- No limits: Risk of resource exhaustion, poor scheduling

---

### 5. Health Check Strategy

**Question**: How should liveness and readiness probes be configured?

**Research Findings**:
- **Liveness Probe**: Determines if container should be restarted
  - Endpoint: `/health` (simple health check)
  - Initial delay: 30s (allow startup time)
  - Period: 10s (check every 10 seconds)
  - Failure threshold: 3 (restart after 3 failures)

- **Readiness Probe**: Determines if pod should receive traffic
  - Endpoint: `/ready` (checks dependencies like DB)
  - Initial delay: 10s (faster than liveness)
  - Period: 5s (more frequent checks)
  - Failure threshold: 3 (remove from service after 3 failures)

**Decision**:
- Implement both liveness (`/health`) and readiness (`/ready`) probes
- HTTP GET probes on standard endpoints
- Conservative initial delays for local development

**Rationale**: Enables automatic recovery and proper traffic routing

**Alternatives Considered**:
- TCP probes: Less informative than HTTP
- Exec probes: More complex, harder to debug
- Single probe: Cannot distinguish restart vs traffic routing

---

### 6. AI Model for Agents SDK (In-Cluster)

**Question**: Which AI model should be used for the Agents SDK logic within the Kubernetes cluster?

**Research Findings**:
- **OpenRouter Models**:
  - `openai/gpt-oss-120b:free`: Free tier, 120B parameters
    - Good balance of capability and cost
    - Suitable for task management operations
    - No rate limits on free tier
  - `anthropic/claude-3.5-sonnet`: Higher quality, paid
    - Better reasoning, more expensive
    - Overkill for simple task operations

**Decision**: Use `openai/gpt-oss-120b:free` via OpenRouter for in-cluster Agents SDK

**Rationale**: Free tier, sufficient capability for task operations, no rate limits

**Alternatives Considered**:
- Claude 3.5 Sonnet: Better quality but paid, unnecessary for task CRUD
- Local models: Requires additional infrastructure, out of scope

---

### 7. Docker Multi-Stage Build Strategy

**Question**: How should multi-stage builds be structured for optimal image size and security?

**Research Findings**:
- **Frontend (Next.js)**:
  - Stage 1 (builder): Install all dependencies, build Next.js app
  - Stage 2 (runtime): Copy built artifacts, install production dependencies only
  - Optimization: Use `.dockerignore` to exclude node_modules, .next, .env

- **Backend (FastAPI)**:
  - Stage 1 (builder): Install build dependencies (gcc, etc.)
  - Stage 2 (runtime): Copy installed packages, exclude build tools
  - Optimization: Use pip cache, install only production dependencies

**Decision**: Implement multi-stage builds for both frontend and backend

**Rationale**: Constitutional requirement, reduces image size by 50-70%, improves security

**Alternatives Considered**:
- Single-stage builds: Simpler but larger images, includes build tools
- Three-stage builds: Unnecessary complexity for this use case

---

### 8. Helm Chart Structure

**Question**: Should we use a single chart or multiple charts for frontend and backend?

**Research Findings**:
- **Umbrella Chart**: Single chart with subcharts for each service
  - Pros: Single deployment command, shared values, version coordination
  - Cons: More complex structure, harder to deploy services independently

- **Separate Charts**: Individual charts for frontend and backend
  - Pros: Independent deployment, simpler structure
  - Cons: Multiple helm install commands, value duplication

**Decision**: Use umbrella chart with templates for both services

**Rationale**: Simpler for local development, single deployment command, shared configuration

**Alternatives Considered**:
- Separate charts: More complex deployment workflow for local dev
- Subcharts: Unnecessary abstraction for 2 services

---

### 9. Secret Management Strategy

**Question**: How should secrets be managed in Kubernetes for local development?

**Research Findings**:
- **Kubernetes Secrets**: Native secret storage
  - Base64 encoded (not encrypted at rest in Minikube)
  - Mounted as environment variables or files
  - Suitable for local development

- **External Secret Managers**: Vault, AWS Secrets Manager
  - Production-grade encryption
  - Out of scope for local Minikube

- **Helm Values**: Secrets in values.yaml
  - Not recommended (secrets in version control)
  - Use values.yaml for non-sensitive config only

**Decision**:
- Use Kubernetes Secrets for sensitive data (DATABASE_URL, JWT_SECRET, etc.)
- Provide secrets.yaml template (not committed)
- Document secret creation in quickstart.md

**Rationale**: Native Kubernetes approach, suitable for local development

**Alternatives Considered**:
- External secret managers: Overkill for local dev
- ConfigMaps: Not designed for sensitive data
- Helm values: Security risk if committed

---

### 10. Deployment Automation Strategy

**Question**: How should the build-to-deploy workflow be automated?

**Research Findings**:
- **Shell Script Approach**:
  - Single `deploy.sh` script orchestrates entire workflow
  - Steps: Build images → Load into Minikube → Helm install/upgrade
  - Error handling: Exit on any failure, preserve previous deployment

- **Makefile Approach**:
  - Separate targets for build, load, deploy
  - More granular control
  - Requires make installation

**Decision**: Use shell script (`deploy.sh`) for automation

**Rationale**: Simpler, no additional dependencies, suitable for local development

**Alternatives Considered**:
- Makefile: More complex, requires make
- CI/CD pipeline: Out of scope for local development

---

## Summary of Key Decisions

| Decision Area | Choice | Rationale |
|---------------|--------|-----------|
| Frontend Base Image | node:20-alpine | Official, minimal, secure |
| Backend Base Image | python:3.11-slim | Compatible, optimal size |
| Image Pull Policy | IfNotPresent | Local development workflow |
| Frontend Service | NodePort | Simple local access |
| Backend Service | ClusterIP | Internal only, secure |
| Frontend Resources | 256Mi/0.25 CPU → 512Mi/0.5 CPU | Conservative local limits |
| Backend Resources | 512Mi/0.5 CPU → 1Gi/1 CPU | Conservative local limits |
| Health Checks | HTTP /health and /ready | Standard Kubernetes pattern |
| AI Model | openai/gpt-oss-120b:free | Free, sufficient capability |
| Build Strategy | Multi-stage | Constitutional requirement |
| Chart Structure | Umbrella chart | Single deployment command |
| Secret Management | Kubernetes Secrets | Native, suitable for local |
| Automation | Shell script (deploy.sh) | Simple, no dependencies |

## Technology Stack Validation

**Confirmed Technologies**:
- ✅ Docker Desktop 4.53+ (Gordon compatible)
- ✅ Minikube (Kubernetes 1.28+)
- ✅ Helm 3+
- ✅ Node.js 20 (Next.js 16.1.2)
- ✅ Python 3.11+ (FastAPI)
- ✅ Neon PostgreSQL (external)
- ✅ Gordon (Docker AI)
- ✅ kubectl-ai
- ✅ Kagent

**No Changes Required**: All technologies align with constitutional requirements and project constraints.
