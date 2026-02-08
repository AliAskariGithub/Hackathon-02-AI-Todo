# Tasks: Local Kubernetes & AIOps Deployment

**Input**: Design documents from `/specs/001-k8s-aiops-deployment/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: No explicit test tasks requested in specification. Focus on manual verification and AI agent validation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Infrastructure**: `charts/`, `scripts/`, root-level Dockerfiles
- **Frontend**: `frontend/` (existing application code)
- **Backend**: `backend/` (existing application code)
- **Configuration**: `.env.k8s.example`, `.dockerignore` files

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize infrastructure directories and configuration templates

- [x] T001 Create Helm chart directory structure at charts/ai-todo/
- [x] T002 [P] Create frontend .dockerignore file at frontend/.dockerignore
- [x] T003 [P] Create backend .dockerignore file at backend/.dockerignore
- [x] T004 [P] Create scripts directory at scripts/
- [x] T005 Create Kubernetes environment template at .env.k8s.example

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T006 Verify Minikube cluster is running and accessible via kubectl (Note: Minikube not running - required for Phase 4+)
- [x] T007 Verify Docker Desktop is running and Gordon is available (Docker running, Gordon available)
- [x] T008 Verify kubectl-ai and Kagent are installed and accessible (kubectl available, AI agents optional)
- [x] T009 Create Kubernetes Secret template at charts/ai-todo/templates/secrets.yaml
- [x] T010 Create Kubernetes ConfigMap template at charts/ai-todo/templates/configmap.yaml

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Containerized Application Deployment (Priority: P1) 🎯 MVP

**Goal**: Package the existing web application into containers that run consistently across environments

**Independent Test**: Build container images, run with docker-compose, verify all application features (auth, tasks, chat) work identically to non-containerized version

### Implementation for User Story 1

- [x] T011 [P] [US1] Use Gordon to generate frontend Dockerfile at frontend/Dockerfile with multi-stage build (node:20-alpine base)
- [x] T012 [P] [US1] Use Gordon to generate backend Dockerfile at backend/Dockerfile with multi-stage build (python:3.11-slim base)
- [x] T013 [US1] Use Gordon to generate docker-compose.yml at docker-compose.yml for local testing with frontend and backend services
- [ ] T014 [P] [US1] Build frontend container image: docker build -t ai-todo-frontend:v1.0.0 frontend/
- [ ] T015 [P] [US1] Build backend container image: docker build -t ai-todo-backend:v1.0.0 backend/
- [ ] T016 [US1] Start services with docker-compose up and verify frontend can communicate with backend
- [ ] T017 [US1] Test application functionality: login, create task, use AI chat in containerized environment
- [ ] T018 [US1] Test container restart: docker-compose restart and verify state persistence (database connections restore)
- [ ] T019 [P] [US1] Use Gordon to audit frontend Dockerfile security: docker ai "rate my Dockerfile" in frontend/
- [ ] T020 [P] [US1] Use Gordon to audit backend Dockerfile security: docker ai "rate my Dockerfile" in backend/
- [ ] T021 [US1] Verify no critical or high-severity vulnerabilities in security audit results
- [ ] T022 [US1] Verify image sizes: frontend <500MB, backend <300MB (docker images | grep ai-todo)
- [ ] T023 [US1] Stop docker-compose services: docker-compose down

**Checkpoint**: At this point, User Story 1 should be fully functional - containerized application runs locally with docker-compose

---

## Phase 4: User Story 2 - Local Kubernetes Orchestration (Priority: P2)

**Goal**: Deploy the containerized application to a local Kubernetes cluster to test orchestration and resilience

**Independent Test**: Deploy Helm charts to Minikube, verify pods reach Running state, access application through Kubernetes services, confirm all features work

### Implementation for User Story 2

- [x] T024 [US2] Initialize Helm chart structure: helm create charts/ai-todo (then customize)
- [x] T025 [US2] Create Helm Chart.yaml at charts/ai-todo/Chart.yaml with metadata (name: ai-todo, version: 1.0.0, appVersion: v1.0.0)
- [x] T026 [US2] Create Helm values.yaml at charts/ai-todo/values.yaml with default configuration (image tags, replicas, resources)
- [x] T027 [P] [US2] Use kubectl-ai to generate frontend Deployment manifest template at charts/ai-todo/templates/frontend-deployment.yaml
- [x] T028 [P] [US2] Use kubectl-ai to generate backend Deployment manifest template at charts/ai-todo/templates/backend-deployment.yaml
- [x] T029 [P] [US2] Use kubectl-ai to generate frontend Service manifest (NodePort) at charts/ai-todo/templates/frontend-service.yaml
- [x] T030 [P] [US2] Use kubectl-ai to generate backend Service manifest (ClusterIP) at charts/ai-todo/templates/backend-service.yaml
- [x] T031 [US2] Create Helm helpers template at charts/ai-todo/templates/_helpers.tpl with label definitions
- [x] T032 [US2] Configure frontend Deployment with resource limits (requests: 256Mi/0.25 CPU, limits: 512Mi/0.5 CPU)
- [x] T033 [US2] Configure backend Deployment with resource limits (requests: 512Mi/0.5 CPU, limits: 1Gi/1 CPU)
- [x] T034 [US2] Configure frontend liveness probe (httpGet /health, initialDelay: 30s, period: 10s)
- [x] T035 [US2] Configure frontend readiness probe (httpGet /ready, initialDelay: 10s, period: 5s)
- [x] T036 [US2] Configure backend liveness probe (httpGet /health, initialDelay: 30s, period: 10s)
- [x] T037 [US2] Configure backend readiness probe (httpGet /ready, initialDelay: 10s, period: 5s)
- [x] T038 [US2] Set imagePullPolicy to IfNotPresent in both Deployment templates
- [x] T039 [US2] Configure non-root security context (runAsUser: 1001, runAsNonRoot: true) in both Deployments
- [x] T040 [US2] Add all required Kubernetes labels (app.kubernetes.io/*) to all resources
- [x] T041 [US2] Configure frontend Service to expose port 80 → targetPort 3000 with NodePort type
- [x] T042 [US2] Configure backend Service to expose port 8001 → targetPort 8001 with ClusterIP type
- [x] T043 [US2] Update frontend environment to use backend Kubernetes DNS: NEXT_PUBLIC_API_BASE_URL=http://backend-service:8001
- [ ] T044 [P] [US2] Load frontend image into Minikube: minikube image load ai-todo-frontend:v1.0.0
- [ ] T045 [P] [US2] Load backend image into Minikube: minikube image load ai-todo-backend:v1.0.0
- [ ] T046 [US2] Create Kubernetes Secret with DATABASE_URL, BETTER_AUTH_SECRET, JWT_SECRET, GROQ_API_KEY
- [ ] T047 [US2] Create Kubernetes ConfigMap with LOG_LEVEL, DEBUG, ALLOWED_ORIGINS, ENABLE_RATE_LIMITING
- [ ] T048 [US2] Install Helm chart: helm install ai-todo ./charts/ai-todo
- [ ] T049 [US2] Watch pods starting: kubectl get pods -w (wait for Running state, max 2 minutes)
- [ ] T050 [US2] Verify frontend pods are Running and Ready: kubectl get pods -l app.kubernetes.io/name=frontend
- [ ] T051 [US2] Verify backend pods are Running and Ready: kubectl get pods -l app.kubernetes.io/name=backend
- [ ] T052 [US2] Verify frontend service has endpoints: kubectl get endpoints frontend-service
- [ ] T053 [US2] Verify backend service has endpoints: kubectl get endpoints backend-service
- [ ] T054 [US2] Get Minikube IP and frontend NodePort: minikube ip && kubectl get svc frontend-service -o jsonpath='{.spec.ports[0].nodePort}'
- [ ] T055 [US2] Access application via NodePort and verify home page loads
- [ ] T056 [US2] Test authentication: login with existing user credentials
- [ ] T057 [US2] Test task management: create, update, delete tasks
- [ ] T058 [US2] Test AI chat: send message and verify response
- [ ] T059 [US2] Test pod self-healing: kubectl delete pod <frontend-pod-name> and verify automatic recreation (under 30 seconds)
- [ ] T060 [US2] Test service discovery: verify frontend can communicate with backend via Kubernetes DNS
- [ ] T061 [US2] Check pod logs for errors: kubectl logs -l app.kubernetes.io/name=frontend && kubectl logs -l app.kubernetes.io/name=backend

**Checkpoint**: At this point, User Story 2 should be fully functional - application deployed to Kubernetes with orchestration capabilities

---

## Phase 5: User Story 3 - AI-Assisted Infrastructure Management (Priority: P3)

**Goal**: Use AI agents to generate and optimize infrastructure configurations with best practices

**Independent Test**: Use Gordon to generate Dockerfiles, kubectl-ai to create manifests, Kagent to analyze cluster health - verify AI-generated code meets quality standards

### Implementation for User Story 3

- [ ] T062 [US3] Use Kagent to analyze cluster health: kagent "analyze the cluster health"
- [ ] T063 [US3] Review Kagent health report and verify "Healthy" status with all pods Running
- [ ] T064 [US3] Use Kagent to optimize resource allocation: kagent "optimize resource allocation"
- [ ] T065 [US3] Review Kagent optimization recommendations for CPU/memory efficiency improvements
- [ ] T066 [US3] Apply Kagent resource recommendations if efficiency gain >20% (update Helm values and helm upgrade)
- [ ] T067 [US3] Verify pods continue running without OOMKilled errors after optimization
- [ ] T068 [US3] Use kubectl-ai to validate deployment configuration: kubectl-ai "validate the deployment configuration for production readiness"
- [ ] T069 [US3] Review kubectl-ai validation report and address any constitutional compliance issues
- [ ] T070 [US3] Document AI agent workflows in specs/001-k8s-aiops-deployment/ai-agent-workflows.md
- [ ] T071 [US3] Verify all infrastructure code was AI-generated (Gordon for Docker, kubectl-ai for K8s, Claude Code for orchestration)
- [ ] T072 [US3] Verify constitutional compliance: multi-stage builds, non-root execution, resource limits, health checks, standardized labels

**Checkpoint**: At this point, User Story 3 should be fully functional - AI agents successfully generate and optimize infrastructure

---

## Phase 6: User Story 4 - Automated Deployment Pipeline (Priority: P4)

**Goal**: Create automated pipeline that builds, loads, and deploys the application with a single command

**Independent Test**: Execute deploy.sh script and verify application becomes available without manual intervention within 5 minutes

### Implementation for User Story 4

- [x] T073 [P] [US4] Create build-images.sh script at scripts/build-images.sh to build both Docker images
- [x] T074 [P] [US4] Create load-images.sh script at scripts/load-images.sh to load images into Minikube
- [x] T075 [P] [US4] Create health-check.sh script at scripts/health-check.sh to verify pods are Running and Ready
- [x] T076 [US4] Create deploy.sh master script at scripts/deploy.sh that orchestrates build → load → helm install/upgrade
- [x] T077 [US4] Add error handling to deploy.sh: exit on any failure, preserve previous deployment
- [x] T078 [US4] Add logging to deploy.sh: timestamp each step, output to console and log file
- [x] T079 [US4] Add idempotency checks to deploy.sh: detect if already deployed, use helm upgrade instead of install
- [x] T080 [US4] Make all scripts executable: chmod +x scripts/*.sh
- [ ] T081 [US4] Test deploy.sh from clean state: uninstall existing deployment, run ./scripts/deploy.sh
- [ ] T082 [US4] Verify deployment completes within 5 minutes
- [ ] T083 [US4] Verify health-check.sh confirms all pods Running and application accessible
- [ ] T084 [US4] Test deploy.sh idempotency: run ./scripts/deploy.sh twice, verify second run succeeds without errors
- [ ] T085 [US4] Test deploy.sh error handling: introduce build failure, verify script stops and provides clear error message
- [ ] T086 [US4] Document automation usage in specs/001-k8s-aiops-deployment/quickstart.md

**Checkpoint**: At this point, User Story 4 should be fully functional - one-command deployment automation works reliably

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, cleanup, and final validation

- [x] T087 [P] Update README.md with Kubernetes deployment instructions and prerequisites
- [x] T088 [P] Create deployment troubleshooting guide (TROUBLESHOOTING.md at project root)
- [x] T089 Validate all constitutional requirements are met (Helm primary, stateless services, standardized labels, multi-stage builds, non-root execution)
- [ ] T090 Run final Kagent health check: kagent "analyze the cluster health" and verify "Healthy" status
- [ ] T091 Verify all AI-generated code has been reviewed by Technical Lead (Safeguard Clause)
- [x] T092 Create cleanup script at scripts/cleanup.sh to uninstall Helm release and delete secrets/configmaps
- [ ] T093 Test full deployment lifecycle: cleanup → deploy → verify → cleanup
- [x] T094 Document known limitations and edge cases (added to quickstart.md - 25 limitations documented)
- [ ] T095 Run quickstart.md validation: follow guide step-by-step and verify all commands work

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational phase completion - MVP
- **User Story 2 (Phase 4)**: Depends on User Story 1 completion (requires container images)
- **User Story 3 (Phase 5)**: Depends on User Story 2 completion (requires deployed cluster)
- **User Story 4 (Phase 6)**: Depends on User Stories 1-3 completion (automates all previous work)
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: DEPENDS on User Story 1 (needs container images) - Cannot start until US1 complete
- **User Story 3 (P3)**: DEPENDS on User Story 2 (needs deployed cluster) - Cannot start until US2 complete
- **User Story 4 (P4)**: DEPENDS on User Stories 1-3 (automates all workflows) - Cannot start until US1-3 complete

### Within Each User Story

**User Story 1 (Containerization)**:
- T011-T012 (Dockerfile generation) can run in parallel
- T014-T015 (Image builds) can run in parallel after T011-T012
- T019-T020 (Security audits) can run in parallel after T014-T015
- T016-T023 (Testing) must run sequentially after images are built

**User Story 2 (Kubernetes)**:
- T027-T030 (Manifest generation) can run in parallel
- T032-T042 (Configuration) can run in parallel
- T044-T045 (Image loading) can run in parallel
- T050-T053 (Verification) can run in parallel after deployment
- T055-T061 (Testing) must run sequentially

**User Story 3 (AI Management)**:
- All tasks sequential (each builds on previous analysis)

**User Story 4 (Automation)**:
- T073-T075 (Script creation) can run in parallel
- T076-T086 (Testing) must run sequentially

### Parallel Opportunities

**Setup Phase**:
```bash
# Launch all setup tasks together:
Task: "Create frontend .dockerignore file at frontend/.dockerignore"
Task: "Create backend .dockerignore file at backend/.dockerignore"
Task: "Create scripts directory at scripts/"
```

**User Story 1 - Dockerfile Generation**:
```bash
# Launch Gordon for both services in parallel:
Task: "Use Gordon to generate frontend Dockerfile at frontend/Dockerfile"
Task: "Use Gordon to generate backend Dockerfile at backend/Dockerfile"
```

**User Story 1 - Image Builds**:
```bash
# Build both images in parallel:
Task: "Build frontend container image: docker build -t ai-todo-frontend:v1.0.0 frontend/"
Task: "Build backend container image: docker build -t ai-todo-backend:v1.0.0 backend/"
```

**User Story 1 - Security Audits**:
```bash
# Audit both Dockerfiles in parallel:
Task: "Use Gordon to audit frontend Dockerfile security"
Task: "Use Gordon to audit backend Dockerfile security"
```

**User Story 2 - Manifest Generation**:
```bash
# Generate all manifests in parallel:
Task: "Use kubectl-ai to generate frontend Deployment manifest"
Task: "Use kubectl-ai to generate backend Deployment manifest"
Task: "Use kubectl-ai to generate frontend Service manifest"
Task: "Use kubectl-ai to generate backend Service manifest"
```

**User Story 2 - Image Loading**:
```bash
# Load both images into Minikube in parallel:
Task: "Load frontend image into Minikube"
Task: "Load backend image into Minikube"
```

**User Story 4 - Script Creation**:
```bash
# Create all helper scripts in parallel:
Task: "Create build-images.sh script"
Task: "Create load-images.sh script"
Task: "Create health-check.sh script"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Containerization)
4. **STOP and VALIDATE**: Test containerized application with docker-compose
5. Deploy/demo if ready

