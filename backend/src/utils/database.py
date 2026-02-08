from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator
from fastapi import Depends
from ..config import settings
import asyncio
import urllib.parse
import logging

# Global variables to hold the engine and session factory to avoid recreating them
_async_engine = None
_async_session_factory = None


def process_database_url(original_url: str) -> str:
    """
    Process the database URL to ensure compatibility with async drivers.
    Removes incompatible parameters for asyncpg and SQLite.
    """
    processed_url = original_url

    if "postgresql" in original_url:
        # Replace psycopg2 driver with asyncpg driver if present
        if "+psycopg2" in original_url:
            processed_url = original_url.replace("+psycopg2", "+asyncpg")
        elif "postgresql://" in original_url and "+asyncpg" not in original_url:
            # If it's a plain postgresql URL without a driver, add asyncpg
            processed_url = original_url.replace("postgresql://", "postgresql+asyncpg://")

        # For Neon/asyncpg, we need to handle query parameters carefully
        # Parse the URL to manipulate query parameters
        parsed = urllib.parse.urlparse(processed_url)

        # Parse the query parameters
        query_params = urllib.parse.parse_qs(parsed.query)

        # For asyncpg, we need to remove incompatible parameters
        allowed_params = {}
        for key, value_list in query_params.items():
            # Remove channel_binding and sslmode which can cause issues with asyncpg
            if key not in ['channel_binding', 'sslmode']:
                # Take the first value for each parameter (since parse_qs returns lists)
                allowed_params[key] = value_list[0] if value_list else ''

        # Rebuild the query string with only compatible parameters
        new_query = urllib.parse.urlencode(allowed_params)

        # Reconstruct the URL with filtered parameters
        processed_url = urllib.parse.urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            new_query,
            parsed.fragment
        ))

        return processed_url

    elif "sqlite" in original_url:
        # For SQLite, use the async SQLite driver
        # For SQLite async operations, we need to use aiosqlite
        if not original_url.startswith("sqlite+aiosqlite"):
            processed_url = original_url.replace("sqlite:///", "sqlite+aiosqlite:///")

        return processed_url
    else:
        # For other database types, return as-is
        return original_url


def get_async_engine():
    global _async_engine
    if _async_engine is None:
        db_url = process_database_url(settings.database_url)

        # Different connection parameters for different database types
        if "postgresql" in db_url:
            # PostgreSQL-specific parameters
            _async_engine = create_async_engine(
                db_url,
                echo=False,
                # For Neon PostgreSQL, ensure proper connection handling
                pool_pre_ping=True,
                pool_recycle=300,  # Recycle connections every 5 minutes
                pool_timeout=30,   # Increase timeout
                max_overflow=0,    # Limit overflow connections for serverless
                pool_size=5,       # Smaller pool for serverless
                connect_args={
                    "server_settings": {
                        "application_name": "ai-todo-app",
                    },
                }
            )
        else:
            # For other database types, return as-is (default case)
            _async_engine = create_async_engine(
                db_url,
                echo=False,
                # For other databases, use standard parameters
                pool_pre_ping=True,
                pool_recycle=300
            )
    return _async_engine


def get_async_session_factory():
    global _async_session_factory
    # Always use the current engine (which may have been recreated with new URL processing)
    engine = get_async_engine()
    if _async_session_factory is None:
        _async_session_factory = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    # Update the session factory in case engine has changed
    _async_session_factory.configure(bind=engine)
    return _async_session_factory


# Create a dependency that gets the session
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Async generator dependency for database sessions."""
    async with get_async_session_factory()() as session:
        try:
            yield session
        finally:
            await session.close()


