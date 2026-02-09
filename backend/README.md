# AI Todo - Backend

FastAPI backend for the AI Todo application with authentication, task management, and AI-powered chat.

## 🚀 Tech Stack

- **Framework**: FastAPI
- **Language**: Python 3.11+
- **Database**: PostgreSQL (Neon serverless)
- **ORM**: SQLModel
- **Authentication**: JWT tokens
- **Password Hashing**: bcrypt
- **AI Integration**: Groq API (Llama 3.3 70B)
- **Validation**: Pydantic
- **ASGI Server**: Uvicorn

## 📋 Prerequisites

- Python 3.11 or higher
- PostgreSQL database (or Neon account)
- Groq API key (for AI features)

## 🛠️ Setup

### Automated Setup (Recommended)

**Windows:**
```bash
setup-local.bat
```

**macOS/Linux:**
```bash
chmod +x setup-local.sh
./setup-local.sh
```

### Manual Setup

1. **Create virtual environment:**
```bash
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure environment:**
```bash
# Copy environment template
cp .env.example .env.local

# Edit .env.local with your configuration
```

4. **Environment variables:**
```env
# Database
DATABASE_URL=postgresql://user:password@host:5432/database
# Or for local SQLite:
# DATABASE_URL=sqlite:///./ai_todo_dev.db

# Authentication & Security
SECRET_KEY=your-secret-key-here
JWT_SECRET=your-jwt-secret-here
ENVIRONMENT=development
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# AI Configuration
GROQ_API_KEY=your-groq-api-key-here
GROQ_MODEL=llama-3.3-70b-versatile

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=true
LOG_LEVEL=debug

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080

# Rate Limiting (optional)
ENABLE_RATE_LIMITING=false
RATE_LIMIT_PER_MINUTE=60
```

5. **Start development server:**
```bash
python main.py
# Or with uvicorn directly:
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Access at:**
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- OpenAPI Spec: http://localhost:8000/openapi.json

## 🏗️ Project Structure

```
backend/
├── src/
│   ├── api/                    # API routes
│   │   ├── routers/           # Route handlers
│   │   │   ├── auth.py        # Authentication endpoints
│   │   │   ├── users.py       # User management
│   │   │   ├── tasks.py       # Task CRUD operations
│   │   │   ├── testimonials.py # Testimonials
│   │   │   ├── analytics.py   # Analytics endpoints
│   │   │   └── chat.py        # AI chat interface
│   │   └── dependencies.py    # Dependency injection
│   ├── config.py              # Configuration management
│   ├── database.py            # Database connection
│   ├── models.py              # SQLModel models
│   ├── schemas.py             # Pydantic schemas
│   ├── auth.py                # Authentication logic
│   ├── mcp/                   # Model Context Protocol
│   │   ├── agents/           # AI agents
│   │   │   └── todo_agent.py # Task management agent
│   │   └── runners/          # Task runners
│   │       └── task_runner.py
│   └── utils/                # Utility functions
├── tests/                    # Test files
├── .env.example             # Environment template
├── requirements.txt         # Python dependencies
├── Dockerfile              # Docker configuration
└── main.py                 # Application entry point
```

## 📡 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/refresh` - Refresh access token
- `POST /api/auth/logout` - Logout user
- `GET /api/auth/session` - Get current session

### Users
- `GET /api/users/me` - Get current user
- `PUT /api/users/me` - Update current user
- `DELETE /api/users/me` - Delete current user

