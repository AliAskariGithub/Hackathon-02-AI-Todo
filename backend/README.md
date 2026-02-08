# Backend - AI Todo Application

FastAPI backend with PostgreSQL, JWT authentication, and AI-powered task management using MCP tools.

## 🚀 Features

### Core Features
- **FastAPI** - Modern, fast web framework for building APIs
- **SQLModel** - SQL databases with Python type annotations
- **PostgreSQL** - Production-ready database (Neon serverless)
- **JWT Authentication** - Secure token-based authentication
- **Async/Await** - Asynchronous request handling
- **OpenAPI Documentation** - Automatic API documentation

### AI Integration
- **MCP Tools** - Model Context Protocol for AI operations
- **GROQ API** - Fast AI inference with Llama 3.3 70B
- **Task Runner** - AI-powered task management and chat
- **Simple Language Mode** - Grade 6-8 reading level responses
- **Streaming Responses** - Real-time chat interactions

### API Features
- **RESTful Endpoints** - Standard REST API design
- **CORS Support** - Cross-origin resource sharing
- **Rate Limiting** - Configurable request throttling
- **Error Handling** - Comprehensive exception handling
- **Logging** - Structured logging with configurable levels

## 📋 Prerequisites

- Python 3.11 or higher
- PostgreSQL database (or Neon account)
- GROQ API key (for AI features)

## 🚀 Quick Start

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

1. **Create Virtual Environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure Environment**
```bash
# Copy environment template
cp .env.example .env.local

# Edit .env.local with your configuration
```

4. **Start Development Server**
```bash
# Using Python directly
python main.py

# Or using uvicorn
uvicorn main:app --reload --port 8001
```

The API will be available at:
- Primary: http://localhost:8001
- Alternative: http://localhost:8000
- API Docs: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

## 🔧 Environment Variables

Create `.env.local` for local development:

```env
# Database Configuration
DATABASE_URL=sqlite:///./ai_todo_dev.db
# Or for PostgreSQL:
# DATABASE_URL=postgresql://user:password@host:port/database

# Authentication
BETTER_AUTH_SECRET=your-secret-key-here
JWT_SECRET=your-jwt-secret-here
JWT_EXPIRATION_DELTA_MINUTES=30

# AI Configuration
GROQ_API_KEY=your-groq-api-key-here
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_BASE_URL=https://api.groq.com/openai/v1

# Server Configuration
HOST=0.0.0.0
PORT=8001
DEBUG=true
LOG_LEVEL=debug

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000,http://127.0.0.1:3001

# Rate Limiting
ENABLE_RATE_LIMITING=false
RATE_LIMIT_PER_MINUTE=100
```

For production, create `.env.production`:

```env
# Database Configuration (Neon PostgreSQL)
DATABASE_URL=postgresql://user:password@host:port/database?sslmode=require

# Authentication (must match frontend)
BETTER_AUTH_SECRET=<your-secure-production-key>
JWT_SECRET=<your-secure-jwt-key>
JWT_EXPIRATION_DELTA_MINUTES=30

# AI Configuration
GROQ_API_KEY=<your-groq-api-key>
GROQ_MODEL=llama-3.3-70b-versatile

# Server Configuration
HOST=0.0.0.0
PORT=7860
DEBUG=false
LOG_LEVEL=info

# CORS Configuration
ALLOWED_ORIGINS=https://ai-y-todo.vercel.app

# Rate Limiting
ENABLE_RATE_LIMITING=true
RATE_LIMIT_PER_MINUTE=60
```

**Important:**
- Generate secure keys: `openssl rand -base64 32`
- Never commit `.env.local` or `.env.production` to version control
- Ensure `BETTER_AUTH_SECRET` matches frontend configuration
- Get GROQ API key from: https://console.groq.com

## 📁 Project Structure

```
backend/
├── src/
│   ├── api/
│   │   ├── deps.py              # Dependency injection
│   │   └── routers/             # API endpoints
│   │       ├── analytics.py     # Analytics endpoints
│   │       ├── chat.py          # Chat/conversation endpoints
│   │       ├── mcp.py           # MCP tool endpoints
│   │       ├── tasks.py         # Task CRUD endpoints
│   │       ├── testimonials.py  # Testimonial endpoints
│   │       └── users.py         # User auth endpoints
│   ├── models/                  # SQLModel database models
│   │   ├── __init__.py
│   │   ├── conversation.py      # Chat conversation models
│   │   ├── message.py           # Chat message models
│   │   ├── task.py              # Task models
│   │   ├── testimonial.py       # Testimonial models
│   │   └── user.py              # User models
│   ├── services/                # Business logic
│   │   ├── chat_service.py      # Chat operations
│   │   ├── task_service.py      # Task operations
│   │   └── user_service.py      # User operations
│   ├── mcp/                     # MCP tools integration
│   │   ├─ runners/
│   │   │   └── task_runner.py   # AI task runner
│   │   └── tools/               # MCP tool definitions
│   ├── utils/                   # Utilities
│   │   ├── database.py          # Database connection
│   │   ├── db_utils.py          # Database utilities
│   │   ├── exception_handlers.py # Error handlers
│   │   └── logging_config.py    # Logging setup
│   └── config.py                # Configuration settings
├── main.py                      # Application entry point
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment template
├── .env.local                   # Local environment (gitignored)
├── .env.production              # Production environment (gitignored)
├── setup-local.sh               # Setup script (Unix)
└── setup-local.bat              # Setup script (Windows)
```

## 🔌 API Endpoints

### Health & Root
- `GET /` - Welcome message
- `GET /health` - Health check

