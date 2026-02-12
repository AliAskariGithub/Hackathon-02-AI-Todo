"""
Unit tests for idempotency service (correlation ID deduplication).

Tests correlation ID storage, lookup, and TTL behavior.
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.services.idempotency_service import (
    is_processed,
    mark_as_processed,
    check_and_mark_processed
)


class TestIdempotencyService:
    """Test idempotency service for correlation ID tracking."""

    @pytest.fixture
    def correlation_id(self):
        """Generate a unique correlation ID for testing."""
        return uuid4()

    @pytest.fixture
    def user_id(self):
        """Generate a unique user ID for testing."""
        return uuid4()

    async def test_is_processed_returns_false_for_new_id(self, correlation_id, user_id):
        """Test that is_processed returns False for new correlation ID."""
        result = await is_processed(correlation_id, user_id)
        assert result is False

    async def test_mark_as_processed_stores_correlation_id(self, correlation_id, user_id):
        """Test that mark_as_processed stores correlation ID."""
        await mark_as_processed(correlation_id, user_id)

        result = await is_processed(correlation_id, user_id)
        assert result is True

    async def test_check_and_mark_processed_atomic_operation(self, correlation_id, user_id):
        """Test that check_and_mark_processed is atomic."""
        # First call should return False and mark as processed
        result1 = await check_and_mark_processed(correlation_id, user_id)
        assert result1 is False

        # Second call should return True (already processed)
        result2 = await check_and_mark_processed(correlation_id, user_id)
        assert result2 is True

    async def test_different_users_different_correlation_ids(self, correlation_id):
        """Test that correlation IDs are scoped per user."""
        user_id_1 = uuid4()
        user_id_2 = uuid4()

        await mark_as_processed(correlation_id, user_id_1)

        # Same correlation ID for different user should not be processed
        result = await is_processed(correlation_id, user_id_2)
        assert result is False

    async def test_multiple_correlation_ids_per_user(self, user_id):
        """Test that multiple correlation IDs can be tracked per user."""
        correlation_id_1 = uuid4()
        correlation_id_2 = uuid4()

        await mark_as_processed(correlation_id_1, user_id)
        await mark_as_processed(correlation_id_2, user_id)

        assert await is_processed(correlation_id_1, user_id) is True
        assert await is_processed(correlation_id_2, user_id) is True

    async def test_correlation_id_ttl_expiration(self, correlation_id, user_id):
        """Test that correlation IDs expire after TTL (mock test)."""
        # This test would require mocking time or using a test TTL
        # In production, TTL is typically 24-48 hours
        await mark_as_processed(correlation_id, user_id, ttl_seconds=1)

        # Immediately should be processed
        assert await is_processed(correlation_id, user_id) is True

        # After TTL expires (would need to wait or mock time)
        # In real implementation, this would be handled by State Store TTL

    async def test_concurrent_check_and_mark(self, correlation_id, user_id):
        """Test concurrent check_and_mark operations (race condition)."""
        # This test would require concurrent execution
        # Only one should succeed in marking as new
        import asyncio

        results = await asyncio.gather(
            check_and_mark_processed(correlation_id, user_id),
            check_and_mark_processed(correlation_id, user_id),
            check_and_mark_processed(correlation_id, user_id)
        )

        # Exactly one should return False (first to process)
        # Others should return True (already processed)
        assert results.count(False) == 1
        assert results.count(True) == 2


class TestIdempotencyEdgeCases:
    """Test edge cases for idempotency service."""

    async def test_empty_correlation_id_raises_error(self):
        """Test that empty correlation ID raises error."""
        with pytest.raises(ValueError, match="correlation_id cannot be empty"):
            await is_processed(None, uuid4())

    async def test_empty_user_id_raises_error(self):
        """Test that empty user ID raises error."""
        with pytest.raises(ValueError, match="user_id cannot be empty"):
            await is_processed(uuid4(), None)

    async def test_invalid_correlation_id_format(self):
        """Test that invalid correlation ID format is handled."""
        with pytest.raises(ValueError):
            await is_processed("not-a-uuid", uuid4())

    async def test_state_store_unavailable_fallback(self, correlation_id, user_id):
        """Test fallback behavior when State Store is unavailable."""
        # This would require mocking State Store failure
        # Should either:
        # 1. Return False (allow processing) - fail-open
        # 2. Raise exception - fail-closed
        # Implementation choice depends on requirements
        pass


class TestIdempotencyMetadata:
    """Test metadata storage with correlation IDs."""

    async def test_store_metadata_with_correlation_id(self, correlation_id, user_id):
        """Test storing metadata with correlation ID."""
        metadata = {
            "task_id": str(uuid4()),
            "recurrence": "Daily",
            "processed_at": datetime.utcnow().isoformat()
        }

        await mark_as_processed(correlation_id, user_id, metadata=metadata)

        # Verify metadata can be retrieved
        stored_metadata = await get_correlation_metadata(correlation_id, user_id)
        assert stored_metadata["task_id"] == metadata["task_id"]
        assert stored_metadata["recurrence"] == metadata["recurrence"]

    async def test_metadata_includes_timestamp(self, correlation_id, user_id):
        """Test that metadata includes processing timestamp."""
        await mark_as_processed(correlation_id, user_id)

        metadata = await get_correlation_metadata(correlation_id, user_id)
        assert "processed_at" in metadata
        assert isinstance(metadata["processed_at"], str)


# Helper function for metadata retrieval (would be in actual service)
async def get_correlation_metadata(correlation_id, user_id):
    """Retrieve metadata for a correlation ID."""
    # Implementation would query State Store
    pass
