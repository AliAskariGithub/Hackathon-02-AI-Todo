# Dapr Components Documentation

## Overview

This document describes all Dapr components used in the AI Todo Event-Driven Architecture, their configurations, and usage patterns.

## Component List

| Component Name | Type | Purpose |
|----------------|------|---------|
| `kafka-pubsub` | Pub/Sub | Event messaging via Kafka |
| `statestore` | State Store | Idempotency tracking and state management |
| `secretstore` | Secret Store | Kubernetes secrets management |
| `tracing-config` | Configuration | Distributed tracing with OpenTelemetry |

---

## Component Details

### 1. kafka-pubsub (Pub/Sub Component)

**Type**: `pubsub.kafka`

**Purpose**: Enables publish/subscribe messaging pattern using Kafka as the message broker.

**Configuration**:

```yaml
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
    value: "ai-todo-kafka-kafka-bootstrap:9092"
  - name: consumerGroup
    value: "ai-todo-consumers"
  - name: clientId
    value: "ai-todo-client"
  - name: authType
    value: "none"
  - name: maxMessageBytes
    value: "1048576"  # 1MB
  - name: consumeRetryInterval
    value: "200ms"
```

**Metadata Fields**:

- **brokers**: Kafka bootstrap server address
  - Value: `ai-todo-kafka-kafka-bootstrap:9092`
  - Points to Strimzi-managed Kafka cluster

- **consumerGroup**: Consumer group ID for all microservices
  - Value: `ai-todo-consumers`
  - Ensures load balancing across consumer instances

- **clientId**: Client identifier for Kafka connections
  - Value: `ai-todo-client`
  - Used for monitoring and debugging

- **authType**: Authentication method
  - Value: `none` (local development)
  - Production: Use `certificate` or `password`

- **maxMessageBytes**: Maximum message size
  - Value: `1048576` (1MB)
  - Prevents oversized messages

- **consumeRetryInterval**: Retry interval for failed consumption
  - Value: `200ms`
  - Balances responsiveness and resource usage

**Usage**:

```python
# Publishing events
from dapr.clients import DaprClient

with DaprClient() as client:
    client.publish_event(
        pubsub_name='kafka-pubsub',
        topic_name='todo.task.events',
        data=json.dumps(event_data),
        data_content_type='application/json'
    )
```

```python
# Subscribing to events (via Dapr subscription endpoint)
@app.get('/dapr/subscribe')
def subscribe():
    return [{
        'pubsubname': 'kafka-pubsub',
        'topic': 'todo.task.events',
        'route': '/events/task'
    }]

@app.post('/events/task')
async def handle_task_event(request: Request):
    event_data = await request.json()
    # Process event
    return {'status': 'success'}
```

**Best Practices**:
- Always set `data_content_type` to `application/json`
- Use correlation IDs for event tracing
- Implement idempotency in event handlers
- Return 200 for success, 500 for retry

---

### 2. statestore (State Store Component)

**Type**: `state.postgresql`

**Purpose**: Provides distributed state management for idempotency tracking, caching, and session storage.

**Configuration**:

```yaml
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
  - name: tableName
    value: "dapr_state"
  - name: metadataTableName
    value: "dapr_metadata"
  - name: timeoutInSeconds
    value: "30"
  - name: cleanupIntervalInSeconds
    value: "3600"
```

**Metadata Fields**:

- **connectionString**: PostgreSQL connection string
  - Stored in Kubernetes secret
  - Format: `host=<host> user=<user> password=<password> dbname=<db> sslmode=require`

- **tableName**: Main state table name
  - Value: `dapr_state`
  - Stores key-value pairs

- **metadataTableName**: Metadata table name
  - Value: `dapr_metadata`
  - Stores table schema version

- **timeoutInSeconds**: Operation timeout
  - Value: `30`
  - Prevents hanging operations

- **cleanupIntervalInSeconds**: TTL cleanup interval
  - Value: `3600` (1 hour)
  - Removes expired state entries

