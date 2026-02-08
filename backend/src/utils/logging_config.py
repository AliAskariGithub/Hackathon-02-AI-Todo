import logging
from ..config import settings


def setup_logging():
    """Configure logging for the application."""
    logging.basicConfig(
        level=settings.log_level.upper(),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name."""
    return logging.getLogger(name)