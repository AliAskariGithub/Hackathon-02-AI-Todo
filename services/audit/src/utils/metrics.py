"""
Prometheus metrics utility for Audit Service.

Provides standardized metrics collection and exposure for monitoring:
- Request counters
- Request duration histograms
- Event processing metrics
- Audit log storage metrics
- Query performance metrics
"""

from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
from typing import Callable
import time
from functools import wraps

# HTTP Request Metrics
http_requests_total = Counter(
    'audit_service_http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'audit_service_http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

# Event Processing Metrics
events_processed_total = Counter(
    'audit_service_events_processed_total',
    'Total events processed',
    ['event_type', 'status']
)

event_processing_duration_seconds = Histogram(
    'audit_service_event_processing_duration_seconds',
    'Event processing duration in seconds',
    ['event_type']
)

# Audit Log Metrics
audit_logs_stored_total = Counter(
    'audit_service_logs_stored_total',
    'Total audit logs stored',
    ['service_name', 'status']
)

audit_log_storage_duration_seconds = Histogram(
    'audit_service_log_storage_duration_seconds',
    'Audit log storage duration in seconds'
)

duplicate_events_detected_total = Counter(
    'audit_service_duplicate_events_detected_total',
    'Total duplicate events detected',
    ['event_type']
)

chronology_violations_total = Counter(
    'audit_service_chronology_violations_total',
    'Total chronological order violations detected'
)

# Query Metrics
audit_queries_total = Counter(
    'audit_service_queries_total',
    'Total audit log queries',
    ['query_type', 'status']
)

audit_query_duration_seconds = Histogram(
    'audit_service_query_duration_seconds',
    'Audit log query duration in seconds',
    ['query_type']
)

audit_query_results_count = Histogram(
    'audit_service_query_results_count',
    'Number of results returned by audit queries',
    buckets=[1, 10, 50, 100, 500, 1000, 5000]
)

# System Metrics
active_connections = Gauge(
    'audit_service_active_connections',
    'Number of active connections'
)

audit_log_total_count = Gauge(
    'audit_service_log_total_count',
    'Total number of audit logs in storage'
)

# Dapr Metrics
dapr_state_operations_total = Counter(
    'audit_service_dapr_state_operations_total',
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


def track_audit_log_stored(service_name: str, status: str, duration: float):
    """Track audit log storage metrics."""
    audit_logs_stored_total.labels(service_name=service_name, status=status).inc()
    audit_log_storage_duration_seconds.observe(duration)


def track_duplicate_event(event_type: str):
    """Track duplicate event detection."""
    duplicate_events_detected_total.labels(event_type=event_type).inc()


def track_chronology_violation():
    """Track chronological order violation."""
    chronology_violations_total.inc()


def track_audit_query(query_type: str, status: str, duration: float, result_count: int):
    """Track audit query metrics."""
    audit_queries_total.labels(query_type=query_type, status=status).inc()
    audit_query_duration_seconds.labels(query_type=query_type).observe(duration)
    audit_query_results_count.observe(result_count)


def update_audit_log_count(count: int):
    """Update total audit log count gauge."""
    audit_log_total_count.set(count)


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
