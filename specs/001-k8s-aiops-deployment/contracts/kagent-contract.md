# Kagent (SRE) Agent Contract

**Agent**: Kagent
**Role**: Site Reliability Engineer (SRE)
**Responsibility**: Cluster health analysis, resource optimization, and troubleshooting

## Agent Capabilities

Kagent is a specialized AI agent for Kubernetes cluster operations with the following capabilities:
- Analyze cluster health and resource utilization
- Identify performance bottlenecks and resource constraints
- Provide optimization recommendations for resource allocation
- Troubleshoot pod failures and deployment issues
- Monitor cluster capacity and suggest scaling strategies
- Validate deployment configurations against best practices

## Invocation Patterns

### 1. Analyze Cluster Health

**Command**:
```bash
kagent "analyze the cluster health"
```

**Context Required**:
- Access to Kubernetes cluster (kubectl context)
- Namespace to analyze (default or specified)
- Current cluster state (nodes, pods, services)

**Expected Output**:
- Comprehensive health report including:
  - Node status and resource availability
  - Pod status across all namespaces
  - Resource utilization (CPU, memory)
  - Failed or pending pods
  - Service endpoint status
  - Overall health rating (Healthy, Warning, Critical)

**Validation**:
- Report accurately reflects cluster state
- Issues are prioritized by severity
- Recommendations are actionable

---

### 2. Optimize Resource Allocation

**Command**:
```bash
kagent "optimize resource allocation"
```

**Context Required**:
- Current deployment configurations
- Historical resource usage patterns
- Cluster capacity constraints
- Performance requirements

**Expected Output**:
- Resource optimization recommendations:
  - Adjusted CPU/memory requests and limits
  - Right-sizing suggestions for over/under-provisioned pods
  - Resource efficiency improvements
  - Expected performance impact
- Estimated resource savings (percentage)

**Validation**:
- Recommendations improve resource efficiency by at least 20%
- No pods experience OOMKilled errors after applying changes
- Application performance remains stable

---

### 3. Troubleshoot Pod Failures

**Command**:
```bash
kagent "why is the frontend pod in CrashLoopBackOff?"
```

**Context Required**:
- Pod name or deployment name
- Recent pod events
- Container logs
- Resource constraints

**Expected Output**:
- Root cause analysis:
  - Specific failure reason (OOMKilled, application error, config issue)
  - Contributing factors (resource limits, missing dependencies)
  - Timeline of events leading to failure
- Step-by-step remediation plan

**Validation**:
- Root cause correctly identified
- Remediation steps resolve the issue
- Preventive measures suggested

---

### 4. Validate Deployment Configuration

**Command**:
```bash
kagent "validate the deployment configuration for production readiness"
```

**Context Required**:
- Deployment YAML or Helm chart
- Target environment (local dev, staging, production)
- Constitutional requirements

**Expected Output**:
- Configuration validation report:
  - Constitutional compliance check
  - Best practices adherence
  - Security posture assessment
  - Resource allocation appropriateness
  - Missing or misconfigured settings
- Pass/Fail status with detailed findings

**Validation**:
- All constitutional requirements verified
- Security issues identified
- Recommendations align with best practices

---

### 5. Monitor Cluster Capacity

**Command**:
```bash
kagent "check if the cluster has enough capacity for the deployment"
```

**Context Required**:
- Deployment resource requirements
- Current cluster capacity
- Existing resource allocations
- Node specifications

**Expected Output**:
- Capacity analysis:
  - Available vs required resources
  - Node-level capacity breakdown
  - Scheduling feasibility
  - Potential resource contention
- Recommendations for capacity planning

**Validation**:
- Accurate capacity calculations
- Scheduling predictions are correct
- Recommendations prevent resource exhaustion

---

## Input Requirements

### Cluster Health Analysis

**Required Information**:
- Kubernetes cluster access (kubectl context: minikube)
- Namespace: default (or specified)
- Time window: current state + recent history (5-10 minutes)