**Usage**:

```python
# Storing state with TTL
from dapr.clients import DaprClient

with DaprClient() as client:
    client.save_state(
        store_name='statestore',
        key=f'idempotency:{correlation_id}',
        value='processed',
        state_metadata={
            'ttlInSeconds': '86400'  # 24 hours
        }
    )
```

```python
# Retrieving state
with DaprClient() as client:
    state = client.get_state(
        store_name='statestore',
        key=f'idempotency:{correlation_id}'
    )

    if state.data:
        # Already processed
        return {'status': 'duplicate'}
```

```python
# Deleting state
with DaprClient() as client:
    client.delete_state(
        store_name='statestore',
        key=f'idempotency:{correlation_id}'
    )
```

**Use Cases**:
- **Idempotency Tracking**: Store correlation IDs to prevent duplicate processing
- **Session Management**: Store user session data
- **Caching**: Cache frequently accessed data
- **Rate Limiting**: Track request counts per user

**Best Practices**:
- Always set TTL to prevent unbounded growth
- Use namespaced keys (e.g., `idempotency:`, `session:`, `cache:`)
- Handle state not found gracefully
- Use transactions for atomic operations

---

### 3. secretstore (Secret Store Component)

**Type**: `secretstores.kubernetes`

**Purpose**: Provides secure access to Kubernetes secrets for sensitive configuration.

**Configuration**:

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: secretstore
  namespace: default
spec:
  type: secretstores.kubernetes
  version: v1
  metadata: []
```

**Usage**:

```python
# Retrieving secrets
from dapr.clients import DaprClient

with DaprClient() as client:
    secret = client.get_secret(
        store_name='secretstore',
        key='postgres-secret',
        metadata={'namespace': 'default'}
    )

    connection_string = secret.secrets['connectionString']
```

**Kubernetes Secret Format**:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: postgres-secret
  namespace: default
type: Opaque
stringData:
  connectionString: "host=postgres user=admin password=secret dbname=todo"
  apiKey: "your-api-key"
```

**Best Practices**:
- Never hardcode secrets in code or configuration
- Use Kubernetes secrets for all sensitive data
- Rotate secrets regularly
- Limit secret access with RBAC

---

### 4. tracing-config (Configuration Component)

**Type**: `configuration`

**Purpose**: Configures distributed tracing with OpenTelemetry and Zipkin for observability.

**Configuration**:

```yaml
apiVersion: dapr.io/v1alpha1
kind: Configuration
metadata:
  name: tracing-config
  namespace: default
spec:
  tracing:
    samplingRate: "1"
    zipkin:
      endpointAddress: "http://zipkin:9411/api/v2/spans"
  metric:
    enabled: true
  features:
    - name: ServiceInvocation
      enabled: true
```

**Tracing Settings**:

- **samplingRate**: Percentage of traces to capture
  - Value: `1` (100% sampling)
  - Production: Use `0.1` (10%) to reduce overhead

- **zipkin.endpointAddress**: Zipkin collector endpoint
  - Value: `http://zipkin:9411/api/v2/spans`
  - Sends traces to Zipkin for visualization

**Metric Settings**:

- **enabled**: Enable Prometheus metrics
  - Value: `true`
  - Exposes metrics at `/metrics` endpoint

**Features**:

- **ServiceInvocation**: Enable service-to-service invocation tracing
  - Required for Dapr Service Invocation calls

**Usage**:

Tracing is automatic when configuration is applied. Access traces via:

```bash
# Port forward Zipkin
kubectl port-forward svc/zipkin 9411:9411

# Open Zipkin UI
open http://localhost:9411
```

**Trace Context Propagation**:

```python
# Dapr automatically propagates trace context
# Add custom spans for detailed tracing
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("process_task_event"):
    # Your code here
    pass
```

**Best Practices**:
- Use 100% sampling in development, 10% in production
- Add custom spans for critical operations
- Include correlation IDs in span attributes
- Monitor trace latency and error rates