### Tasks
- `GET /api/tasks` - List all tasks
- `POST /api/tasks` - Create new task
- `GET /api/tasks/{id}` - Get task by ID
- `PUT /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task
- `PATCH /api/tasks/{id}/complete` - Mark task as complete

### Chat
- `POST /api/chat` - Send chat message (streaming)
- `GET /api/chat/history` - Get chat history

### Testimonials
- `GET /api/testimonials` - List testimonials
- `POST /api/testimonials` - Create testimonial
- `GET /api/testimonials/{id}` - Get testimonial by ID

### Analytics
- `GET /api/analytics/stats` - Get application statistics
- `GET /health` - Health check endpoint

## 🔐 Authentication

### JWT Token Flow

1. **Registration/Login**: User provides credentials
2. **Token Generation**: Server generates access token (15 min) and refresh token (7 days)
3. **Token Storage**: Tokens stored in HTTP-only cookies
4. **Token Refresh**: Automatic refresh before expiration
5. **Token Validation**: Middleware validates tokens on protected routes

### Security Features

- **Password Hashing**: bcrypt with salt rounds
- **HTTP-Only Cookies**: XSS protection
- **CSRF Protection**: SameSite cookie attribute
- **Token Expiration**: Short-lived access tokens
- **Refresh Tokens**: Long-lived for seamless UX

## 🤖 AI Integration

### Groq API Configuration

The backend uses Groq's Llama 3.3 70B model for AI-powered chat:

```python
# Configuration
GROQ_API_KEY=your-api-key
GROQ_MODEL=llama-3.3-70b-versatile
```

### Chat Features

- **Natural Language Processing**: Understand user intent
- **Task Management**: Create, update, delete tasks via chat
- **Simple Language Mode**: Grade 6-8 reading level responses
- **Streaming Responses**: Real-time message delivery
- **Context Awareness**: Maintains conversation context

## 🗄️ Database

### Models

**User:**
```python
- id: UUID (primary key)
- email: str (unique)
- user_name: str (unique)
- hashed_password: str
- created_at: datetime
- updated_at: datetime
```

**Task:**
```python
- id: UUID (primary key)
- user_id: UUID (foreign key)
- title: str
- description: str (optional)
- completed: bool
- created_at: datetime
- updated_at: datetime
```

**Testimonial:**
```python
- id: UUID (primary key)
- name: str
- email: str
- rating: int (1-5)
- message: str
- created_at: datetime
```

### Migrations

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## 🐳 Docker Deployment

### Build Docker Image
```bash
docker build -t ai-todo-backend:latest .
```

### Run Container
```bash
docker run -p 8000:8000 \
  -e DATABASE_URL=your-database-url \
  -e SECRET_KEY=your-secret-key \
  -e GROQ_API_KEY=your-groq-api-key \
  ai-todo-backend:latest
```

### Docker Compose
```bash
# From project root
docker-compose up backend
```

## ☸️ Kubernetes Deployment

### Using Helm
```bash
# From project root
helm install ai-todo ./charts/ai-todo
```

### Access via Port Forward
```bash
kubectl port-forward service/backend-service 8000:8000
# Access at: http://localhost:8000
```

### Configuration

Kubernetes secrets and configmaps are managed via Helm:
- Database URL stored in secrets
- API keys stored in secrets
- CORS origins in configmap
- Server settings in configmap

## 🧪 Testing

### Run Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_auth.py

# Run with verbose output
pytest -v
```

### Test Coverage

- Authentication endpoints
- User CRUD operations
- Task management
- Database operations
- AI chat integration

## 🔍 Troubleshooting

### Common Issues

**Database connection errors:**
```bash
# Verify DATABASE_URL is correct
echo $DATABASE_URL

# Test connection
python -c "from src.database import engine; engine.connect()"

# Check PostgreSQL is running
pg_isready -h localhost -p 5432
```

**Import errors:**
```bash
# Ensure virtual environment is activated
which python  # Should point to venv

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**Port already in use:**
```bash
# Find process using port 8000
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # Mac/Linux

# Kill process or use different port
PORT=8001 python main.py
```

**CORS errors:**
- Verify `ALLOWED_ORIGINS` includes frontend URL
- Check frontend is using correct API URL
- Ensure credentials are included in requests

**AI chat not working:**
- Verify `GROQ_API_KEY` is valid
- Check Groq API status
- Review logs for API errors
- Verify model name is correct

## 📊 Monitoring

### Health Checks
```bash
# Check API health
curl http://localhost:8000/health

# Check database connection
curl http://localhost:8000/api/analytics/stats
```

### Logging

Logs are written to stdout with configurable levels:
- `DEBUG`: Detailed information
- `INFO`: General information
- `WARNING`: Warning messages
- `ERROR`: Error messages
- `CRITICAL`: Critical issues

Configure via `LOG_LEVEL` environment variable.

## 📚 Documentation

- **Main README**: [../README.md](../README.md)
- **API Documentation**: http://localhost:8000/docs (when running)
- **Environment Setup**: [../ENVIRONMENT_SETUP.md](../ENVIRONMENT_SETUP.md)
- **Docker Guide**: [../docs/DOCKER_GUIDE.md](../docs/DOCKER_GUIDE.md)
- **Kubernetes Guide**: [../docs/MINIKUBE_GUIDE.md](../docs/MINIKUBE_GUIDE.md)

## 🤝 Contributing

1. Follow PEP 8 style guide
2. Add type hints to all functions
3. Write docstrings for classes and functions
4. Add tests for new features
5. Update API documentation
6. Handle errors gracefully
7. Log important events

## 📄 License

See [../LICENSE](../LICENSE) for details.

---

**Built with ❤️ using FastAPI**
