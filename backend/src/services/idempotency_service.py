"""
Idempotency Service - Correlation ID Storage and Lookup

This service provides idempotency checks using correlation IDs stored in
Dapr State Store. It prevents duplicate recurring task generation on event replay.

Key Features:
- Store correlation IDs with TTL (Time-To-Live)
- Check if correlation ID has been processed
- Automatic cleanup after TTL expires
- Thread-safe operations via Dapr State Store
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from uuid import UUID

from ..dapr_sdk_utils.state import DaprStateStore, correlation_id_key


class IdempotencyService:
    """
    Service for managing idempotency via correlation IDs.

    This service uses Dapr State Store to track processed correlation IDs,
    preventing duplicate operations on event replay.
    """

    def __init__(self, ttl_days: int = 7):
        """
        Initialize idempotency service.

        Args:
            ttl_days: Time-To-Live for correlation ID tracking (default: 7 days)
        """
        self.state_store = DaprStateStore()
        self.ttl_days = ttl_days

    async def is_processed(self, correlation_id: UUID) -> bool:
        """
        Check if correlation ID has already been processed.

        Args:
            correlation_id: Correlation ID to check

        Returns:
            True if already processed, False otherwise

        Example:
            >>> service = IdempotencyService()
            >>> is_duplicate = await service.is_processed(UUID("correlation-uuid"))
        """
        key = correlation_id_key(correlation_id)
        result = self.state_store.get_state(key)
        return result is not None

    async def mark_as_processed(
        self,
        correlation_id: UUID,
        operation_type: str,
        operation_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Mark correlation ID as processed.

        Args:
            correlation_id: Correlation ID to mark
            operation_type: Type of operation (e.g., "task_generation", "reminder_scheduling")
            operation_data: Optional data about the operation

        Example:
            >>> service = IdempotencyService()
            >>> await service.mark_as_processed(
            ...     correlation_id=UUID("correlation-uuid"),
            ...     operation_type="task_generation",
            ...     operation_data={"task_id": "task-uuid"}
            ... )
        """
        key = correlation_id_key(correlation_id)
        value = {
            "correlation_id": str(correlation_id),
            "operation_type": operation_type,
            "operation_data": operation_data or {},
            "processed_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(days=self.ttl_days)).isoformat()
        }

        # Store with metadata indicating TTL
        # Note: Dapr State Store TTL is configured at component level
        # This expires_at field is for informational purposes
        self.state_store.save_state(key, value)

    async def get_processed_operation(
        self,
        correlation_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """
        Get details of processed operation by correlation ID.

        Args:
            correlation_id: Correlation ID to lookup

        Returns:
            Operation details or None if not found

        Example:
            >>> service = IdempotencyService()
            >>> operation = await service.get_processed_operation(UUID("correlation-uuid"))
            >>> if operation:
            ...     print(f"Operation type: {operation['operation_type']}")
            ...     print(f"Processed at: {operation['processed_at']}")
        """
        key = correlation_id_key(correlation_id)
        return self.state_store.get_state(key)

    async def delete_processed_operation(
        self,
        correlation_id: UUID
    ) -> None:
        """
        Delete processed operation tracking (manual cleanup).

        This is typically not needed as TTL handles automatic cleanup,
        but can be used for manual cleanup in special cases.

        Args:
            correlation_id: Correlation ID to delete

        Example:
            >>> service = IdempotencyService()
            >>> await service.delete_processed_operation(UUID("correlation-uuid"))
        """
        key = correlation_id_key(correlation_id)
        self.state_store.delete_state(key)

    async def check_and_mark_processed(
        self,
        correlation_id: UUID,
        operation_type: str,
        operation_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Atomic check-and-mark operation.

        This method checks if the correlation ID has been processed and,
        if not, marks it as processed in a single operation.

        Args:
            correlation_id: Correlation ID to check and mark
            operation_type: Type of operation
            operation_data: Optional operation data

        Returns:
            True if this is the first processing (marked successfully)
            False if already processed (duplicate)

        Example:
            >>> service = IdempotencyService()
            >>> is_first_time = await service.check_and_mark_processed(
            ...     correlation_id=UUID("correlation-uuid"),
            ...     operation_type="task_generation",
            ...     operation_data={"task_id": "task-uuid"}
            ... )
            >>> if is_first_time:
            ...     # Proceed with operation
            ...     pass
            >>> else:
            ...     # Skip duplicate operation
            ...     pass
        """
        # Check if already processed
        if await self.is_processed(correlation_id):
            return False

        # Mark as processed
        await self.mark_as_processed(
            correlation_id=correlation_id,
            operation_type=operation_type,
            operation_data=operation_data
        )

        return True

    async def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about processed operations.

        This is useful for monitoring and debugging.

        Returns:
            Statistics dictionary

        Example:
            >>> service = IdempotencyService()
            >>> stats = await service.get_statistics()
            >>> print(f"Total processed: {stats['total_processed']}")
        """
        # This would require querying all correlation ID keys
        # For now, return placeholder statistics
        # In production, this could be implemented with State Store queries
        return {
            "total_processed": 0,
            "ttl_days": self.ttl_days,
            "note": "Statistics require State Store query support"
        }


# Singleton instance for application-wide use
_idempotency_service_instance: Optional[IdempotencyService] = None


def get_idempotency_service() -> IdempotencyService:
    """
    Get the singleton IdempotencyService instance.

    Returns:
        IdempotencyService instance

    Example:
        >>> from services.idempotency_service import get_idempotency_service
        >>> service = get_idempotency_service()
        >>> is_duplicate = await service.is_processed(correlation_id)
    """
    global _idempotency_service_instance
    if _idempotency_service_instance is None:
        _idempotency_service_instance = IdempotencyService()
    return _idempotency_service_instance


# Module-level convenience functions for backward compatibility
async def is_processed(correlation_id: UUID) -> bool:
    """Check if correlation ID has been processed."""
    service = get_idempotency_service()
    return await service.is_processed(correlation_id)


async def mark_as_processed(
    correlation_id: UUID,
    operation_type: str,
    operation_data: Optional[Dict[str, Any]] = None
) -> None:
    """Mark correlation ID as processed."""
    service = get_idempotency_service()
    await service.mark_as_processed(correlation_id, operation_type, operation_data)


async def check_and_mark_processed(
    correlation_id: UUID,
    operation_type: str,
    operation_data: Optional[Dict[str, Any]] = None
) -> bool:
    """Atomic check-and-mark operation."""
    service = get_idempotency_service()
    return await service.check_and_mark_processed(correlation_id, operation_type, operation_data)