---

## Component Lifecycle

### Initialization Order

1. **Secrets** (secretstore) - Must be available first
2. **State Store** (statestore) - Depends on secrets for connection
3. **Pub/Sub** (kafka-pubsub) - Can initialize in parallel with state store
4. **Configuration** (tracing-config) - Applied to all components

### Health Checks

```bash
# Check component status
kubectl get components

# Describe component for details
kubectl describe component kafka-pubsub

# View Dapr sidecar logs
kubectl logs <pod-name> -c daprd
```

### Troubleshooting

**Component Not Ready**:
```bash
# Check component events
kubectl describe component <component-name>

# Check Dapr operator logs
kubectl logs -l app=dapr-operator -n dapr-system

# Verify dependencies (Kafka, PostgreSQL)
kubectl get pods
```

**Connection Errors**:
```bash
# Test Kafka connectivity
kubectl exec -it <pod-name> -c daprd -- \
  curl http://localhost:3500/v1.0/healthz

# Test state store connectivity
kubectl exec -it <pod-name> -c daprd -- \
  curl http://localhost:3500/v1.0/state/statestore
```

---

## Security Considerations

### Production Hardening

1. **Kafka Authentication**:
   ```yaml
   - name: authType
     value: "certificate"
   - name: caCert
     secretKeyRef:
       name: kafka-certs
       key: ca.crt
   ```

2. **State Store Encryption**:
   ```yaml
   - name: connectionString
     secretKeyRef:
       name: postgres-secret
       key: connectionString
   # Connection string should include sslmode=require
   ```

3. **Network Policies**:
   - Restrict pod-to-pod communication
   - Allow only necessary ports (3500 for Dapr, 9092 for Kafka)

4. **RBAC**:
   - Limit secret access to specific service accounts
   - Use namespace isolation

---

## Performance Tuning

### Pub/Sub Optimization

```yaml
# Increase throughput
- name: maxMessageBytes
  value: "2097152"  # 2MB

# Reduce latency
- name: consumeRetryInterval
  value: "100ms"

# Batch processing
- name: maxBulkPubBytes
  value: "131072"  # 128KB
```

### State Store Optimization

```yaml
# Connection pooling
- name: maxIdleConns
  value: "10"
- name: maxOpenConns
  value: "20"

# Query timeout
- name: queryExecMode
  value: "cache_statement"
```

---

## Monitoring

### Metrics

Dapr exposes Prometheus metrics at `http://localhost:9090/metrics`:

- `dapr_component_loaded`: Component initialization status
- `dapr_pubsub_ingress_count`: Messages received
- `dapr_pubsub_egress_count`: Messages published
- `dapr_state_operation_count`: State operations
- `dapr_http_server_request_count`: HTTP requests

### Alerts

Recommended alerts:
- Component initialization failures
- High pub/sub error rate (> 1%)
- State store connection failures
- Trace sampling rate drops

---

## Migration Guide

### Upgrading Dapr Version

```bash
# Backup current configuration
kubectl get components -o yaml > components-backup.yaml

# Upgrade Dapr
dapr upgrade -k --runtime-version 1.15.0

# Verify components still work
kubectl get components
```

### Changing Component Type

```bash
# Example: Migrate from PostgreSQL to Redis state store
# 1. Deploy new component
kubectl apply -f redis-statestore.yaml

# 2. Update application to use new component
# 3. Migrate data (if needed)
# 4. Remove old component
kubectl delete component statestore
```

---

## References

- [Dapr Pub/Sub Spec](https://docs.dapr.io/reference/components-reference/supported-pubsub/)
- [Dapr State Store Spec](https://docs.dapr.io/reference/components-reference/supported-state-stores/)
- [Dapr Secret Store Spec](https://docs.dapr.io/reference/components-reference/supported-secret-stores/)
- [Dapr Configuration Spec](https://docs.dapr.io/reference/configuration-spec/)
