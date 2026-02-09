from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from pathlib import Path
from src.api.routers.tasks import router as tasks_router
from src.api.routers.testimonials import router as testimonials_router
from src.api.routers.users import router as users_router
from src.api.routers.analytics import router as analytics_router
from src.api.routers.mcp import router as mcp_router
from src.api.routers.chat import router as chat_router
from src.api.routers.auth import router as auth_router
from src.utils.db_utils import create_tables
from src.utils.logging_config import setup_logging
from src.utils.exception_handlers import (
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler
)
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError

# Load environment variables from .env file with explicit path
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

# Get configuration from environment variables
DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000').split(',')
PORT = int(os.getenv('PORT', '8000'))
HOST = os.getenv('HOST', '0.0.0.0')

# Debug logging (only in development)
if DEBUG:
    print(f"DEBUG: Loaded .env from {env_path}")
    print(f"DEBUG: GROQ_API_KEY = {os.getenv('GROQ_API_KEY', 'NOT FOUND')[:30]}...")
    print(f"DEBUG: ALLOWED_ORIGINS = {ALLOWED_ORIGINS}")
    print(f"DEBUG: PORT = {PORT}")
    print(f"DEBUG: HOST = {HOST}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    setup_logging()
    try:
        # Attempt to create tables, but don't fail if database is unavailable
        create_tables()
    except Exception as e:
        print(f"Warning: Could not initialize database at startup: {e}")
        print("Application will continue without database initialization")
    yield


app = FastAPI(
    title="Todo Backend API",
    description="A multi-user todo application backend with FastAPI and SQLModel",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware for frontend/backend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # Use environment variable
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # Expose authorization header to allow JWT tokens to be passed
    expose_headers=["Access-Control-Allow-Origin", "Authorization"]
)

# Register exception handlers
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)


# Include the routers
app.include_router(auth_router)  # Auth router (login, logout, refresh)
app.include_router(tasks_router)
app.include_router(testimonials_router)
app.include_router(users_router)
app.include_router(analytics_router)
app.include_router(mcp_router)
app.include_router(chat_router)


@app.get("/")
def read_root():
    return {"message": "Welcome to the Todo Backend API"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


# For running with uvicorn
if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT, reload=DEBUG)
