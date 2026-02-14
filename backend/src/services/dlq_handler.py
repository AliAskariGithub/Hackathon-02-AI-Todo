"""
Dead Letter Queue (DLQ) Handler

Handles failed events that could not be processed after retries.
Provides mechanisms for inspecting, reprocessing, and managing failed events.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from uuid import UUID
import json

logger = logging.getLogger(__name__)


class DLQHandler:
    """
    Handler for managing dead letter queue events.
    """

    def __init__(self, dapr_http_port: int = 3500):
        """
        Initialize the DLQ handler.

        Args:
            dapr_http_port: Dapr sidecar HTTP port
        """
        self.dapr_http_port = dapr_http_port
        self.dlq_topic = "todo.task.events.dlq"

    async def send_to_dlq(
        self,
        event: Dict[str, Any],
        error_message: str,
        retry_count: int,
        original_topic: str
    ) -> bool:
        """
        Send a failed event to the dead letter queue.

        Args:
            event: The original event that failed
            error_message: Description of the error
            retry_count: Number of retry attempts made
            original_topic: The original topic the event came from

        Returns:
            True if successfully sent to DLQ, False otherwise
        """
        try:
            # Enrich event with DLQ metadata
            dlq_event = {
                "original_event": event,
                "error_message": error_message,
                "retry_count": retry_count,
                "original_topic": original_topic,
                "dlq_timestamp": datetime.utcnow().isoformat(),
                "correlation_id": event.get("correlation_id"),
                "event_type": event.get("event_type")
            }

            logger.error(
                f"Sending event to DLQ: event_type={event.get('event_type')}, "
                f"error={error_message}, retries={retry_count}"
            )

            # Publish to DLQ topic via Dapr
            from ...dapr_sdk_utils.pubsub import DaprPubSub
            pubsub = DaprPubSub()

            pubsub.publish_event(
                topic=self.dlq_topic,
                event_type="todo.dlq.event",
                payload=dlq_event,
                correlation_id=event.get("correlation_id")
            )

            logger.info(f"Successfully sent event to DLQ: {event.get('event_type')}")
            return True

        except Exception as e:
            logger.error(f"Failed to send event to DLQ: {str(e)}")
            # Last resort: log to file
            self._log_to_file(dlq_event)
            return False

    def _log_to_file(self, dlq_event: Dict[str, Any]) -> None:
        """
        Log failed event to file as last resort.

        Args:
            dlq_event: The DLQ event to log
        """
        try:
            log_file = "dlq_events.log"
            with open(log_file, "a") as f:
                f.write(json.dumps(dlq_event) + "\n")
            logger.info(f"Logged DLQ event to file: {log_file}")
        except Exception as e:
            logger.error(f"Failed to log DLQ event to file: {str(e)}")

    async def get_dlq_events(
        self,
        limit: int = 100,
        event_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve events from the dead letter queue.

        Args:
            limit: Maximum number of events to retrieve
            event_type: Optional filter by event type

        Returns:
            List of DLQ events
        """
        try:
            # TODO: Implement DLQ event retrieval from storage
            # This would typically query a database or state store
            logger.info(f"Retrieving DLQ events: limit={limit}, event_type={event_type}")
            return []

        except Exception as e:
            logger.error(f"Error retrieving DLQ events: {str(e)}")
            return []

    async def reprocess_dlq_event(
        self,
        dlq_event_id: UUID,
        target_topic: Optional[str] = None
    ) -> bool:
        """
        Reprocess a failed event from the DLQ.

        Args:
            dlq_event_id: ID of the DLQ event to reprocess
            target_topic: Optional target topic (defaults to original topic)

        Returns:
            True if reprocessing succeeded, False otherwise
        """
        try:
            # TODO: Implement DLQ event reprocessing
            # 1. Retrieve event from DLQ storage
            # 2. Republish to original or target topic
            # 3. Remove from DLQ if successful
            logger.info(f"Reprocessing DLQ event: {dlq_event_id}")
            return True

        except Exception as e:
            logger.error(f"Error reprocessing DLQ event: {str(e)}")
            return False


class RetryPolicy:
    """
    Retry policy with exponential backoff for event processing.
    """

    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0
    ):
        """
        Initialize retry policy.

        Args:
            max_retries: Maximum number of retry attempts
            initial_delay: Initial delay in seconds
            max_delay: Maximum delay in seconds
            exponential_base: Base for exponential backoff calculation
        """
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base

    def calculate_delay(self, retry_count: int) -> float:
        """
        Calculate delay for the given retry attempt.

        Args:
            retry_count: Current retry attempt (0-indexed)

        Returns:
            Delay in seconds
        """
        delay = self.initial_delay * (self.exponential_base ** retry_count)
        return min(delay, self.max_delay)

    def should_retry(self, retry_count: int) -> bool:
        """
        Determine if another retry should be attempted.

        Args:
            retry_count: Current retry attempt (0-indexed)

        Returns:
            True if should retry, False otherwise
        """
        return retry_count < self.max_retries


async def process_event_with_retry(
    event: Dict[str, Any],
    handler_func,
    retry_policy: RetryPolicy,
    dlq_handler: DLQHandler,
    original_topic: str
) -> Dict[str, Any]:
    """
    Process an event with retry logic and DLQ fallback.

    Args:
        event: The event to process
        handler_func: Async function to handle the event
        retry_policy: Retry policy configuration
        dlq_handler: DLQ handler for failed events
        original_topic: Original topic the event came from

    Returns:
        Processing result dictionary
    """
    import asyncio

    retry_count = 0

    while True:
        try:
            # Attempt to process event
            result = await handler_func(event)

            if result.get("status") == "success":
                logger.info(
                    f"Successfully processed event: {event.get('event_type')} "
                    f"(retries: {retry_count})"
                )
                return result

            # If handler returned error status, retry
            if retry_policy.should_retry(retry_count):
                delay = retry_policy.calculate_delay(retry_count)
                logger.warning(
                    f"Event processing returned error, retrying in {delay}s "
                    f"(attempt {retry_count + 1}/{retry_policy.max_retries})"
                )
                await asyncio.sleep(delay)
                retry_count += 1
                continue
            else:
                # Max retries exceeded, send to DLQ
                await dlq_handler.send_to_dlq(
                    event=event,
                    error_message=result.get("message", "Unknown error"),
                    retry_count=retry_count,
                    original_topic=original_topic
                )
                return {
                    "status": "dlq",
                    "message": "Max retries exceeded, sent to DLQ"
                }

        except Exception as e:
            # Exception during processing
            if retry_policy.should_retry(retry_count):
                delay = retry_policy.calculate_delay(retry_count)
                logger.warning(
                    f"Event processing failed with exception: {str(e)}, "
                    f"retrying in {delay}s (attempt {retry_count + 1}/{retry_policy.max_retries})"
                )
                await asyncio.sleep(delay)
                retry_count += 1
                continue
            else:
                # Max retries exceeded, send to DLQ
                await dlq_handler.send_to_dlq(
                    event=event,
                    error_message=str(e),
                    retry_count=retry_count,
                    original_topic=original_topic
                )
                return {
                    "status": "dlq",
                    "message": f"Max retries exceeded after exception: {str(e)}"
                }
