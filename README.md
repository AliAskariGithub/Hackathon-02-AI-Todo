# AI Todo Application

A full-stack AI-powered todo application built with modern web technologies. The project includes both frontend and backend components with authentication, task management, and testimonials system.

## 🚀 Features

### Core Features
- **Secure Authentication**: Cookie-based authentication with HTTP-only cookies for XSS protection
- **Task Management**: Full CRUD operations on tasks with optimistic updates
- **Testimonials System**: User-submitted testimonials with ratings and feedback
- **Responsive UI**: Mobile-friendly design with loading states and error handling
- **Automatic Token Refresh**: Seamless 14-minute token refresh for uninterrupted sessions
- **Database Integration**: PostgreSQL with Neon hosting for serverless scalability

### Interactive Chat Experience 🆕
- **AI Task Assistant**: Natural language chat interface for task management
- **Simple Language Mode**: AI responses in grade 6-8 reading level for better accessibility
- **Keyboard Shortcuts**: Power user navigation with visual indicators
  - `Cmd/Ctrl + K`: Focus chat input
  - `Enter`: Send message
  - `Shift + Enter`: New line
  - `Esc`: Exit focus mode
- **Focus Mode**: Distraction-free chat with smooth animations and centered layout
- **Task Navigation**: Click task references in chat to navigate directly to task details
- **JSON Display Toggle**: Switch between human-readable and structured JSON responses
- **Accessibility**: Full keyboard navigation, ARIA labels, reduced motion support

