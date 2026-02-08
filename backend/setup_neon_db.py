"""
Script to set up the Neon PostgreSQL database with the required tables.
This script creates the necessary tables for users, tasks, and testimonials.
"""

from sqlmodel import SQLModel
from sqlalchemy import create_engine
from src.models import User, Task, Testimonial
from src.config import settings
import urllib.parse


def create_tables():
    """Create all database tables."""
    print("Setting up Neon PostgreSQL database...")

    # Prepare the database URL for sync operations (same as in sync_database.py)
    original_url = settings.database_url
    if "postgresql" in original_url:
        # Replace postgresql+asyncpg:// with postgresql+psycopg2:// for sync operations
        sync_db_url = original_url.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
        # Handle case where it might be just postgresql://
        if sync_db_url == original_url:  # No replacement happened
            sync_db_url = original_url.replace("postgresql://", "postgresql+psycopg2://")

        # Parse the URL to handle query parameters properly
        parsed = urllib.parse.urlparse(sync_db_url)

        # Remove problematic query parameters for psycopg2
        query_params = urllib.parse.parse_qs(parsed.query)

        # Keep only parameters that are compatible with psycopg2
        allowed_params = {}
        for key, value_list in query_params.items():
            # For psycopg2, keep sslmode but remove channel_binding which may cause issues
            if key not in ['channel_binding']:
                # Take first value from the list
                allowed_params[key] = value_list[0] if value_list else ''

        new_query = urllib.parse.urlencode(allowed_params)
        sync_db_url = urllib.parse.urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            new_query,
            parsed.fragment
        ))

        sync_engine = create_engine(sync_db_url)
    elif "sqlite" in original_url:
        sync_engine = create_engine(original_url, connect_args={"check_same_thread": False})
    else:
        sync_engine = create_engine(original_url)

    try:
        # Create all tables
        SQLModel.metadata.create_all(bind=sync_engine)

        print("Database tables created successfully!")
        print("- User table")
        print("- Task table")
        print("- Testimonial table")

    except Exception as e:
        print(f"Error creating tables: {e}")
        raise
    finally:
        sync_engine.dispose()


if __name__ == "__main__":
    create_tables()