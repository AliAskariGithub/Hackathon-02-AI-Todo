# Gordon (Docker AI) Agent Contract

**Agent**: Gordon (Docker AI)
**Role**: Container Architect
**Responsibility**: Generate, audit, and optimize Dockerfiles and docker-compose configurations

## Agent Capabilities

Gordon is a specialized AI agent for Docker containerization with the following capabilities:
- Generate production-ready Dockerfiles with multi-stage builds
- Audit existing Dockerfiles for security vulnerabilities
- Optimize container images for size and performance
- Create docker-compose configurations for local testing
- Provide best practices recommendations

## Invocation Patterns

### 1. Generate Dockerfile

**Command**:
```bash
docker ai "Create a multi-stage Dockerfile for my Next.js frontend application"
```

**Context Required**:
- Application type (Next.js, FastAPI, etc.)
- Base directory containing source code
- Build requirements (dependencies, build commands)
- Runtime requirements (ports, environment variables)

**Expected Output**:
- Multi-stage Dockerfile with builder and runtime stages
- Non-root user configuration
- Optimized layer caching
- Security best practices applied

**Validation**:
- Dockerfile builds successfully without errors
- Image size meets constitutional limits (<500MB frontend, <300MB backend)
- Runs as non-root user
- Includes proper health check configuration

---

### 2. Audit Dockerfile Security

**Command**:
```bash
docker ai "rate my Dockerfile"
```

**Context Required**:
- Path to Dockerfile to audit
- Current directory should contain the Dockerfile

**Expected Output**:
- Security vulnerability assessment
- Best practices compliance check
- Recommendations for improvements
- Risk rating (low, medium, high)

**Validation**:
- No critical or high-severity vulnerabilities
- Passes constitutional security requirements
- Recommendations are actionable

---

### 3. Generate docker-compose Configuration

**Command**:
```bash
docker ai "Create a docker-compose.yml for local testing with frontend and backend services"
```

**Context Required**:
- Service definitions (frontend, backend)
- Port mappings
- Environment variables
- Network configuration
- Volume mounts (if needed)

**Expected Output**:
- docker-compose.yml with service definitions
- Proper networking between services
- Environment variable configuration
- Volume mounts for development

**Validation**:
- Services start successfully with `docker-compose up`
- Frontend can communicate with backend
- Environment variables are properly passed
- Logs are accessible via `docker-compose logs`

---

### 4. Optimize Container Image

**Command**:
```bash
docker ai "optimize my Dockerfile to reduce image size"
```

**Context Required**:
- Existing Dockerfile
- Current image size
- Target size reduction goals

**Expected Output**:
- Optimized Dockerfile with size improvements
- Explanation of optimization techniques applied
- Estimated size reduction

**Validation**:
- Image size reduced by at least 20%
- Application functionality unchanged
- Build time not significantly increased

---

## Input Requirements

### Frontend (Next.js) Dockerfile Generation

**Required Information**:
- Base image: node:20-alpine
- Build command: `npm run build`
- Start command: `npm start`
- Port: 3000
- Environment variables: NEXT_PUBLIC_API_BASE_URL, NEXT_PUBLIC_SITE_URL
- Dependencies: package.json, package-lock.json

**Expected Dockerfile Structure**:
```dockerfile
# Stage 1: Builder
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: Runtime
FROM node:20-alpine AS runtime
WORKDIR /app
RUN addgroup -g 1001 -S appgroup && adduser -u 1001 -S appuser -G appgroup
COPY --from=builder --chown=appuser:appgroup /app/.next ./.next
COPY --from=builder --chown=appuser:appgroup /app/node_modules ./node_modules
COPY --from=builder --chown=appuser:appgroup /app/package.json ./package.json
COPY --from=builder --chown=appuser:appgroup /app/public ./public
USER appuser
EXPOSE 3000
CMD ["npm", "start"]
```

---

### Backend (FastAPI) Dockerfile Generation

