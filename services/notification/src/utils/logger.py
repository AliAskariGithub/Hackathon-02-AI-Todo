"""
Structured logging utility for Notification Service.

Provides consistent JSON-formatted logging across the microservice with
correlation ID tracking and contextual information.
"""

import logging
import json
import sys
from datetime import datetime
from typing import Any, Dict, Optional
from contextvars import ContextVar

# Context variable for correlation ID tracking
correlation_id_var: ContextVar[Optional[str]] = ContextVar('correlation_id', default=None)


class StructuredFormatter(logging.Formatter):
    """
    Custom formatter that outputs logs in JSON format for structured logging.

    Includes:
    - Timestamp (ISO 8601)
    - Log level
    - Service name
    - Correlation ID (if available)
    - Message
    - Additional context fields
    """

    def __init__(self, service_name: str = "notification-service"):
        super().__init__()
        self.service_name = service_name

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON string."""
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "service": self.service_name,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add correlation ID if available
        correlation_id = correlation_id_var.get()
        if correlation_id:
            log_data["correlation_id"] = correlation_id

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields from record
        if hasattr(record, 'extra_fields'):
            log_data.update(record.extra_fields)

        return json.dumps(log_data)


def setup_logging(
    service_name: str = "notification-service",
    level: str = "INFO",
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Configure structured logging for the service.

    Args:
        service_name: Name of the service for log identification
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for log output (in addition to stdout)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(service_name)
    logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers
    logger.handlers.clear()

    # Console handler with structured formatter
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(StructuredFormatter(service_name))
    logger.addHandler(console_handler)

    # Optional file handler
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(StructuredFormatter(service_name))
        logger.addHandler(file_handler)

    return logger


def set_correlation_id(correlation_id: str) -> None:
    """Set correlation ID for current context."""
    correlation_id_var.set(correlation_id)


def get_correlation_id() -> Optional[str]:
    """Get correlation ID from current context."""
    return correlation_id_var.get()


def log_with_context(
    logger: logging.Logger,
    level: str,
    message: str,
    **extra_fields: Any
) -> None:
    """
    Log message with additional context fields.

    Args:
        logger: Logger instance
        level: Log level (debug, info, warning, error, critical)
        message: Log message
        **extra_fields: Additional fields to include in log
    """
    log_method = getattr(logger, level.lower())

    # Create a log record with extra fields
    extra = {'extra_fields': extra_fields}
    log_method(message, extra=extra)


# Example usage:
if __name__ == "__main__":
    # Setup logger
    logger = setup_logging("notification-service", "DEBUG")

    # Set correlation ID
    set_correlation_id("test-correlation-123")

    # Log with context
    log_with_context(
        logger,
        "info",
        "Processing reminder notification",
        reminder_id="reminder-456",
        user_id="user-789",
        scheduled_time="2024-02-14T10:00:00Z"
    )

    # Standard logging
    logger.info("Service started successfully")
    logger.warning("High memory usage detected")
    logger.error("Failed to send notification")
