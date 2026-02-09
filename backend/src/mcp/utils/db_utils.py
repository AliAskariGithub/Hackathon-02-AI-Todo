"""
Database utilities for MCP tools.
Provides safe database access patterns for async operations.
"""
from contextlib import asynccontextmanager
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator
import asyncio
from ..utils.database import get_async_session_factory


@asynccontextmanager
async def get_db_session():
    """
    Context manager to get a database session for MCP tools.
    This properly handles the async session lifecycle.

    Yields:
        AsyncSession: Database session for use in operations
    """
    session_factory = get_async_session_factory()
    async with session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


async def run_in_db_session(func, *args, **kwargs):
    """
    Run a function with a database session.

    Args:
        func: Async function to run with a database session
        *args: Arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function

    Returns:
        Result of the function execution
    """
    async with get_db_session() as session:
        return await func(session, *args, **kwargs)