**Required Information**:
- Base image: python:3.11-slim
- Dependencies: requirements.txt
- Start command: `uvicorn main:app --host 0.0.0.0 --port 8001`
- Port: 8001
- Environment variables: DATABASE_URL, JWT_SECRET, GROQ_API_KEY

**Expected Dockerfile Structure**:
```dockerfile
# Stage 1: Builder
FROM python:3.11-slim AS builder
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim AS runtime
WORKDIR /app
RUN useradd -m -u 1001 appuser
COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local
COPY --chown=appuser:appuser . .
USER appuser
ENV PATH=/home/appuser/.local/bin:$PATH
EXPOSE 8001
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
```

---

## Output Specifications

### Dockerfile Requirements

**Constitutional Compliance**:
- ✅ Multi-stage builds (builder + runtime)
- ✅ Non-root user execution
- ✅ Official base images only
- ✅ Minimal layers (combine RUN commands where possible)
- ✅ No hardcoded secrets
- ✅ Proper .dockerignore usage

**Security Requirements**:
- No root user in final stage
- No unnecessary packages installed
- Secrets passed via environment variables (not baked in)
- Base images from official sources
- Regular security updates applied

**Performance Requirements**:
- Image size under constitutional limits
- Build cache optimization
- Layer ordering for cache efficiency
- Minimal runtime dependencies

---

## Error Handling

### Common Issues and Resolutions

**Issue**: "Cannot find module" errors during build
**Resolution**: Ensure all dependencies are copied before build step

**Issue**: Permission denied errors
**Resolution**: Verify non-root user has proper ownership of files

**Issue**: Image size exceeds limits
**Resolution**: Use alpine base images, remove build dependencies in runtime stage

**Issue**: Container fails health checks
**Resolution**: Ensure application starts correctly and health endpoint is accessible

---

## Integration with Workflow

### Step 1: Generate Dockerfiles
```bash
cd frontend
docker ai "Create a multi-stage Dockerfile for my Next.js 16 application with production optimization"

cd ../backend
docker ai "Create a multi-stage Dockerfile for my FastAPI application with Python 3.11"
```

### Step 2: Audit Security
```bash
cd frontend
docker ai "rate my Dockerfile"

cd ../backend
docker ai "rate my Dockerfile"
```

### Step 3: Generate docker-compose
```bash
cd ..
docker ai "Create a docker-compose.yml for local testing with Next.js frontend on port 3000 and FastAPI backend on port 8001"
```

### Step 4: Build and Test
```bash
docker-compose build
docker-compose up -d
docker-compose logs -f
```

---

## Success Criteria

**Dockerfile Generation**:
- ✅ Builds successfully without errors
- ✅ Image size under limits (frontend <500MB, backend <300MB)
- ✅ Runs as non-root user
- ✅ Passes security audit with no critical issues

**docker-compose Generation**:
- ✅ All services start successfully
- ✅ Frontend can communicate with backend
- ✅ Environment variables properly configured
- ✅ Application functions identically to non-containerized version

**Security Audit**:
- ✅ No critical or high-severity vulnerabilities
- ✅ All constitutional requirements met
- ✅ Best practices recommendations addressed

---

## Agent Limitations

**What Gordon CAN Do**:
- Generate Dockerfiles and docker-compose configurations
- Audit security vulnerabilities
- Optimize image size and build performance
- Provide best practices recommendations

**What Gordon CANNOT Do**:
- Generate Kubernetes manifests (use kubectl-ai)
- Deploy to Kubernetes clusters (use kubectl-ai)
- Monitor cluster health (use Kagent)
- Modify application source code
- Create Helm charts (use kubectl-ai or Claude Code)

---

## Review and Approval Process

**Before Deployment**:
1. Gordon generates Dockerfile
2. Technical Lead reviews generated Dockerfile
3. Security audit performed (`docker ai "rate my Dockerfile"`)
4. Build test performed locally
5. Technical Lead approves for use
6. Dockerfile committed to repository

**Constitutional Safeguard**: All Gordon-generated code must be reviewed by Technical Lead before deployment to Minikube cluster.
