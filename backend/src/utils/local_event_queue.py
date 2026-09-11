"""
Local event queue for graceful degradation when Kafka is unavailable.

Provides in-memory event buffering with periodic retry to Kafka.
Events are held for up to 5 minutes before being discarded.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from collections import deque
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class QueuedEvent:
    """Represents an event in the local queue."""
    event_data: Dict[str, Any]
    topic: str
    timestamp: datetime
    retry_count: int = 0
    max_retries: int = 10

    def is_expired(self, max_age_seconds: int = 300) -> bool:
        """Check if event has exceeded maximum age (default 5 minutes)."""
        age = (datetime.utcnow() - self.timestamp).total_seconds()
        return age > max_age_seconds

    def should_retry(self) -> bool:
        """Check if event should be retried."""
        return self.retry_count < self.max_retries and not self.is_expired()


class LocalEventQueue:
    """
    Local in-memory event queue for graceful degradation.

    When Kafka is unavailable, events are queued locally and retried
    periodically. Events older than 5 minutes are discarded.

    Usage:
        queue = LocalEventQueue(max_size=1000, retry_interval=30)
        await queue.start()

        # Queue event when Kafka is down
        await queue.enqueue(event_data, topic)

        # Stop background retry task
        await queue.stop()
    """

    def __init__(
        self,
        max_size: int = 1000,
        retry_interval: int = 30,
        max_age_seconds: int = 300
    ):
        self.max_size = max_size
        self.retry_interval = retry_interval
        self.max_age_seconds = max_age_seconds
        self.queue: deque[QueuedEvent] = deque(maxlen=max_size)
        self.retry_task: Optional[asyncio.Task] = None
        self.is_running = False
        self._lock = asyncio.Lock()

        # Statistics
        self.stats = {
            "total_queued": 0,
            "total_retried": 0,
            "total_succeeded": 0,
            "total_expired": 0,
            "total_dropped": 0,
            "current_size": 0
        }

    async def start(self):
        """Start background retry task."""
        if self.is_running:
            return

        self.is_running = True
        self.retry_task = asyncio.create_task(self._retry_loop())
        logger.info("Local event queue started")

    async def stop(self):
        """Stop background retry task."""
        self.is_running = False
        if self.retry_task:
            self.retry_task.cancel()
            try:
                await self.retry_task
            except asyncio.CancelledError:
                pass
        logger.info("Local event queue stopped")

    async def enqueue(self, event_data: Dict[str, Any], topic: str) -> bool:
        """
        Add event to local queue.

        Args:
            event_data: Event payload
            topic: Kafka topic name

        Returns:
            True if queued successfully, False if queue is full
        """
        async with self._lock:
            if len(self.queue) >= self.max_size:
                self.stats["total_dropped"] += 1
                logger.warning(
                    f"Local event queue full ({self.max_size}), dropping event",
                    extra={"topic": topic, "event_type": event_data.get("event_type")}
                )
                return False

            queued_event = QueuedEvent(
                event_data=event_data,
                topic=topic,
                timestamp=datetime.utcnow()
            )
            self.queue.append(queued_event)
            self.stats["total_queued"] += 1
            self.stats["current_size"] = len(self.queue)

            logger.info(
                f"Event queued locally (queue size: {len(self.queue)})",
                extra={"topic": topic, "event_type": event_data.get("event_type")}
            )
            return True

    async def _retry_loop(self):
        """Background task to retry queued events."""
        while self.is_running:
            try:
                await asyncio.sleep(self.retry_interval)
                await self._process_queue()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in retry loop: {e}", exc_info=True)

    async def _process_queue(self):
        """Process queued events and retry publishing to Kafka."""
        if not self.queue:
            return

        async with self._lock:
            events_to_retry = list(self.queue)
            self.queue.clear()

        succeeded = []
        failed = []
        expired = []

        for event in events_to_retry:
            if event.is_expired(self.max_age_seconds):
                expired.append(event)
                self.stats["total_expired"] += 1
                logger.warning(
                    f"Event expired after {self.max_age_seconds}s, discarding",
                    extra={
                        "topic": event.topic,
                        "event_type": event.event_data.get("event_type"),
                        "age_seconds": (datetime.utcnow() - event.timestamp).total_seconds()
                    }
                )
                continue

            if not event.should_retry():
                expired.append(event)
                self.stats["total_expired"] += 1
                logger.warning(
                    f"Event exceeded max retries ({event.max_retries}), discarding",
                    extra={
                        "topic": event.topic,
                        "event_type": event.event_data.get("event_type"),
                        "retry_count": event.retry_count
                    }
                )
                continue

            # Try to publish to Kafka
            success = await self._try_publish(event)

            if success:
                succeeded.append(event)
                self.stats["total_succeeded"] += 1
            else:
                event.retry_count += 1
                failed.append(event)
                self.stats["total_retried"] += 1

        # Re-queue failed events
        if failed:
            async with self._lock:
                for event in failed:
                    if len(self.queue) < self.max_size:
                        self.queue.append(event)
                self.stats["current_size"] = len(self.queue)

        if succeeded or expired:
            logger.info(
                f"Queue processing complete: {len(succeeded)} succeeded, "
                f"{len(failed)} failed, {len(expired)} expired/dropped"
            )

    async def _try_publish(self, event: QueuedEvent) -> bool:
        """
        Try to publish event to Kafka via Dapr.

        Args:
            event: Queued event to publish

        Returns:
            True if published successfully, False otherwise
        """
        try:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"http://localhost:3500/v1.0/publish/kafka-pubsub/{event.topic}",
                    json=event.event_data,
                    headers={"Content-Type": "application/json"},
                    timeout=5.0
                )

                if response.status_code == 200:
                    logger.info(
                        f"Successfully published queued event to Kafka",
                        extra={
                            "topic": event.topic,
                            "event_type": event.event_data.get("event_type"),
                            "retry_count": event.retry_count
                        }
                    )
                    return True
                else:
                    logger.warning(
                        f"Failed to publish queued event: HTTP {response.status_code}",
                        extra={
                            "topic": event.topic,
                            "event_type": event.event_data.get("event_type"),
                            "retry_count": event.retry_count
                        }
                    )
                    return False

        except Exception as e:
            logger.warning(
                f"Error publishing queued event: {e}",
                extra={
                    "topic": event.topic,
                    "event_type": event.event_data.get("event_type"),
                    "retry_count": event.retry_count
                }
            )
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Get queue statistics."""
        return {
            **self.stats,
            "is_running": self.is_running,
            "max_size": self.max_size,
            "retry_interval": self.retry_interval,
            "max_age_seconds": self.max_age_seconds
        }

    def clear(self):
        """Clear all queued events."""
        self.queue.clear()
        self.stats["current_size"] = 0
        logger.info("Local event queue cleared")


