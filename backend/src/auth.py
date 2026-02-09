from better_auth import auth
from better_auth.oauth2 import google, github
from better_auth.database import get_db
from better_auth.models import User
from better_auth.types import BetterAuthOptions
from better_auth.fastapi_integration import BetterAuthFastAPI
import os
from typing import Optional
from sqlmodel import SQLModel, Field, create_engine, Session
from contextlib import asynccontextmanager
from fastapi import FastAPI
import asyncio


# Better Auth configuration
auth_options = BetterAuthOptions(
    secret=os.getenv("BETTER_AUTH_SECRET", "your-super-secret-key-change-this-in-production"),
    base_url=os.getenv("BETTER_AUTH_URL", "http://localhost:8000"),
    database_url=os.getenv("DATABASE_URL"),
    email_password={
        "enabled": True,
        "require_verification": False
    },
    oauth_providers={
        "google": google,
        "github": github
    }
)

# Initialize Better Auth
better_auth = auth(auth_options)

# Create the FastAPI integration
better_auth_fastapi = BetterAuthFastAPI(better_auth)