"""
Prometheus metrics utility for Recurring Task Service.

Provides standardized metrics collection and exposure for monitoring:
- Request counters
- Request duration histograms
- Event processing metrics
- Task creation metrics
- Recurrence calculation metrics
"""

from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
from typing import Callable
import time
from functools import wraps

# HTTP Request Metrics
http_requests_total = Counter(
    'recurring_service_http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'recurring_service_http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

# Event Processing Metrics
events_processed_total = Counter(
    'recurring_service_events_processed_total',
    'Total events processed',
    ['event_type', 'status']
)

event_processing_duration_seconds = Histogram(
    'recurring_service_event_processing_duration_seconds',
    'Event processing duration in seconds',
    ['event_type']
)

# Recurring Task Metrics
recurring_tasks_created_total = Counter(
    'recurring_service_tasks_created_total',
    'Total recurring task instances created',
    ['recurrence_type', 'status']
)

recurrence_calculation_duration_seconds = Histogram(
    'recurring_service_recurrence_calculation_duration_seconds',
    'Recurrence calculation duration in seconds',
    ['recurrence_type']
)

task_creation_retries_total = Counter(
    'recurring_service_task_creation_retries_total',
    'Total task creation retry attempts',
    ['retry_count']
)

# System Metrics
active_connections = Gauge(
    'recurring_service_active_connections',
    'Number of active connections'
)

# Dapr Metrics
dapr_pubsub_publish_total = Counter(
    'recurring_service_dapr_pubsub_publish_total',
    'Total Dapr pub/sub publish operations',
    ['topic', 'status']
)

dapr_service_invocation_total = Counter(
    'recurring_service_dapr_service_invocation_total',
    'Total Dapr service invocation operations',
    ['service', 'method', 'status']
)

dapr_state_operations_total = Counter(
    'recurring_service_dapr_state_operations_total',
    'Total Dapr state operations',
    ['operation', 'status']
)


def track_request_metrics(method: str, endpoint: str, status: int, duration: float):
    """Track HTTP request metrics."""
    http_requests_total.labels(method=method, endpoint=endpoint, status=status).inc()
    http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(duration)


def track_event_processing(event_type: str, status: str, duration: float):
    """Track event processing metrics."""
    events_processed_total.labels(event_type=event_type, status=status).inc()
    event_processing_duration_seconds.labels(event_type=event_type).observe(duration)


def track_recurring_task_created(recurrence_type: str, status: str):
    """Track recurring task creation metrics."""
    recurring_tasks_created_total.labels(recurrence_type=recurrence_type, status=status).inc()


def track_recurrence_calculation(recurrence_type: str, duration: float):
    """Track recurrence calculation metrics."""
    recurrence_calculation_duration_seconds.labels(recurrence_type=recurrence_type).observe(duration)


def track_task_creation_retry(retry_count: int):
    """Track task creation retry attempts."""
    task_creation_retries_total.labels(retry_count=str(retry_count)).inc()


def track_dapr_pubsub(topic: str, status: str):
    """Track Dapr pub/sub operations."""
    dapr_pubsub_publish_total.labels(topic=topic, status=status).inc()


def track_dapr_service_invocation(service: str, method: str, status: str):
    """Track Dapr service invocation operations."""
    dapr_service_invocation_total.labels(service=service, method=method, status=status).inc()


def track_dapr_state(operation: str, status: str):
    """Track Dapr state operations."""
    dapr_state_operations_total.labels(operation=operation, status=status).inc()


def metrics_endpoint() -> Response:
    """
    Prometheus metrics endpoint handler.

    Returns:
        Response with Prometheus metrics in text format
    """
    metrics_data = generate_latest()
    return Response(content=metrics_data, media_type=CONTENT_TYPE_LATEST)


def track_time(metric_func: Callable):
    """
    Decorator to track execution time of functions.

    Args:
        metric_func: Function that takes duration as parameter
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                metric_func(duration)
                return result
            except Exception as e:
                duration = time.time() - start_time
                metric_func(duration)
                raise e

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                metric_func(duration)
                return result
            except Exception as e:
                duration = time.time() - start_time
                metric_func(duration)
                raise e

        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