**Expected Health Report Structure**:
```
Cluster Health Report
=====================
Generated: 2026-02-08 10:30:00
Cluster: minikube
Namespace: default

Overall Status: Healthy ✅

Nodes:
- minikube: Ready (4 CPU, 8GB RAM)
  - Allocatable: 3.5 CPU, 7GB RAM
  - Used: 1.2 CPU (34%), 3.5GB RAM (50%)
  - Available: 2.3 CPU, 3.5GB RAM

Pods:
- Total: 4
- Running: 4 ✅
- Pending: 0
- Failed: 0
- CrashLoopBackOff: 0

Deployments:
- frontend: 2/2 replicas ready ✅
- backend: 1/1 replicas ready ✅

Services:
- frontend-service: 2 endpoints ✅
- backend-service: 1 endpoint ✅

Resource Utilization:
- CPU: 34% (1.2/3.5 cores)
- Memory: 50% (3.5GB/7GB)
- Disk: 25% (10GB/40GB)

Issues: None

Recommendations:
1. Resource utilization is healthy
2. Consider adding resource quotas for namespace isolation
3. Monitor memory usage trends over time
```

---

### Resource Optimization Analysis

**Required Information**:
- Current deployment resource specifications
- Actual resource usage (from metrics-server or monitoring)
- Performance requirements (latency, throughput)
- Cluster capacity constraints

**Expected Optimization Report Structure**:
```
Resource Optimization Report
============================
Generated: 2026-02-08 10:30:00
Namespace: default

Frontend Deployment:
- Current Requests: 256Mi RAM, 250m CPU
- Current Limits: 512Mi RAM, 500m CPU
- Actual Usage: 180Mi RAM (70% of request), 150m CPU (60% of request)
- Recommendation: Reduce requests to 200Mi RAM, 200m CPU
- Efficiency Gain: 22% memory, 20% CPU
- Risk: Low (usage well below new requests)

Backend Deployment:
- Current Requests: 512Mi RAM, 500m CPU
- Current Limits: 1Gi RAM, 1000m CPU
- Actual Usage: 450Mi RAM (88% of request), 400m CPU (80% of request)
- Recommendation: Keep current requests (usage near threshold)
- Efficiency Gain: 0% (already optimized)
- Risk: N/A

Overall Savings:
- Memory: 56Mi (11% of total allocated)
- CPU: 50m (10% of total allocated)
- Cluster Capacity Freed: 1.4% memory, 1.4% CPU

Action Items:
1. Update frontend deployment resource requests
2. Monitor for 24 hours to validate changes
3. Adjust limits if needed based on peak usage
```

---

## Output Specifications

### Health Report Requirements

**Constitutional Compliance**:
- ✅ All pods have resource limits defined
- ✅ All pods have health checks configured
- ✅ All pods run as non-root
- ✅ All services have endpoints
- ✅ No critical security issues

**Severity Levels**:
- **Healthy**: All systems operational, no issues
- **Warning**: Minor issues, no immediate impact
- **Critical**: Service degradation or failures

**Metrics Tracked**:
- Node health and capacity
- Pod status and restart counts
- Resource utilization (CPU, memory, disk)
- Service endpoint availability
- Deployment replica status
- Recent events and errors

---

## Error Handling

### Common Issues and Resolutions

**Issue**: OOMKilled pods
**Cause**: Memory limit too low for actual usage
**Resolution**: Increase memory limits, optimize application memory usage

**Issue**: Pending pods (unschedulable)
**Cause**: Insufficient cluster resources
**Resolution**: Reduce resource requests or add cluster capacity

**Issue**: CrashLoopBackOff
**Cause**: Application startup failure, missing dependencies
**Resolution**: Check logs, verify environment variables, adjust health check timing

**Issue**: High CPU throttling
**Cause**: CPU limits too restrictive
**Resolution**: Increase CPU limits or optimize application performance

**Issue**: Service has no endpoints
**Cause**: No ready pods matching selector
**Resolution**: Fix pod readiness issues, verify label selectors

---

## Integration with Workflow