### Enhanced UI/UX
- **Custom Auth Pages**: Login/signup pages with Electric Lime theme (#0FFF50)
- **Testimonial Carousel**: Auto-rotating testimonials with smooth transitions
- **Dynamic Pages**: Contact page with form validation, Settings page with tabbed UI
- **Comprehensive Footer**: Multi-column responsive footer with navigation and social links
- **Smooth Animations**: Page transitions using Framer Motion with accessibility considerations
- **Theme System**: Dark/light mode toggle with consistent color scheme

## 🛠️ Tech Stack

### Frontend
- Next.js 16.1.2 with App Router
- React 19.2.3
- TypeScript
- Tailwind CSS
- shadcn/ui components
- Lucide React icons
- Framer Motion 12.31.0 for animations
- Better Auth for authentication
- Zustand 5.0.11 for state management
- react-json-view 1.21.3 for JSON rendering
- Zod for form validation
- React Hook Form for form handling

### Backend
- Python 3.11+
- FastAPI
- SQLModel
- PostgreSQL (Neon serverless)
- JWT for authentication
- bcrypt for password hashing

### Infrastructure & DevOps
- **Containerization**: Docker with multi-stage builds
- **Orchestration**: Kubernetes (Minikube for local)
- **Package Management**: Helm 3.x
- **Automation**: Bash scripts for build/deploy/health-check workflows
- **Security**: Non-root containers, resource limits, health probes

## 📋 Prerequisites

### For Local Development
- Node.js 18+ (for frontend)
- Python 3.11+ (for backend)
- PostgreSQL database (or Neon account)

### For Kubernetes Deployment
- Docker 20.10+ (with Docker Desktop recommended)
- Minikube 1.30+ (for local Kubernetes cluster)
- kubectl 1.27+ (Kubernetes CLI)
- Helm 3.12+ (Kubernetes package manager)
- 4GB+ RAM available for Minikube
- 20GB+ disk space for images and cluster

## 🚀 Quick Start

### Automated Setup (Recommended)

**For Windows:**
```bash
# Frontend
cd frontend
setup-local.bat

# Backend
cd backend
setup-local.bat
```

**For macOS/Linux:**
```bash
# Frontend
cd frontend
chmod +x setup-local.sh
./setup-local.sh

# Backend
cd backend
chmod +x setup-local.sh
./setup-local.sh
```

### Manual Setup

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Copy the environment file and configure:
```bash
# For local development
cp .env.example .env.local

# For production
cp .env.example .env.production
```

4. Edit `.env.local` with your configuration:
```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_SITE_URL=http://localhost:3000
```

**Note:** Authentication now uses secure HTTP-only cookies. No additional auth configuration needed in frontend environment variables.

5. Start the development server:
```bash
npm run dev
```

**Available on:**
- Primary: `http://localhost:3000`
- Alternative: `http://localhost:3001`

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create and activate a virtual environment:
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy the environment file and configure:
```bash
# For local development
cp .env.example .env.local

# For production
cp .env.example .env.production
```

5. Edit `.env.local` with your configuration:
```env
DATABASE_URL=sqlite:///./ai_todo_dev.db
SECRET_KEY=your-secret-key-here
ENVIRONMENT=development
GROQ_API_KEY=your-groq-api-key-here
GROQ_MODEL=llama-3.3-70b-versatile
PORT=8001
DEBUG=true
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
```

**Note:** The SECRET_KEY is used for JWT token signing. Generate a secure random string for production.

6. Start the backend server:
```bash
python main.py
```

**Available on:**
- Primary: `http://localhost:8000`
- Alternative: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

## 🔧 Environment Variables

### Frontend Environment Variables

Create `.env.local` for local development or `.env.production` for production:

```env
# API Configuration
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000  # or production URL
NEXT_PUBLIC_SITE_URL=http://localhost:3000      # or production URL

# Development Settings (optional)
NEXT_PUBLIC_DEBUG=true
NEXT_PUBLIC_VERBOSE_LOGGING=true
```

**Note:** Authentication is handled via HTTP-only cookies. No auth secrets needed in frontend environment.

### Backend Environment Variables

Create `.env.local` for local development or `.env.production` for production:

```env
# Database
DATABASE_URL=sqlite:///./ai_todo_dev.db  # or PostgreSQL URL

# Authentication & Security
SECRET_KEY=your-secret-key-here  # Used for JWT token signing
ENVIRONMENT=development  # or 'production' (enables HTTPS-only cookies)
ACCESS_TOKEN_EXPIRE_MINUTES=15  # Short-lived access tokens
REFRESH_TOKEN_EXPIRE_DAYS=7  # Long-lived refresh tokens

# AI Configuration
GROQ_API_KEY=your-groq-api-key-here
GROQ_MODEL=llama-3.3-70b-versatile

# Server Configuration
HOST=0.0.0.0
PORT=8001
DEBUG=true
LOG_LEVEL=debug

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001

# Rate Limiting
ENABLE_RATE_LIMITING=false
RATE_LIMIT_PER_MINUTE=100
```

**Important Security Notes:**
- **SECRET_KEY**: Generate a secure random string (32+ characters) for production using: `openssl rand -base64 32`
- **ENVIRONMENT**: Set to `production` in production to enable secure HTTPS-only cookies
- **HTTPS Required**: In production, you MUST use HTTPS for cookie-based authentication to work
- Never commit `.env.local` or `.env.production` to version control

For detailed environment setup instructions, see [ENVIRONMENT_SETUP.md](./ENVIRONMENT_SETUP.md)

## 🏗️ Project Structure

```
├── backend/                 # Python FastAPI backend
│   ├── src/
│   │   ├── api/           # API routes
│   │   │   └── routers/   # API endpoints (tasks, chat, users, etc.)
│   │   ├── models/        # Database models
│   │   ├── services/      # Business logic
│   │   ├── mcp/           # MCP tools and runners
│   │   └── utils/         # Utilities
│   ├── main.py            # Application entry point
│   ├── requirements.txt   # Python dependencies
│   ├── .env.example       # Environment template
│   └── setup-local.sh/bat # Setup scripts
├── frontend/               # Next.js frontend
│   ├── app/               # App Router pages
│   │   ├── (auth)/        # Auth pages (login, signup, settings)
│   │   ├── chat/          # Chat page (main route)
│   │   ├── contact/       # Contact page
│   │   ├── dashboard/     # Dashboard page
│   │   └── page.tsx       # Home page
│   ├── components/        # React components
│   │   ├── chat/          # Chat components
│   │   │   ├── FocusModeToggle.tsx
│   │   │   ├── FocusModeWrapper.tsx
│   │   │   ├── DisplayModeToggle.tsx
│   │   │   ├── JsonMessageView.tsx
│   │   │   ├── TaskLinkButton.tsx
│   │   │   └── KeyboardShortcutHint.tsx
│   │   ├── ui/            # UI components (shadcn/ui + custom)
│   │   │   ├── kbd.tsx    # Keyboard shortcut indicator
│   │   │   └── ...        # Other UI components
│   │   ├── Navbar.tsx     # Navigation bar
│   │   └── Footer.tsx     # Footer with links
│   ├── lib/               # Shared utilities
│   │   ├── animations.ts  # Framer Motion variants
│   │   └── utils/         # Utility functions
│   │       └── taskLinkGenerator.ts
│   ├── hooks/             # React hooks
│   │   ├── useKeyboardShortcuts.ts
│   │   ├── useReducedMotion.ts
│   │   └── use-toast.ts
│   ├── stores/            # Zustand stores
│   │   └── ui-store.ts    # UI state (focus mode, display mode)
│   ├── providers/         # React context providers
│   ├── services/          # API clients
│   ├── .env.example       # Environment template
│   └── setup-local.sh/bat # Setup scripts
├── specs/                 # Feature specifications
│   └── 008-todo-interactive-chat/
│       ├── spec.md        # Feature specification
│       ├── plan.md        # Implementation plan
│       └── tasks.md       # Task breakdown
├── history/               # Development history
│   ├── prompts/           # Prompt History Records
│   └── adr/               # Architecture Decision Records
├── CLAUDE.md              # Project instructions for Claude
├── ENVIRONMENT_SETUP.md   # Detailed environment setup guide
├── TESTING_GUIDE.md       # Testing instructions
└── README.md              # This file
```

## 🧪 Available Scripts

### Frontend
- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run lint` - Run linter

### Backend
- `python -m uvicorn main:app --reload` - Start development server
- `python -m py_compile $(find . -name "*.py")` - Compile all Python files

## 🔐 Authentication & Security

### Cookie-Based Authentication (Secure)

The application uses **HTTP-only cookie-based authentication** for maximum security:

**Security Features:**
- ✅ **XSS Protection**: Tokens stored in HTTP-only cookies (not accessible via JavaScript)
- ✅ **CSRF Protection**: SameSite=Lax cookie attribute prevents cross-site attacks
- ✅ **Short-Lived Tokens**: Access tokens expire in 15 minutes
- ✅ **Automatic Refresh**: Seamless token refresh every 14 minutes
- ✅ **Long-Lived Sessions**: Refresh tokens last 7 days for better UX

**Authentication Flow:**

1. **Registration/Login**
   - User submits credentials via custom-themed auth pages
   - Backend validates credentials and hashes passwords with bcrypt
   - Backend generates access token (15 min) and refresh token (7 days)
   - Backend sets HTTP-only cookies with security flags
   - Frontend receives user data (no tokens in response body)

2. **Authenticated Requests**
   - Browser automatically sends cookies with every request
   - Backend validates access token from cookie
   - No manual token handling required in frontend

3. **Token Refresh**
   - Frontend automatically refreshes token every 14 minutes
   - Refresh endpoint validates refresh token and issues new access token
   - Process is seamless and invisible to users

4. **Logout**
   - Backend clears both access and refresh token cookies
   - User is redirected to login page

**Cookie Configuration:**
```python
# Access Token Cookie
httponly=True      # Prevents JavaScript access (XSS protection)
secure=True        # HTTPS only in production
samesite="lax"     # CSRF protection
max_age=900        # 15 minutes
path="/"           # Available to all routes

# Refresh Token Cookie
httponly=True
secure=True
samesite="lax"
max_age=604800     # 7 days
path="/api/auth/refresh"  # Only sent to refresh endpoint
```

**Important Production Requirements:**
- ⚠️ **HTTPS is REQUIRED** in production for secure cookies to work
- ⚠️ Frontend and backend must have proper CORS configuration
- ⚠️ `ENVIRONMENT=production` must be set in backend to enable secure cookies

For detailed migration information, see [specs/009-better-auth-migration/AUTH_MIGRATION_GUIDE.md](./specs/009-better-auth-migration/AUTH_MIGRATION_GUIDE.md)

## 📊 Database Schema

The application uses PostgreSQL with the following main entities:

- **Users**: Stores user information (email, username, hashed password, profile data)
- **Tasks**: User's todo items (title, description, completion status)
- **Testimonials**: User reviews (name, email, rating, message)
- **Settings**: User preferences and settings (theme, notifications, privacy settings)

## 🚀 Deployment

### Production URLs

**Frontend (Vercel):**
- Production: https://ai-y-todo.vercel.app
- Local: http://localhost:3000 or http://localhost:3001

**Backend (Hugging Face Spaces):**
- Production: https://aliaskariface-backend-todo-app.hf.space
- Local: http://localhost:8000

### Deployment Instructions

#### Frontend Deployment (Vercel)

1. **Prepare Environment Variables**

Set the following in Vercel dashboard:
```env
NEXT_PUBLIC_API_BASE_URL=https://aliaskariface-backend-todo-app.hf.space
NEXT_PUBLIC_SITE_URL=https://ai-y-todo.vercel.app
NEXT_PUBLIC_DEBUG=false
NEXT_PUBLIC_VERBOSE_LOGGING=false
```

**Note:** No authentication secrets needed in frontend. Authentication is handled via HTTP-only cookies set by the backend.

2. **Deploy via Vercel CLI**
```bash
cd frontend
npm install -g vercel
vercel login
vercel --prod
```

Or connect your GitHub repository to Vercel for automatic deployments.

#### Backend Deployment (Hugging Face Spaces)

1. **Prepare Environment Variables**

Set the following in Hugging Face Spaces secrets:
```env
DATABASE_URL=<your-neon-postgresql-url>
SECRET_KEY=<your-secure-secret-key>
ENVIRONMENT=production
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
GROQ_API_KEY=<your-groq-api-key>
GROQ_MODEL=llama-3.3-70b-versatile
PORT=7860
DEBUG=false
LOG_LEVEL=info
ALLOWED_ORIGINS=https://ai-y-todo.vercel.app
ENABLE_RATE_LIMITING=true
RATE_LIMIT_PER_MINUTE=60
```

2. **Deploy to Hugging Face Spaces**
- Create a new Space with Docker SDK
- Upload backend code
- Configure secrets in Space settings
- Deploy

### Local Development

For local development, use the automated setup scripts:

**Windows:**
```bash
# Frontend
cd frontend
setup-local.bat

# Backend
cd backend
setup-local.bat
```

**macOS/Linux:**
```bash
# Frontend
cd frontend
chmod +x setup-local.sh
./setup-local.sh

# Backend
cd backend
chmod +x setup-local.sh
./setup-local.sh
```

## 🐳 Docker Compose Deployment

The application can be run locally using Docker Compose for quick testing and development.

> **📚 For comprehensive Docker documentation, see [docs/DOCKER_GUIDE.md](./docs/DOCKER_GUIDE.md)**
>
> The Docker Guide includes:
> - Complete command reference
> - Advanced usage and troubleshooting
> - Production deployment strategies
> - Health check scripts and monitoring
> - Container management best practices

### Prerequisites

- Docker 20.10+ (Docker Desktop recommended)
- Docker Compose 2.0+
- 4GB+ RAM available
- 10GB+ disk space

### Quick Start

```bash
# 1. Start the containers
docker-compose up -d

# 2. Verify containers are running and healthy
docker-compose ps

# 3. Run health checks (optional)
chmod +x scripts/health-check-docker.sh
./scripts/health-check-docker.sh

# 4. Access the application
# Frontend: http://localhost:3000
# Backend:  http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## ☸️ Kubernetes Deployment (Minikube)

Deploy the application to a local Kubernetes cluster using Minikube and Helm for a production-like environment.

> **📚 For comprehensive Kubernetes documentation, see:**
> - [docs/MINIKUBE_GUIDE.md](./docs/MINIKUBE_GUIDE.md) - Complete Minikube, Helm & Kubernetes guide
> - [docs/MINIKUBE_DEPLOYMENT.md](./docs/MINIKUBE_DEPLOYMENT.md) - Step-by-step deployment instructions
> - [docs/MINIKUBE_QUICK_REFERENCE.md](./docs/MINIKUBE_QUICK_REFERENCE.md) - Quick command reference
> - [docs/INGRESS_SETUP.md](./docs/INGRESS_SETUP.md) - Ingress configuration guide
> - [docs/DEPLOYMENT_COMPLETION_REPORT.md](./docs/DEPLOYMENT_COMPLETION_REPORT.md) - Deployment status

### Prerequisites

- Docker 20.10+ (with Docker Desktop recommended)
- Minikube 1.30+
- kubectl 1.27+
- Helm 3.12+
- 4GB+ RAM available for Minikube
- 20GB+ disk space

### Quick Start

```bash
# 1. Start Minikube cluster
minikube start --cpus=4 --memory=8192

# 2. Build Docker images
docker-compose build

# 3. Load images into Minikube
minikube image load ai-todo-frontend:latest
minikube image load ai-todo-backend:latest

# 4. Deploy with Helm
helm install ai-todo ./charts/ai-todo

# 5. Set up port forwarding
kubectl port-forward service/ai-todo-frontend 8080:80 &
kubectl port-forward service/backend-service 8000:8000 &

# 6. Access the application
# Frontend: http://localhost:8080
# Backend:  http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Deployment Status

**Current Deployment:**
- ✅ Minikube cluster running (192.168.49.2)
- ✅ Helm release: ai-todo v1.0.0 (revision 5)
- ✅ Pods: 3/3 running (2 frontend, 1 backend)
- ✅ Ingress: NGINX controller configured
- ✅ Monitoring: Metrics Server and Dashboard enabled
- ✅ Resource usage: 7% CPU, 33% Memory (optimal)

**Access Methods:**
1. **Port Forwarding** (Active): http://localhost:8080, http://localhost:8000
2. **NodePort**: http://192.168.49.2:31752
3. **Ingress**: http://ai-todo.local (requires tunnel and hosts file)

### Management Commands

```bash
# View pod status
kubectl get pods

# Check logs
kubectl logs -f <pod-name>

# Monitor resources
kubectl top pods

# Access Kubernetes Dashboard
minikube dashboard

# Upgrade deployment
helm upgrade ai-todo ./charts/ai-todo

# Uninstall
helm uninstall ai-todo
```

### Container Management

```bash
# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f frontend
docker-compose logs -f backend

# Restart services
docker-compose restart

# Stop containers
docker-compose down

# Rebuild and restart
docker-compose up -d --build
```

### Environment Configuration

The Docker Compose setup uses environment files:
- `frontend/.env.docker` - Frontend container configuration
- `backend/.env.docker` - Backend container configuration

These files are automatically loaded by Docker Compose. Make sure they contain the correct values for local development:

**Frontend (.env.docker):**
```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_SITE_URL=http://localhost:3000
BETTER_AUTH_SECRET=your-secret-key
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000
```

**Backend (.env.docker):**
```env
DATABASE_URL=your-database-url
BETTER_AUTH_SECRET=your-secret-key
JWT_SECRET=your-jwt-secret
GROQ_API_KEY=your-groq-api-key
HOST=0.0.0.0
PORT=8000
ALLOWED_ORIGINS=["http://localhost:3000"]
```

### Health Checks

Both containers include automated health checks:
- **Frontend**: Checks HTTP response on port 3000
- **Backend**: Checks `/health` endpoint on port 8000

View health status:
```bash
docker-compose ps

# Or run comprehensive health check
./scripts/health-check-docker.sh
```

### Troubleshooting

**Containers not starting:**
```bash
# Check logs for errors
docker-compose logs

# Rebuild images
docker-compose build --no-cache
docker-compose up -d
```

**Port conflicts:**
```bash
# Check if ports are in use
netstat -ano | findstr :3000  # Windows
netstat -ano | findstr :8000  # Windows
lsof -i :3000                 # Mac/Linux
lsof -i :8000                 # Mac/Linux

# Stop conflicting services or change ports in docker-compose.yml
```

**Frontend can't connect to backend:**
- Verify `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000` in frontend/.env
- Ensure backend container is healthy: `docker-compose ps`
- Check backend logs: `docker-compose logs backend`

## ☸️ Kubernetes Deployment

The application can be deployed to a local Kubernetes cluster using Minikube and Helm. This provides a production-like environment for testing and development.

### Prerequisites

Ensure you have the following installed:
- Docker 20.10+ (Docker Desktop recommended)
- Minikube 1.30+
- kubectl 1.27+
- Helm 3.12+

### Quick Start (Automated)

The fastest way to deploy is using the automated deployment script:

```bash
# 1. Start Minikube (if not already running)
minikube start --driver=docker --cpus=4 --memory=8192

# 2. Run the automated deployment script
./scripts/deploy.sh
```

This script will:
1. Build Docker images for frontend and backend
2. Load images into Minikube
3. Deploy the application using Helm
4. Run health checks
5. Display access information

**Access the application:**

**Method 1: Port Forward (Recommended for Windows)**
```bash
kubectl port-forward service/ai-todo-frontend 8080:80
# Access at: http://localhost:8080
```

**Method 2: Direct NodePort Access**
```bash
# Get the Minikube IP and NodePort
minikube ip
kubectl get service ai-todo-frontend -o jsonpath='{.spec.ports[0].nodePort}'

# Access at: http://<minikube-ip>:<node-port>
# Example: http://192.168.49.2:31752
```

**Method 3: Minikube Service (Opens browser automatically)**
```bash
minikube service ai-todo-frontend
```

### Manual Deployment Steps

If you prefer manual control or need to troubleshoot:

#### Step 1: Start Minikube

```bash
# Start Minikube with recommended resources
minikube start --driver=docker --cpus=4 --memory=8192

# Verify Minikube is running
minikube status
```

#### Step 2: Build Docker Images

```bash
# Build frontend image
cd frontend
docker build -t ai-todo-frontend:v1.0.0 .

# Build backend image
cd ../backend
docker build -t ai-todo-backend:v1.0.0 .

# Verify images
docker images | grep ai-todo
```

#### Step 3: Load Images into Minikube

```bash
# Load images into Minikube's Docker daemon
minikube image load ai-todo-frontend:v1.0.0
minikube image load ai-todo-backend:v1.0.0

# Verify images in Minikube
minikube image ls | grep ai-todo
```

#### Step 4: Configure Secrets

Create a Kubernetes secret with your environment variables:

```bash
# Copy the example file
cp .env.k8s.example .env.k8s

# Edit with your actual values
# Then create the secret
kubectl create secret generic ai-todo-secrets \
  --from-env-file=.env.k8s \
  --dry-run=client -o yaml | kubectl apply -f -
```

#### Step 5: Deploy with Helm

```bash
# Install the Helm chart
helm install ai-todo ./charts/ai-todo \
  --namespace default \
  --wait \
  --timeout 5m

# Or upgrade if already installed
helm upgrade ai-todo ./charts/ai-todo \
  --namespace default \
  --wait \
  --timeout 5m
```

#### Step 6: Verify Deployment

```bash
# Check pod status
kubectl get pods -l app.kubernetes.io/part-of=ai-todo

# Check services
kubectl get services -l app.kubernetes.io/part-of=ai-todo

# View logs
kubectl logs -l app.kubernetes.io/component=frontend --tail=50
kubectl logs -l app.kubernetes.io/component=backend --tail=50
```

### Configuration

The Helm chart can be customized via `charts/ai-todo/values.yaml`:

```yaml
# Example: Adjust resource limits
resources:
  frontend:
    requests:
      memory: "256Mi"
      cpu: "250m"
    limits:
      memory: "512Mi"
      cpu: "500m"
  backend:
    requests:
      memory: "512Mi"
      cpu: "500m"
    limits:
      memory: "1Gi"
      cpu: "1000m"

# Example: Change replica counts
replicaCount:
  frontend: 2
  backend: 1
```

### Useful Commands

```bash
# View all resources
kubectl get all -l app.kubernetes.io/part-of=ai-todo

# Port forward for local access
kubectl port-forward service/ai-todo-frontend 3000:80

# View detailed pod information
kubectl describe pod -l app.kubernetes.io/component=frontend

# Execute commands in a pod
kubectl exec -it <pod-name> -- /bin/sh

# View Helm release status
helm status ai-todo

# View Helm release history
helm history ai-todo

# Rollback to previous version
helm rollback ai-todo

# Uninstall the application
helm uninstall ai-todo
```

### Cleanup

To remove the deployment and free up resources:

```bash
# Using the cleanup script
./scripts/cleanup.sh

# Or manually
helm uninstall ai-todo
kubectl delete configmap -l app.kubernetes.io/part-of=ai-todo
kubectl delete secret -l app.kubernetes.io/part-of=ai-todo

# Stop Minikube (optional)
minikube stop

# Delete Minikube cluster (optional)
minikube delete
```

### Troubleshooting

**Pods not starting:**
```bash
# Check pod events
kubectl describe pod <pod-name>

# Check logs
kubectl logs <pod-name>

# Check if images are loaded
minikube image ls | grep ai-todo
```

**Cannot access application:**
```bash
# Verify service is running
kubectl get service ai-todo-frontend

# Get Minikube IP
minikube ip

# Check NodePort
kubectl get service ai-todo-frontend -o jsonpath='{.spec.ports[0].nodePort}'
```

**Image pull errors:**
```bash
# Ensure images are loaded into Minikube
./scripts/load-images.sh

# Verify imagePullPolicy is IfNotPresent
kubectl get deployment ai-todo-frontend -o yaml | grep imagePullPolicy
```

**Health check failures:**
```bash
# Run the health check script
./scripts/health-check.sh

# Check readiness probes
kubectl get pods -o wide
kubectl describe pod <pod-name> | grep -A 10 Readiness
```

For more detailed deployment instructions and troubleshooting, see:
- [Kubernetes Deployment Quickstart](specs/001-k8s-aiops-deployment/quickstart.md)
- [Feature Specification](specs/001-k8s-aiops-deployment/spec.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add some amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🐛 Issues & Support

If you encounter any issues or have questions, please file an issue in the repository.