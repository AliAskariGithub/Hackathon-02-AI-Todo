# Minikube, Helm & Kubernetes Guide

## Table of Contents

- [Introduction](#introduction)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Core Concepts](#core-concepts)
- [Getting Started](#getting-started)
- [Common Commands](#common-commands)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)
- [Resources](#resources)

---

## Introduction

This guide provides comprehensive information about deploying and managing the AI Todo application using Minikube, Helm, and Kubernetes.

### What is Minikube?

Minikube is a tool that runs a single-node Kubernetes cluster locally on your machine. It's perfect for:
- Local development and testing
- Learning Kubernetes
- CI/CD pipelines
- Testing deployments before production

### What is Helm?

Helm is a package manager for Kubernetes that:
- Simplifies application deployment
- Manages complex Kubernetes manifests
- Provides versioning and rollback capabilities
- Enables configuration templating

### What is Kubernetes?

Kubernetes (K8s) is a container orchestration platform that:
- Automates deployment, scaling, and management of containerized applications
- Provides self-healing capabilities
- Manages load balancing and service discovery
- Handles rolling updates and rollbacks

---

## Prerequisites

### System Requirements

**Minimum:**
- 2 CPUs or more
- 2GB of free memory
- 20GB of free disk space
- Internet connection
- Container or virtual machine manager (Docker, Hyperkit, Hyper-V, etc.)

**Recommended:**
- 4 CPUs or more
- 8GB of free memory
- 50GB of free disk space

### Required Software

1. **Docker Desktop** (Windows/Mac) or **Docker Engine** (Linux)
   - Download: https://www.docker.com/products/docker-desktop

2. **Minikube**
   - Windows: `choco install minikube` or download from https://minikube.sigs.k8s.io/
   - Mac: `brew install minikube`
   - Linux: `curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64`

3. **kubectl** (Kubernetes CLI)
   - Windows: `choco install kubernetes-cli`
   - Mac: `brew install kubectl`
   - Linux: `curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"`

4. **Helm** (Package Manager)
   - Windows: `choco install kubernetes-helm`
   - Mac: `brew install helm`
   - Linux: `curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash`

### Verify Installation

```bash
# Check Minikube version
minikube version

# Check kubectl version
kubectl version --client

# Check Helm version
helm version

# Check Docker version
docker --version
```

---

## Core Concepts

### Kubernetes Architecture

```
┌─────────────────────────────────────────┐
│         Kubernetes Cluster              │
│  ┌────────────────────────────────────┐ │
│  │  Control Plane (Master Node)       │ │
│  │  - API Server                      │ │
│  │  - Scheduler                       │ │
│  │  - Controller Manager              │ │
│  │  - etcd (Key-Value Store)          │ │
│  └────────────────────────────────────┘ │
│  ┌────────────────────────────────────┐ │
│  │  Worker Nodes                      │ │
│  │  ┌──────────────────────────────┐  │ │
│  │  │  Pods (Containers)           │  │ │
│  │  │  - Frontend                  │  │ │
│  │  │  - Backend                   │  │ │
│  │  └──────────────────────────────┘  │ │
│  │  - kubelet                         │ │
│  │  - kube-proxy                      │ │
│  └────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

### Key Kubernetes Objects

**Pod:**
- Smallest deployable unit
- Contains one or more containers
- Shares network and storage

**Deployment:**
- Manages replica sets
- Handles rolling updates
- Provides declarative updates

**Service:**
- Exposes pods to network
- Provides load balancing
- Types: ClusterIP, NodePort, LoadBalancer

**ConfigMap:**
- Stores configuration data
- Separates config from code
- Can be mounted as files or env vars

**Secret:**
- Stores sensitive data
- Base64 encoded
- Used for passwords, tokens, keys

**Namespace:**
- Virtual clusters
- Resource isolation
- Access control boundaries

### Helm Concepts

**Chart:**
- Package of Kubernetes resources
- Contains templates and values
- Versioned and shareable

**Release:**
- Instance of a chart
- Deployed to cluster
- Can be upgraded or rolled back

**Values:**
- Configuration parameters
- Override default settings
- Can be provided via files or CLI

---

## Getting Started

### 1. Start Minikube

```bash
# Start Minikube with Docker driver
minikube start --driver=docker

# Start with specific resources
minikube start --cpus=4 --memory=8192 --disk-size=50g

# Check status
minikube status
```

### 2. Configure kubectl

```bash
# Set context to Minikube
kubectl config use-context minikube

# Verify connection
kubectl cluster-info

# Check nodes
kubectl get nodes
```

### 3. Enable Addons (Optional)

```bash
# Enable metrics server (for resource monitoring)
minikube addons enable metrics-server

# Enable dashboard
minikube addons enable dashboard

# Enable ingress
minikube addons enable ingress

# List all addons
minikube addons list
```

### 4. Access Minikube Dashboard

```bash
# Open Kubernetes dashboard
minikube dashboard

# Get dashboard URL
minikube dashboard --url
```

---

## Common Commands

### Minikube Commands

```bash
# Start cluster
minikube start

# Stop cluster
minikube stop

# Delete cluster
minikube delete

# Pause cluster
minikube pause

# Unpause cluster
minikube unpause

# Get cluster IP
minikube ip

# SSH into Minikube
minikube ssh

# View logs
minikube logs

# Load Docker image into Minikube
minikube image load <image-name>:<tag>

# List images in Minikube
minikube image ls

# Access service
minikube service <service-name>

# Get service URL
minikube service <service-name> --url

# Create tunnel (for LoadBalancer services)
minikube tunnel
```

### kubectl Commands

**Cluster Information:**
```bash
# Cluster info
kubectl cluster-info

# Get nodes
kubectl get nodes

# Describe node
kubectl describe node <node-name>
```

**Pod Management:**
```bash
# List pods
kubectl get pods

# List pods with more details
kubectl get pods -o wide

# Describe pod
kubectl describe pod <pod-name>

# Get pod logs
kubectl logs <pod-name>

# Follow logs
kubectl logs -f <pod-name>

# Execute command in pod
kubectl exec -it <pod-name> -- /bin/sh

# Delete pod
kubectl delete pod <pod-name>
```

**Deployment Management:**
```bash
# List deployments
kubectl get deployments

# Describe deployment
kubectl describe deployment <deployment-name>

# Scale deployment
kubectl scale deployment <deployment-name> --replicas=3

# Update image
kubectl set image deployment/<deployment-name> <container-name>=<new-image>

# Rollout status
kubectl rollout status deployment/<deployment-name>

# Rollout history
kubectl rollout history deployment/<deployment-name>

# Rollback
kubectl rollout undo deployment/<deployment-name>

# Restart deployment
kubectl rollout restart deployment/<deployment-name>
```

**Service Management:**
```bash
# List services
kubectl get services

# Describe service
kubectl describe service <service-name>

# Port forward
kubectl port-forward service/<service-name> <local-port>:<service-port>

# Delete service
kubectl delete service <service-name>
```

**ConfigMap & Secrets:**
```bash
# List configmaps
kubectl get configmaps

# Describe configmap
kubectl describe configmap <configmap-name>

# Edit configmap
kubectl edit configmap <configmap-name>

# List secrets
kubectl get secrets

# Describe secret
kubectl describe secret <secret-name>
```

**Namespace Management:**
```bash
# List namespaces
kubectl get namespaces

# Create namespace
kubectl create namespace <namespace-name>

# Set default namespace
kubectl config set-context --current --namespace=<namespace-name>

# Delete namespace
kubectl delete namespace <namespace-name>
```

**Resource Monitoring:**
```bash
# Get all resources
kubectl get all

# Get resources with labels
kubectl get all -l app=myapp

# Watch resources
kubectl get pods --watch

# Top pods (requires metrics-server)
kubectl top pods

# Top nodes
kubectl top nodes
```

### Helm Commands

**Chart Management:**
```bash
# Search for charts
helm search hub <keyword>

# Add repository
helm repo add <repo-name> <repo-url>

# Update repositories
helm repo update

# List repositories
helm repo list

# Remove repository
helm repo remove <repo-name>
```

**Release Management:**
```bash
# Install chart
helm install <release-name> <chart-path>

# Install with custom values
helm install <release-name> <chart-path> -f values.yaml

# Install with set values
helm install <release-name> <chart-path> --set key=value

# List releases
helm list

# Get release status
helm status <release-name>

# Upgrade release
helm upgrade <release-name> <chart-path>

# Rollback release
helm rollback <release-name> <revision>

# Uninstall release
helm uninstall <release-name>

# Get release history
helm history <release-name>

# Get release values
helm get values <release-name>

# Get release manifest
helm get manifest <release-name>
```

**Chart Development:**
```bash
# Create new chart
helm create <chart-name>

# Lint chart
helm lint <chart-path>

# Template chart (dry-run)
helm template <release-name> <chart-path>

# Package chart
helm package <chart-path>

# Test release
helm test <release-name>
```

---

## Troubleshooting

### Common Issues

#### 1. Minikube Won't Start

**Problem:** Minikube fails to start

**Solutions:**
```bash
# Delete and recreate cluster
minikube delete
minikube start

# Try different driver
minikube start --driver=virtualbox

# Check Docker is running
docker ps

# Increase resources
minikube start --cpus=4 --memory=8192
```

#### 2. Pods Not Starting

**Problem:** Pods stuck in Pending or CrashLoopBackOff

**Solutions:**
```bash
# Check pod status
kubectl describe pod <pod-name>

# Check events
kubectl get events --sort-by=.metadata.creationTimestamp

# Check logs
kubectl logs <pod-name>

# Check previous logs (if crashed)
kubectl logs <pod-name> --previous

# Check resource limits
kubectl top pods
kubectl top nodes
```

#### 3. Image Pull Errors

**Problem:** ImagePullBackOff or ErrImagePull

**Solutions:**
```bash
# Load image into Minikube
minikube image load <image-name>:<tag>

# Verify image exists
minikube image ls | grep <image-name>

# Set imagePullPolicy to IfNotPresent
# In deployment YAML: imagePullPolicy: IfNotPresent
```

#### 4. Service Not Accessible

**Problem:** Cannot access service from host

**Solutions:**
```bash
# Use port forwarding
kubectl port-forward service/<service-name> <local-port>:<service-port>

# Use minikube service
minikube service <service-name>

# Check service endpoints
kubectl get endpoints <service-name>

# Verify service selector matches pod labels
kubectl describe service <service-name>
kubectl get pods --show-labels
```

#### 5. CORS Errors

**Problem:** Frontend cannot connect to backend

**Solutions:**
```bash
# Update backend CORS configuration
kubectl edit configmap <configmap-name>

# Add frontend URL to ALLOWED_ORIGINS
# ALLOWED_ORIGINS: http://localhost:3000,http://localhost:8080

# Restart backend
kubectl rollout restart deployment/<backend-deployment>
```

#### 6. Port Already in Use

**Problem:** Port forwarding fails with "address already in use"

**Solutions:**
```bash
# Find process using port (Windows)
netstat -ano | findstr :<port>

# Find process using port (Linux/Mac)
lsof -i :<port>

# Kill process (Windows)
taskkill /PID <pid> /F

# Kill process (Linux/Mac)
kill -9 <pid>

# Use different port
kubectl port-forward service/<service-name> <different-port>:<service-port>
```

### Debugging Commands

```bash
# Get all resources in namespace
kubectl get all -n <namespace>

# Describe all pods
kubectl describe pods

# Get events
kubectl get events --sort-by=.metadata.creationTimestamp

# Check cluster info
kubectl cluster-info dump

# Check node status
kubectl describe nodes

# Check resource usage
kubectl top pods
kubectl top nodes

# Check API server logs
minikube logs

# SSH into Minikube
minikube ssh

# Check Docker containers in Minikube
minikube ssh
docker ps
```

---

## Best Practices

### 1. Resource Management

**Set Resource Limits:**
```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

**Use Namespaces:**
```bash
# Create namespace for each environment
kubectl create namespace development
kubectl create namespace staging
kubectl create namespace production
```

### 2. Configuration Management

**Use ConfigMaps for Configuration:**
```bash
# Create from file
kubectl create configmap app-config --from-file=config.yaml

# Create from literal
kubectl create configmap app-config --from-literal=key=value
```

**Use Secrets for Sensitive Data:**
```bash
# Create secret
kubectl create secret generic app-secrets \
  --from-literal=db-password=mypassword \
  --from-literal=api-key=myapikey
```

### 3. Health Checks

**Define Liveness and Readiness Probes:**
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 5
```

### 4. Deployment Strategies

**Use Rolling Updates:**
```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1
    maxUnavailable: 0
```

**Test Before Deploying:**
```bash
# Dry run
kubectl apply -f deployment.yaml --dry-run=client

# Template with Helm
helm template myapp ./chart

# Lint Helm chart
helm lint ./chart
```

### 5. Monitoring and Logging

**Enable Metrics Server:**
```bash
minikube addons enable metrics-server
```

**View Logs:**
```bash
# Stream logs
kubectl logs -f <pod-name>

# Logs from all pods in deployment
kubectl logs -f deployment/<deployment-name>

# Previous logs (if crashed)
kubectl logs <pod-name> --previous
```

### 6. Security

**Run as Non-Root:**
```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1001
  fsGroup: 1001
```

**Use Network Policies:**
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend-to-backend
spec:
  podSelector:
    matchLabels:
      app: backend
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
```

### 7. Backup and Recovery

**Backup Helm Values:**
```bash
# Export current values
helm get values <release-name> > backup-values.yaml
```

**Backup Kubernetes Resources:**
```bash
# Export all resources
kubectl get all -o yaml > backup.yaml

# Export specific resource
kubectl get deployment <name> -o yaml > deployment-backup.yaml
```

---

## Resources

### Official Documentation

- **Kubernetes:** https://kubernetes.io/docs/
- **Minikube:** https://minikube.sigs.k8s.io/docs/
- **Helm:** https://helm.sh/docs/
- **kubectl:** https://kubernetes.io/docs/reference/kubectl/

### Learning Resources

- **Kubernetes Basics:** https://kubernetes.io/docs/tutorials/kubernetes-basics/
- **Helm Getting Started:** https://helm.sh/docs/intro/quickstart/
- **Minikube Tutorial:** https://kubernetes.io/docs/tutorials/hello-minikube/

### Community

- **Kubernetes Slack:** https://slack.k8s.io/
- **Helm Community:** https://helm.sh/community/
- **Stack Overflow:** https://stackoverflow.com/questions/tagged/kubernetes

### Tools

- **k9s:** Terminal UI for Kubernetes - https://k9scli.io/
- **Lens:** Kubernetes IDE - https://k8slens.dev/
- **Kubectx/Kubens:** Context and namespace switcher - https://github.com/ahmetb/kubectx

---

## Next Steps

1. **Read the Deployment Guide:** See `MINIKUBE_DEPLOYMENT.md` for step-by-step deployment instructions
2. **Explore Helm Charts:** Check the `charts/ai-todo/` directory for chart configuration
3. **Set Up Monitoring:** Install Prometheus and Grafana for observability
4. **Configure Ingress:** Set up Ingress controller for better routing
5. **Deploy to Cloud:** Move to production Kubernetes (EKS, GKE, AKS)

---

**Last Updated:** February 2026
**Version:** 1.0.0
