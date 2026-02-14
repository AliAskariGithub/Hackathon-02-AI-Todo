"""
Prometheus metrics utility for Notification Service.

Provides standardized metrics collection and exposure for monitoring:
- Request counters
- Request duration histograms
- Active connections gauge
- Error counters
- Business metrics (notifications sent, timing accuracy)
"""

from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
from typing import Callable
import time
from functools import wraps

# HTTP Request Metrics
http_requests_total = Counter(
    'notification_service_http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'notification_service_http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

# Event Processing Metrics
events_processed_total = Counter(
    'notification_service_events_processed_total',
    'Total events processed',
    ['event_type', 'status']
)

event_processing_duration_seconds = Histogram(
    'notification_service_event_processing_duration_seconds',
    'Event processing duration in seconds',
    ['event_type']
)

# Notification Metrics
notifications_sent_total = Counter(
    'notification_service_notifications_sent_total',
    'Total notifications sent',
    ['status']
)

notification_timing_accuracy_seconds = Histogram(
    'notification_service_timing_accuracy_seconds',
    'Notification timing accuracy (difference from scheduled time)',
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
)

# System Metrics
active_connections = Gauge(
    'notification_service_active_connections',
    'Number of active connections'
)

# Dapr Metrics
dapr_pubsub_publish_total = Counter(
    'notification_service_dapr_pubsub_publish_total',
    'Total Dapr pub/sub publish operations',
    ['topic', 'status']
)

dapr_state_operations_total = Counter(
    'notification_service_dapr_state_operations_total',
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


def track_notification_sent(status: str, timing_difference: float):
    """Track notification sent metrics."""
    notifications_sent_total.labels(status=status).inc()
    notification_timing_accuracy_seconds.observe(abs(timing_difference))


def track_dapr_pubsub(topic: str, status: str):
    """Track Dapr pub/sub operations."""
    dapr_pubsub_publish_total.labels(topic=topic, status=status).inc()


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


# Example usage:
if __name__ == "__main__":
    # Track HTTP request
    track_request_metrics("POST", "/events/reminder", 200, 0.123)

    # Track event processing
    track_event_processing("todo.reminder.fired", "success", 0.045)

    # Track notification sent
    track_notification_sent("success", 0.5)  # 0.5 seconds difference

    # Track Dapr operations
    track_dapr_pubsub("todo.notifications", "success")
    track_dapr_state("get", "success")

    # Get metrics
    print(generate_latest().decode('utf-8'))
