from sqlmodel import SQLModel
import logging


logger = logging.getLogger(__name__)


def create_tables():
    """Create all database tables on startup."""
    try:
        # Import sync_engine here to handle potential initialization errors
        from .sync_database import sync_engine

        logger.info("Creating database tables...")
        # Try to create tables, but don't fail if DB is not available
        SQLModel.metadata.create_all(bind=sync_engine)
        logger.info("Database tables created successfully.")
    except Exception as e:
        logger.warning(f"Could not create database tables at startup: {str(e)}")
        logger.info("Application will continue without database initialization.")