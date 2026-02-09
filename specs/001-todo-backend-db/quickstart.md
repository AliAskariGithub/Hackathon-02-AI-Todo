# Quickstart Guide: Todo Backend & Database

## Project Setup

### Prerequisites
- Python 3.11+
- Poetry or pip for dependency management
- Access to Neon Serverless PostgreSQL database

### Environment Configuration
1. Create `.env` file in project root
2. Add your Neon PostgreSQL connection string:
   ```
   DATABASE_URL=postgresql://username:password@ep-xxxxxx.us-east-1.aws.neon.tech/dbname?sslmode=require
   ```

### Installation
```bash
# Install dependencies
poetry install
# or
pip install -r requirements.txt

# Run the application
uvicorn main:app --reload
```

## Key Components

### Database Models
- `Task`: Core task entity with user ownership
- `User`: User stub model for future authentication

### Database Session Management
- Async dependency for database sessions
- Automatic cleanup of connections
- Proper error handling for transaction safety

### API Endpoints
- `/api/{user_id}/tasks`: Full CRUD operations
- Built with FastAPI for automatic OpenAPI documentation
- Pydantic models for request/response validation

## Running Tests
```bash
# Run unit tests
pytest

# Run integration tests
pytest tests/integration/

# Check code quality
mypy .
flake8 .
black --check .
```

## Development Workflow

1. **Database Setup**: Tables auto-created on startup
2. **API Development**: Add endpoints to the tasks router
3. **Testing**: Validate user isolation and CRUD operations
4. **Validation**: Ensure all endpoints return correct status codes

## Next Steps

1. Implement the API endpoints following the contract
2. Add proper error handling and validation
3. Set up testing for user isolation
4. Prepare for authentication integration (Spec 2)