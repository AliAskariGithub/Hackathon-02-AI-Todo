# Minikube Quick Reference Guide

## Quick Start

```bash
# Start Minikube
minikube start

# Check status
minikube status

# Access application
# Frontend: http://localhost:8080
# Backend: http://localhost:8000
```

## Common Commands

### Cluster Management

```bash
# Start cluster
minikube start

# Stop cluster
minikube stop

# Delete cluster
minikube delete

# Get cluster IP
minikube ip

# SSH into cluster
minikube ssh

# View cluster info
kubectl cluster-info
```

### Application Access

```bash
# Port forwarding (recommended)
kubectl port-forward service/ai-todo-frontend 8080:80 &
kubectl port-forward service/backend-service 8000:8000 &

# NodePort access
minikube service ai-todo-frontend

# Ingress access (requires tunnel)
minikube tunnel
# Then add to hosts: 127.0.0.1 ai-todo.local
# Access at: http://ai-todo.local
```

### Pod Management

```bash
# List all pods
kubectl get pods

# Get pod details
kubectl describe pod <pod-name>

# View pod logs
kubectl logs <pod-name>

# Follow logs
kubectl logs -f <pod-name>

# Execute command in pod
kubectl exec -it <pod-name> -- /bin/sh

# Restart deployment
kubectl rollout restart deployment/ai-todo-backend
kubectl rollout restart deployment/ai-todo-frontend
```

### Service Management

```bash
# List services
kubectl get services

# Get service details
kubectl describe service <service-name>

# Check service endpoints
kubectl get endpoints
```

### Helm Operations

```bash
# List releases
helm list

# Get release status
helm status ai-todo

# Upgrade release
helm upgrade ai-todo ./charts/ai-todo -f charts/ai-todo/values.yaml

# Rollback release
helm rollback ai-todo

# Uninstall release
helm uninstall ai-todo
```

### Monitoring & Debugging

```bash
# Check resource usage
kubectl top nodes
kubectl top pods

# View cluster events
kubectl get events --sort-by=.metadata.creationTimestamp

# Check pod status
kubectl get pods -o wide

# Describe pod for troubleshooting
kubectl describe pod <pod-name>

# Check logs for errors
kubectl logs <pod-name> --previous
```

### Configuration Management

```bash
# View ConfigMap
kubectl get configmap ai-todo-config -o yaml

# Edit ConfigMap
kubectl edit configmap ai-todo-config

# View Secrets
kubectl get secrets

# Describe Secret
kubectl describe secret ai-todo-secrets
```

### Ingress Management

```bash
# List Ingress resources
kubectl get ingress

# Describe Ingress
kubectl describe ingress ai-todo-ingress

# Check Ingress controller
kubectl get pods -n ingress-nginx

# View Ingress controller logs
kubectl logs -n ingress-nginx -l app.kubernetes.io/component=controller
```

### Dashboard Access

```bash
# Open dashboard in browser
minikube dashboard

# Get dashboard URL
minikube dashboard --url
```

## Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl get pods

# Describe pod for details
kubectl describe pod <pod-name>

# Check logs
kubectl logs <pod-name>

# Check events
kubectl get events --sort-by=.metadata.creationTimestamp
```

### Image Pull Errors

```bash
# Load image into Minikube
minikube image load <image-name>:<tag>

# Verify image exists
minikube image ls | grep <image-name>

# Set imagePullPolicy to IfNotPresent in deployment
```

### Service Not Accessible

```bash
# Check service endpoints
kubectl get endpoints <service-name>

# Verify service selector matches pod labels
kubectl describe service <service-name>
kubectl get pods --show-labels

# Use port forwarding
kubectl port-forward service/<service-name> <local-port>:<service-port>
```

### CORS Errors

```bash
# Update CORS configuration
kubectl patch configmap ai-todo-config --type merge -p '{"data":{"ALLOWED_ORIGINS":"http://localhost:3000,http://localhost:8080"}}'

# Restart backend
kubectl rollout restart deployment/ai-todo-backend
```

### Port Already in Use

```bash
# Find process using port (Windows)
netstat -ano | findstr :<port>

# Kill process (Windows)
taskkill /PID <pid> /F

# Find process using port (Linux/Mac)
lsof -i :<port>

# Kill process (Linux/Mac)
kill -9 <pid>
```

## Quick Health Checks

```bash
# Check all pods are running
kubectl get pods | grep -v Running

# Test backend health
curl http://localhost:8000/health

# Test frontend
curl -I http://localhost:8080

# Check resource usage
kubectl top pods

# View recent events
kubectl get events --sort-by=.metadata.creationTimestamp | tail -10
```

## Cleanup

```bash
# Delete deployment
helm uninstall ai-todo

# Stop port forwarding
pkill -f "kubectl port-forward"

# Stop Minikube
minikube stop

# Delete cluster (removes all data)
minikube delete
```

## Environment Variables

### Frontend
- `NEXT_PUBLIC_API_BASE_URL`: Backend API URL
- `NEXT_PUBLIC_SITE_URL`: Frontend site URL
- `BETTER_AUTH_SECRET`: Authentication secret

### Backend
- `DATABASE_URL`: PostgreSQL connection string
- `ALLOWED_ORIGINS`: CORS allowed origins
- `JWT_SECRET`: JWT token secret
- `GROQ_API_KEY`: Groq API key for AI features

## Useful Aliases

Add these to your shell profile for faster access:

```bash
# Kubernetes aliases
alias k='kubectl'
alias kgp='kubectl get pods'
alias kgs='kubectl get services'
alias kgi='kubectl get ingress'
alias kl='kubectl logs'
alias kd='kubectl describe'

# Minikube aliases
alias mk='minikube'
alias mks='minikube status'
alias mki='minikube ip'
alias mkd='minikube dashboard'

# Helm aliases
alias h='helm'
alias hl='helm list'
alias hs='helm status'
```

## Access URLs

### Development (Port Forwarding)
- Frontend: http://localhost:8080
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

### NodePort (Direct)
- Frontend: http://192.168.49.2:31752

### Ingress (Production-like)
- Frontend: http://ai-todo.local
- Backend: http://ai-todo.local/api
- API Docs: http://ai-todo.local/docs
- Health: http://ai-todo.local/health

## Support

For detailed information, see:
- `docs/MINIKUBE_GUIDE.md` - Comprehensive guide
- `docs/MINIKUBE_DEPLOYMENT.md` - Deployment instructions
- `docs/INGRESS_SETUP.md` - Ingress configuration
- `docs/DOCKER_GUIDE.md` - Docker setup

---

**Last Updated:** February 2026
**Version:** 1.0.0
