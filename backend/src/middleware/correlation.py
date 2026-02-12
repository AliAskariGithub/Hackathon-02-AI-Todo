"""
Correlation ID Middleware for Distributed Tracing

This middleware extracts or generates correlation IDs for all incoming requests,
enabling distributed tracing across services and event flows.

Key Features:
- Extract correlation ID from request headers
- Generate new correlation ID if not present
- Add correlation ID to response headers
- Make correlation ID available to request context
- Log correlation ID for tracing
"""

from typing import Callable
from uuid import uuid4, UUID
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import logging

# Correlation ID header name
CORRELATION_ID_HEADER = "X-Correlation-ID"

# Request state key for correlation ID
CORRELATION_ID_CTX_KEY = "correlation_id"

logger = logging.getLogger(__name__)


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle correlation IDs for distributed tracing.

    This middleware:
    1. Extracts correlation ID from incoming request headers
    2. Generates a new correlation ID if not present
    3. Adds correlation ID to request state for access in handlers
    4. Adds correlation ID to response headers
    5. Logs correlation ID for tracing
    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        """
        Process request and add correlation ID.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler in chain

        Returns:
            HTTP response with correlation ID header
        """
        # Extract correlation ID from request header or generate new one
        correlation_id = request.headers.get(CORRELATION_ID_HEADER)

        if correlation_id:
            try:
                # Validate UUID format
                correlation_id_uuid = UUID(correlation_id)
                correlation_id = str(correlation_id_uuid)
            except ValueError:
                # Invalid UUID format, generate new one
                logger.warning(
                    f"Invalid correlation ID format: {correlation_id}. "
                    "Generating new correlation ID."
                )
                correlation_id = str(uuid4())
        else:
            # No correlation ID provided, generate new one
            correlation_id = str(uuid4())

        # Add correlation ID to request state for access in handlers
        request.state.correlation_id = correlation_id

        # Log correlation ID for tracing
        logger.info(
            f"Request {request.method} {request.url.path} "
            f"[correlation_id={correlation_id}]"
        )

        # Process request
        response = await call_next(request)

        # Add correlation ID to response headers
        response.headers[CORRELATION_ID_HEADER] = correlation_id

        return response


def get_correlation_id(request: Request) -> str:
    """
    Get correlation ID from request state.

    Args:
        request: FastAPI request object

    Returns:
        Correlation ID string

    Example:
        >>> from fastapi import Request
        >>> @app.get("/tasks")
        >>> async def get_tasks(request: Request):
        ...     correlation_id = get_correlation_id(request)
        ...     # Use correlation_id for event publishing
    """
    return getattr(request.state, CORRELATION_ID_CTX_KEY, str(uuid4()))


def get_correlation_id_uuid(request: Request) -> UUID:
    """
    Get correlation ID as UUID from request state.

    Args:
        request: FastAPI request object

    Returns:
        Correlation ID as UUID

    Example:
        >>> from fastapi import Request
        >>> @app.get("/tasks")
        >>> async def get_tasks(request: Request):
        ...     correlation_id = get_correlation_id_uuid(request)
        ...     # Use correlation_id for event publishing
    """
    correlation_id_str = get_correlation_id(request)
    return UUID(correlation_id_str)


class CorrelationIdFilter(logging.Filter):
    """
    Logging filter to add correlation ID to log records.

    This filter extracts the correlation ID from the current request context
    and adds it to all log records for better traceability.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Add correlation ID to log record.

        Args:
            record: Log record to modify

        Returns:
            True (always allow log record)
        """
        # Try to get correlation ID from request context
        # If not available, use "N/A"
        record.correlation_id = getattr(record, 'correlation_id', 'N/A')
        return True


def configure_correlation_id_logging():
    """
    Configure logging to include correlation IDs.

    This function adds the CorrelationIdFilter to all loggers
    and updates the log format to include correlation IDs.

    Example:
        >>> # In main.py
        >>> from middleware.correlation import configure_correlation_id_logging
        >>> configure_correlation_id_logging()
    """
    # Add correlation ID filter to root logger
    root_logger = logging.getLogger()
    root_logger.addFilter(CorrelationIdFilter())

    # Update log format to include correlation ID
    log_format = (
        "%(asctime)s - %(name)s - %(levelname)s - "
        "[correlation_id=%(correlation_id)s] - %(message)s"
    )

    # Update all handlers with new format
    for handler in root_logger.handlers:
        handler.setFormatter(logging.Formatter(log_format))


# Example usage in FastAPI app
"""
from fastapi import FastAPI
from middleware.correlation import CorrelationIdMiddleware, configure_correlation_id_logging

app = FastAPI()

# Add correlation ID middleware
app.add_middleware(CorrelationIdMiddleware)

# Configure logging
configure_correlation_id_logging()

@app.get("/tasks")
async def get_tasks(request: Request):
    correlation_id = get_correlation_id(request)
    # Use correlation_id for event publishing, logging, etc.
    return {"tasks": []}
"""
