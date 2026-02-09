# Ingress Setup for AI Todo Application

## Overview

This guide explains how to access the AI Todo application using Kubernetes Ingress, which provides a production-like setup with advanced routing capabilities.

## Prerequisites

- Minikube cluster running
- Ingress addon enabled (`minikube addons enable ingress`)
- Application deployed via Helm

## Ingress Configuration

The Ingress resource is configured to route traffic based on paths:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ai-todo-ingress
  namespace: default
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/ssl-redirect: "false"
    nginx.ingress.kubernetes.io/use-regex: "true"
spec:
  ingressClassName: nginx
  rules:
  - host: ai-todo.local
    http:
      paths:
      # Backend API routes
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: backend-service
            port:
              number: 8000
      - path: /docs
        pathType: Prefix
        backend:
          service:
            name: backend-service
            port:
              number: 8000
      - path: /health
        pathType: Prefix
        backend:
          service:
            name: backend-service
            port:
              number: 8000
      # Frontend routes (catch-all)
      - path: /
        pathType: Prefix
        backend:
          service:
            name: ai-todo-frontend
            port:
              number: 80
```

## Setup Instructions

### Step 1: Enable Ingress Addon

```bash
# Enable Ingress controller
minikube addons enable ingress

# Wait for Ingress controller to be ready
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=120s
```

### Step 2: Apply Ingress Configuration

```bash
# Apply the Ingress resource
kubectl apply -f k8s/ingress.yaml

# Verify Ingress is created
kubectl get ingress ai-todo-ingress

# Check Ingress details
kubectl describe ingress ai-todo-ingress
```

### Step 3: Configure Hosts File

Add the following entry to your hosts file:

**Windows:** `C:\Windows\System32\drivers\etc\hosts`
**Linux/Mac:** `/etc/hosts`

```
192.168.49.2 ai-todo.local
```

**Note:** Replace `192.168.49.2` with your Minikube IP if different:
```bash
minikube ip
```

### Step 4: Access the Application

Once configured, access the application at:

- **Frontend:** http://ai-todo.local
- **Backend API:** http://ai-todo.local/api
- **API Documentation:** http://ai-todo.local/docs
- **Health Check:** http://ai-todo.local/health

## Verification

### Test Ingress Routing

```bash
# Test frontend
curl -H "Host: ai-todo.local" http://192.168.49.2/

# Test backend health
curl -H "Host: ai-todo.local" http://192.168.49.2/health

# Test API endpoint
curl -H "Host: ai-todo.local" http://192.168.49.2/api/analytics/stats
```

### Check Ingress Status

```bash
# Get Ingress details
kubectl get ingress ai-todo-ingress -o wide

# Check Ingress controller logs
kubectl logs -n ingress-nginx -l app.kubernetes.io/component=controller
```

## Troubleshooting

### Issue: Cannot access ai-todo.local

**Solution:**
1. Verify hosts file entry is correct
2. Check Minikube IP: `minikube ip`
3. Ensure Ingress controller is running:
   ```bash
   kubectl get pods -n ingress-nginx
   ```

### Issue: 404 Not Found

**Solution:**
1. Verify Ingress is created: `kubectl get ingress`
2. Check backend services are running: `kubectl get svc`
3. Review Ingress configuration: `kubectl describe ingress ai-todo-ingress`

### Issue: Backend API not accessible

**Solution:**
1. Check backend service endpoints:
   ```bash
   kubectl get endpoints backend-service
   ```
2. Verify backend pods are running:
   ```bash
   kubectl get pods -l app.kubernetes.io/name=backend
   ```
3. Check backend logs:
   ```bash
   kubectl logs -l app.kubernetes.io/name=backend
   ```

## Advanced Configuration

### Enable TLS/SSL

To enable HTTPS, create a TLS secret and update the Ingress:

```bash
# Create self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout tls.key -out tls.crt \
  -subj "/CN=ai-todo.local/O=ai-todo"

# Create Kubernetes secret
kubectl create secret tls ai-todo-tls \
  --key tls.key \
  --cert tls.crt

# Update Ingress to use TLS
kubectl patch ingress ai-todo-ingress -p '
spec:
  tls:
  - hosts:
    - ai-todo.local
    secretName: ai-todo-tls
'
```

### Custom Domain

To use a custom domain:

1. Update the Ingress host:
   ```bash
   kubectl patch ingress ai-todo-ingress -p '
   spec:
     rules:
     - host: your-domain.com
   '
   ```

2. Update hosts file or DNS records to point to Minikube IP

## Comparison: Access Methods

| Method | URL | Use Case | Pros | Cons |
|--------|-----|----------|------|------|
| **Port Forwarding** | localhost:8080 | Local development | Simple, no config | Manual process, single user |
| **NodePort** | 192.168.49.2:31752 | Direct access | No port forwarding needed | Non-standard ports |
| **Ingress** | ai-todo.local | Production-like | Standard ports, path-based routing | Requires hosts file |

## Next Steps

1. **Production Deployment:** Deploy to cloud Kubernetes (EKS, GKE, AKS)
2. **SSL/TLS:** Configure proper certificates with Let's Encrypt
3. **DNS:** Set up proper DNS records instead of hosts file
4. **Monitoring:** Add Prometheus and Grafana for observability
5. **Rate Limiting:** Configure Ingress rate limiting annotations

---

**Last Updated:** February 2026
**Version:** 1.0.0