### Step 1: Pre-Deployment Validation
```bash
# Before deploying, validate configuration
kagent "validate the deployment configuration for production readiness"

# Check cluster capacity
kagent "check if the cluster has enough capacity for the deployment"
```

### Step 2: Post-Deployment Health Check
```bash
# After helm install, verify health
kagent "analyze the cluster health"

# Check specific deployment
kagent "check the status of the frontend deployment"
```

### Step 3: Ongoing Optimization
```bash
# After application runs for a while, optimize resources
kagent "optimize resource allocation"

# Monitor for issues
kagent "show me any pods that have restarted recently"
```

### Step 4: Troubleshooting
```bash
# If issues occur
kagent "why is the backend pod failing?"
kagent "what's causing high memory usage in the frontend?"
```

---

## Success Criteria

**Health Analysis**:
- ✅ Accurate cluster state representation
- ✅ All issues identified and prioritized
- ✅ Overall health status reflects reality
- ✅ Recommendations are actionable

**Resource Optimization**:
- ✅ Resource efficiency improved by at least 20%
- ✅ No performance degradation after optimization
- ✅ No OOMKilled or CPU throttling issues
- ✅ Cluster capacity better utilized

**Troubleshooting**:
- ✅ Root cause identified correctly
- ✅ Remediation steps resolve the issue
- ✅ Preventive measures suggested
- ✅ Clear, step-by-step guidance provided

**Configuration Validation**:
- ✅ All constitutional requirements verified
- ✅ Security issues identified
- ✅ Best practices compliance checked
- ✅ Pass/Fail status with detailed findings

---

## Agent Limitations

**What Kagent CAN Do**:
- Analyze cluster health and resource utilization
- Provide optimization recommendations
- Troubleshoot pod failures and deployment issues
- Validate configurations against best practices
- Monitor cluster capacity and performance

**What Kagent CANNOT Do**:
- Generate Dockerfiles (use Gordon)
- Generate Kubernetes manifests (use kubectl-ai)
- Modify deployments directly (provides recommendations only)
- Create Helm charts (use Claude Code)
- Fix application code bugs (identifies infrastructure issues only)

---

## Monitoring Metrics

### Key Performance Indicators (KPIs)

**Resource Utilization**:
- CPU usage percentage (target: 50-80%)
- Memory usage percentage (target: 50-80%)
- Disk usage percentage (target: <80%)

**Availability**:
- Pod ready percentage (target: 100%)
- Service endpoint availability (target: 100%)
- Deployment replica status (target: desired = actual)

**Performance**:
- Pod restart count (target: 0 restarts/hour)
- Container startup time (target: <30 seconds)
- Health check success rate (target: >99%)

**Capacity**:
- Cluster CPU capacity remaining (target: >20%)
- Cluster memory capacity remaining (target: >20%)
- Schedulable pods (target: no pending pods)

---

## Best Practices Validation

### Constitutional Requirements Checklist

**Infrastructure-as-Code**:
- ✅ All resources managed via Helm
- ✅ Stateless services (no local state)
- ✅ Standardized labels present

**Containerization**:
- ✅ Multi-stage builds used
- ✅ Non-root execution configured
- ✅ Semantic versioning for images

**Operational Standards**:
- ✅ Health check endpoints exposed
- ✅ Resource requests and limits defined
- ✅ Rolling update strategy configured

**Security**:
- ✅ Non-root security context
- ✅ No hardcoded secrets
- ✅ Secrets managed via Kubernetes Secrets

---

## Review and Approval Process

**Health Check Workflow**:
1. Kagent analyzes cluster health
2. Report generated with findings
3. Technical Lead reviews report
4. Critical issues addressed immediately
5. Optimization recommendations prioritized
6. Changes implemented and validated

**Optimization Workflow**:
1. Kagent provides resource optimization recommendations
2. Technical Lead reviews recommendations
3. Changes tested in development environment
4. Performance validated (no degradation)
5. Changes applied to cluster
6. Monitoring continues for 24 hours

**Constitutional Safeguard**: All Kagent recommendations must be reviewed and approved by Technical Lead before implementation.
