"""
Circuit Breaker pattern implementation for Dapr Service Invocation calls.

Prevents cascading failures by temporarily blocking calls to failing services
and allowing them time to recover.

States:
- CLOSED: Normal operation, requests pass through
- OPEN: Service is failing, requests are blocked
- HALF_OPEN: Testing if service has recovered
"""

import time
from enum import Enum
from typing import Callable, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import asyncio
from functools import wraps


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""
    failure_threshold: int = 5  # Number of failures before opening circuit
    success_threshold: int = 2  # Number of successes to close circuit from half-open
    timeout: int = 60  # Seconds to wait before trying half-open
    expected_exception: type = Exception  # Exception type to catch


class CircuitBreakerError(Exception):
    """Raised when circuit breaker is open."""
    pass


class CircuitBreaker:
    """
    Circuit breaker implementation for protecting service calls.

    Usage:
        breaker = CircuitBreaker(
            failure_threshold=5,
            success_threshold=2,
            timeout=60
        )

        @breaker
        async def call_service():
            # Your service call here
            pass
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        success_threshold: int = 2,
        timeout: int = 60,
        expected_exception: type = Exception
    ):
        self.config = CircuitBreakerConfig(
            failure_threshold=failure_threshold,
            success_threshold=success_threshold,
            timeout=timeout,
            expected_exception=expected_exception
        )
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.last_state_change: datetime = datetime.utcnow()

    def __call__(self, func: Callable) -> Callable:
        """Decorator to wrap function with circuit breaker."""
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            return await self._call_async(func, *args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            return self._call_sync(func, *args, **kwargs)

        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    async def _call_async(self, func: Callable, *args, **kwargs) -> Any:
        """Execute async function with circuit breaker protection."""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self._transition_to_half_open()
            else:
                raise CircuitBreakerError(
                    f"Circuit breaker is OPEN. Service unavailable. "
                    f"Will retry after {self._time_until_retry():.1f} seconds."
                )

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except self.config.expected_exception as e:
            self._on_failure()
            raise e

    def _call_sync(self, func: Callable, *args, **kwargs) -> Any:
        """Execute sync function with circuit breaker protection."""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self._transition_to_half_open()
            else:
                raise CircuitBreakerError(
                    f"Circuit breaker is OPEN. Service unavailable. "
                    f"Will retry after {self._time_until_retry():.1f} seconds."
                )

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.config.expected_exception as e:
            self._on_failure()
            raise e

    def _on_success(self):
        """Handle successful call."""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                self._transition_to_closed()
        elif self.state == CircuitState.CLOSED:
            self.failure_count = 0

    def _on_failure(self):
        """Handle failed call."""
        self.last_failure_time = datetime.utcnow()

        if self.state == CircuitState.HALF_OPEN:
            self._transition_to_open()
        elif self.state == CircuitState.CLOSED:
            self.failure_count += 1
            if self.failure_count >= self.config.failure_threshold:
                self._transition_to_open()

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self.last_failure_time is None:
            return True

        time_since_failure = (datetime.utcnow() - self.last_failure_time).total_seconds()
        return time_since_failure >= self.config.timeout

    def _time_until_retry(self) -> float:
        """Calculate seconds until retry is allowed."""
        if self.last_failure_time is None:
            return 0.0

        time_since_failure = (datetime.utcnow() - self.last_failure_time).total_seconds()
        return max(0.0, self.config.timeout - time_since_failure)

    def _transition_to_open(self):
        """Transition to OPEN state."""
        self.state = CircuitState.OPEN
        self.last_state_change = datetime.utcnow()
        self.success_count = 0

    def _transition_to_half_open(self):
        """Transition to HALF_OPEN state."""
        self.state = CircuitState.HALF_OPEN
        self.last_state_change = datetime.utcnow()
        self.success_count = 0
        self.failure_count = 0

    def _transition_to_closed(self):
        """Transition to CLOSED state."""
        self.state = CircuitState.CLOSED
        self.last_state_change = datetime.utcnow()
        self.failure_count = 0
        self.success_count = 0

    def get_state(self) -> dict:
        """Get current circuit breaker state."""
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure_time": self.last_failure_time.isoformat() if self.last_failure_time else None,
            "last_state_change": self.last_state_change.isoformat(),
            "time_until_retry": self._time_until_retry() if self.state == CircuitState.OPEN else 0.0
        }

    def reset(self):
        """Manually reset circuit breaker to CLOSED state."""
        self._transition_to_closed()


# Example usage:
if __name__ == "__main__":
    import httpx

    # Create circuit breaker for Dapr service invocation
    breaker = CircuitBreaker(
        failure_threshold=3,
        success_threshold=2,
        timeout=30,
        expected_exception=httpx.HTTPError
    )

    @breaker
    async def call_backend_service(task_data: dict):
        """Call backend service via Dapr."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:3500/v1.0/invoke/backend-api/method/tasks/internal",
                json=task_data,
                timeout=5.0
            )
            response.raise_for_status()
            return response.json()

    # Use the protected function
    async def main():
        try:
            result = await call_backend_service({"title": "Test Task"})
            print(f"Success: {result}")
        except CircuitBreakerError as e:
            print(f"Circuit breaker open: {e}")
        except Exception as e:
            print(f"Service error: {e}")

        # Check circuit breaker state
        print(f"Circuit state: {breaker.get_state()}")

    asyncio.run(main())