# Global instance
_local_queue: Optional[LocalEventQueue] = None


def get_local_queue() -> LocalEventQueue:
    """Get or create global local event queue instance."""
    global _local_queue
    if _local_queue is None:
        _local_queue = LocalEventQueue()
    return _local_queue


async def publish_with_fallback(
    event_data: Dict[str, Any],
    topic: str,
    dapr_http_port: int = 3500
) -> bool:
    """
    Publish event to Kafka with local queue fallback.

    Tries to publish directly to Kafka. If that fails, queues locally
    for retry.

    Args:
        event_data: Event payload
        topic: Kafka topic name
        dapr_http_port: Dapr HTTP port

    Returns:
        True if published or queued successfully
    """
    import httpx

    try:
        # Try direct publish to Kafka
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"http://localhost:{dapr_http_port}/v1.0/publish/kafka-pubsub/{topic}",
                json=event_data,
                headers={"Content-Type": "application/json"},
                timeout=5.0
            )

            if response.status_code == 200:
                return True
            else:
                logger.warning(
                    f"Kafka publish failed with HTTP {response.status_code}, "
                    f"falling back to local queue"
                )

    except Exception as e:
        logger.warning(
            f"Kafka unavailable ({e}), falling back to local queue"
        )

    # Fallback to local queue
    queue = get_local_queue()
    return await queue.enqueue(event_data, topic)


# Example usage:
if __name__ == "__main__":
    async def main():
        # Start local queue
        queue = get_local_queue()
        await queue.start()

        # Simulate event publishing with fallback
        event = {
            "event_type": "todo.task.created",
            "payload": {"task_id": "123", "title": "Test Task"},
            "timestamp": datetime.utcnow().isoformat(),
            "correlation_id": "test-123"
        }

        success = await publish_with_fallback(event, "todo.task.events")
        print(f"Publish result: {success}")

        # Check stats
        print(f"Queue stats: {queue.get_stats()}")

        # Wait for retry
        await asyncio.sleep(35)

        # Stop queue
        await queue.stop()

    asyncio.run(main())