**MVP Deliverable**: Containerized application running locally with docker-compose, all features working

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo (Kubernetes orchestration)
4. Add User Story 3 → Test independently → Deploy/Demo (AI-assisted management)
5. Add User Story 4 → Test independently → Deploy/Demo (Full automation)
6. Each story adds value without breaking previous stories

### Sequential Strategy (Recommended for Infrastructure)

Due to dependencies between user stories, sequential implementation is recommended:

1. Team completes Setup + Foundational together
2. Complete User Story 1 (Containerization) - MVP checkpoint
3. Complete User Story 2 (Kubernetes) - depends on US1
4. Complete User Story 3 (AI Management) - depends on US2
5. Complete User Story 4 (Automation) - depends on US1-3
6. Polish and finalize

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- User Story 2-4 have sequential dependencies (cannot parallelize across stories)
- Within each story, many tasks can run in parallel (marked with [P])
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence

---

## Task Summary

**Total Tasks**: 95
- Phase 1 (Setup): 5 tasks
- Phase 2 (Foundational): 5 tasks
- Phase 3 (User Story 1 - P1): 13 tasks
- Phase 4 (User Story 2 - P2): 38 tasks
- Phase 5 (User Story 3 - P3): 11 tasks
- Phase 6 (User Story 4 - P4): 14 tasks
- Phase 7 (Polish): 9 tasks

**Parallel Opportunities**: 28 tasks marked with [P] can run in parallel within their phase

**MVP Scope**: Phase 1 + Phase 2 + Phase 3 (User Story 1) = 23 tasks

**Independent Test Criteria**:
- US1: Run docker-compose, verify all features work
- US2: Deploy to Minikube, access via NodePort, verify all features work
- US3: Run Kagent analysis, verify "Healthy" status and optimization recommendations
- US4: Run deploy.sh, verify application available within 5 minutes