### Authentication
- `POST /api/users/register` - Register new user
- `POST /api/users/login` - Login user
- `GET /api/users/me` - Get current user

### Tasks
- `GET /api/{user_id}/tasks` - List user tasks
- `POST /api/{user_id}/tasks` - Create task
- `GET /api/{user_id}/tasks/{task_id}` - Get task
- `PUT /api/{user_id}/tasks/{task_id}` - Update task
- `DELETE /api/{user_id}/tasks/{task_id}` - Delete task

### Chat
- `GET /api/{user_id}/conversations` - List conversations
- `POST /api/{user_id}/conversations` - Create conversation
- `GET /api/{user_id}/conversations/{conversation_id}` - Get conversation
- `POST /api/{user_id}/conversations/{conversation_id}/messages` - Send message
- `GET /api/{user_id}/conversations/{conversation_id}/messages` - Get messages

### MCP Tools
- `POST /api/mcp/execute-tool` - Execute MCP tool
- `GET /api/mcp/tools` - List available tools

### Testimonials
- `GET /api/testimonials` - List testimonials
- `POST /api/testimonials` - Create testimonial

### Analytics
- `GET /api/{user_id}/analytics` - Get user analytics

## 🗄️ Database

### SQLite (Development)
```env
DATABASE_URL=sqlite:///./ai_todo_dev.db
```

### PostgreSQL (Production)
```env
DATABASE_URL=postgresql://user:password@host:port/database?sslmode=require
```

### Neon Serverless PostgreSQL (Recommended)
1. Create account at https://neon.tech
2. Create a new project
3. Copy connection string
4. Add to `.env.production`

### Database Models
- **User**: Authentication and profile
- **Task**: Todo items with status
- **Conversation**: Chat conversations
- **Message**: Chat messages
- **Testimonial**: User testimonials

## 🤖 AI Integration

### GROQ API Setup
1. Get API key from https://console.groq.com
2. Add to environment variables
3. Configure model (default: llama-3.3-70b-versatile)

### MCP Tools
The backend includes MCP (Model Context Protocol) tools for:
- Task creation and management
- Task querying and filtering
- Natural language task operations
- Simple language responses (grade 6-8 level)

### Task Runner
Located in `src/mcp/runners/task_runner.py`:
- Processes natural language requests
- Executes MCP tools
- Returns simple, conversational responses
- Supports streaming for real-time chat

## 🔐 Authentication

### JWT Token Flow
1. User registers or logs in
2. Backend generates JWT token
3. Token includes user ID and expiration
4. Frontend stores token in localStorage
5. Token sent in Authorization header
6. Backend validates token on protected routes

### Password Security
- Passwords hashed with bcrypt
- Salt rounds: 12
- Never stored in plain text

## 🚀 Deployment

### Hugging Face Spaces (Recommended)

1. **Create Space**
   - Go to https://huggingface.co/spaces
   - Create new Space with Docker SDK
   - Name: backend-todo-app

2. **Configure Secrets**
   Add environment variables in Space settings:
   ```env
   DATABASE_URL=<neon-postgresql-url>
   BETTER_AUTH_SECRET=<production-secret>
   JWT_SECRET=<production-jwt-secret>
   GROQ_API_KEY=<groq-api-key>
   PORT=7860
   DEBUG=false
   ALLOWED_ORIGINS=https://ai-y-todo.vercel.app
   ENABLE_RATE_LIMITING=true
   ```

3. **Create Dockerfile**
   ```dockerfile
   FROM python:3.11-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   COPY . .
   EXPOSE 7860
   CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
   ```

4. **Deploy**
   - Push code to Space repository
   - Space will automatically build and deploy

### Manual Deployment

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Environment Variables**
   ```bash
   export DATABASE_URL=<your-database-url>
   export BETTER_AUTH_SECRET=<your-secret>
   # ... other variables
   ```

3. **Run with Gunicorn**
   ```bash
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001
   ```

## 🧪 Testing

### Run Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest

# Run with coverage
pytest --cov=src tests/
```

### Manual API Testing
```bash
# Health check
curl http://localhost:8001/health

# Register user
curl -X POST http://localhost:8001/api/users/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","username":"testuser","password":"password123"}'

# Login
curl -X POST http://localhost:8001/api/users/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"password123"}'
```

## 🐛 Troubleshooting

### Database Connection Issues
```bash
# Check database URL format
echo $DATABASE_URL

# Test connection
python -c "from src.utils.database import engine; print(engine)"
```

### Port Already in Use
```bash
# Find process using port 8001
# Windows
netstat -ano | findstr :8001

# macOS/Linux
lsof -i :8001

# Kill process or use different port
uvicorn main:app --reload --port 8002
```

### Import Errors
```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt

# Check Python version
python --version  # Should be 3.11+
```

### CORS Errors
- Verify `ALLOWED_ORIGINS` includes frontend URL
- Check frontend is sending requests to correct backend URL
- Ensure CORS middleware is configured in `main.py`

## 📚 Documentation

- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com)
- [Pydantic Documentation](https://docs.pydantic.dev)
- [Uvicorn Documentation](https://www.uvicorn.org)
- [GROQ API Documentation](https://console.groq.com/docs)

## 🔧 Development

### Code Style
```bash
# Format code
black src/

# Sort imports
isort src/

# Lint
flake8 src/
```

### Database Migrations
```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Write tests
4. Run linting and tests
5. Submit a pull request

## 📄 License

MIT License - See LICENSE file for details

## 🔗 Related

- Frontend: `../frontend/README.md`
- Main README: `../README.md`
- Environment Setup: `../ENVIRONMENT_SETUP.md`
- Testing Guide: `../TESTING_GUIDE.md`
