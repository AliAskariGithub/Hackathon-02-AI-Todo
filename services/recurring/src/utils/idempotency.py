"""
Idempotency Check Utility for Recurring Task Service

Uses Dapr State Store to track processed events and prevent duplicate task generation.
"""

import os
import logging
from typing import Optional
from datetime import datetime, timedelta
import httpx

logger = logging.getLogger(__name__)

# Configuration
DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")
DAPR_STATE_STORE = os.getenv("DAPR_STATE_STORE", "statestore")
IDEMPOTENCY_TTL_HOURS = int(os.getenv("IDEMPOTENCY_TTL_HOURS", "24"))


class IdempotencyChecker:
    """
    Idempotency checker using Dapr State Store.

    Tracks processed correlation IDs to prevent duplicate task generation.
    """

    def __init__(self):
        self.dapr_url = f"http://localhost:{DAPR_HTTP_PORT}"
        self.state_store = DAPR_STATE_STORE
        self.ttl_seconds = IDEMPOTENCY_TTL_HOURS * 3600

    async def is_processed(self, correlation_id: str) -> bool:
        """
        Check if an event with the given correlation ID has been processed.

        Args:
            correlation_id: Unique correlation ID for the event

        Returns:
            True if event has been processed, False otherwise
        """
        try:
            state_key = f"processed_event_{correlation_id}"

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.dapr_url}/v1.0/state/{self.state_store}/{state_key}"
                )

                if response.status_code == 200 and response.text:
                    logger.info(f"Event already processed: {correlation_id}")
                    return True

                return False

        except Exception as e:
            logger.error(f"Error checking idempotency: {str(e)}")
            # On error, assume not processed to avoid losing events
            return False

    async def mark_processed(self, correlation_id: str) -> bool:
        """
        Mark an event as processed in the state store.

        Args:
            correlation_id: Unique correlation ID for the event

        Returns:
            True if successfully marked, False otherwise
        """
        try:
            state_key = f"processed_event_{correlation_id}"

            state_data = [{
                "key": state_key,
                "value": {
                    "processed_at": datetime.utcnow().isoformat(),
                    "correlation_id": correlation_id
                },
                "metadata": {
                    "ttlInSeconds": str(self.ttl_seconds)
                }
            }]

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.dapr_url}/v1.0/state/{self.state_store}",
                    json=state_data
                )

                if response.status_code in [200, 201, 204]:
                    logger.info(f"Event marked as processed: {correlation_id}")
                    return True
                else:
                    logger.error(f"Failed to mark event as processed: {response.status_code}")
                    return False

        except Exception as e:
            logger.error(f"Error marking event as processed: {str(e)}")
            return False

    async def process_with_idempotency(self, correlation_id: str, process_func):
        """
        Process an event with idempotency check.

        Args:
            correlation_id: Unique correlation ID for the event
            process_func: Async function to execute if event not processed

        Returns:
            Result from process_func or None if already processed
        """
        # Check if already processed
        if await self.is_processed(correlation_id):
            logger.info(f"Skipping duplicate event: {correlation_id}")
            return None

        # Process the event
        result = await process_func()

        # Mark as processed
        await self.mark_processed(correlation_id)

        return result


# Global instance
idempotency_checker = IdempotencyChecker()
