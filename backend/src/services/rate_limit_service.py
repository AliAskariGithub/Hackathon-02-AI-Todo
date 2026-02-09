"""Rate limiting service for per-user chat message limits."""
from datetime import datetime, timedelta
from typing import Dict, Tuple
from uuid import UUID
import asyncio


class RateLimitService:
    """Service for managing per-user rate limiting."""

    def __init__(self):
        """Initialize rate limit service with in-memory storage."""
        # Structure: {user_id: [(timestamp, count), ...]}
        self._user_limits: Dict[UUID, list] = {}
        self._lock = asyncio.Lock()

        # Rate limit configuration
        self.MESSAGES_PER_MINUTE = 20
        self.MESSAGES_PER_HOUR = 200

    async def check_rate_limit(self, user_id: UUID) -> Tuple[bool, str]:
        """
        Check if user has exceeded rate limits.

        Returns:
            Tuple of (is_allowed, error_message)
        """
        async with self._lock:
            now = datetime.utcnow()

            # Initialize user tracking if not exists
            if user_id not in self._user_limits:
                self._user_limits[user_id] = []

            # Clean up old entries
            self._cleanup_old_entries(user_id, now)

            # Get user's message history
            user_messages = self._user_limits[user_id]

            # Check minute limit
            one_minute_ago = now - timedelta(minutes=1)
            messages_last_minute = sum(
                1 for timestamp in user_messages
                if timestamp > one_minute_ago
            )

            if messages_last_minute >= self.MESSAGES_PER_MINUTE:
                retry_after = 60 - (now - min(
                    ts for ts in user_messages if ts > one_minute_ago
                )).seconds
                return False, f"Rate limit exceeded. You can send up to {self.MESSAGES_PER_MINUTE} messages per minute. Please wait {retry_after} seconds."

            # Check hour limit
            one_hour_ago = now - timedelta(hours=1)
            messages_last_hour = sum(
                1 for timestamp in user_messages
                if timestamp > one_hour_ago
            )

            if messages_last_hour >= self.MESSAGES_PER_HOUR:
                oldest_message = min(ts for ts in user_messages if ts > one_hour_ago)
                retry_after = 3600 - (now - oldest_message).seconds
                return False, f"Rate limit exceeded. You can send up to {self.MESSAGES_PER_HOUR} messages per hour. Please wait {retry_after // 60} minutes."

            # Record this message
            self._user_limits[user_id].append(now)

            return True, ""

    def _cleanup_old_entries(self, user_id: UUID, now: datetime):
        """Remove entries older than 1 hour."""
        one_hour_ago = now - timedelta(hours=1)
        self._user_limits[user_id] = [
            timestamp for timestamp in self._user_limits[user_id]
            if timestamp > one_hour_ago
        ]

    async def get_user_stats(self, user_id: UUID) -> Dict[str, int]:
        """Get current rate limit stats for a user."""
        async with self._lock:
            now = datetime.utcnow()

            if user_id not in self._user_limits:
                return {
                    "messages_last_minute": 0,
                    "messages_last_hour": 0,
                    "remaining_minute": self.MESSAGES_PER_MINUTE,
                    "remaining_hour": self.MESSAGES_PER_HOUR
                }

            self._cleanup_old_entries(user_id, now)
            user_messages = self._user_limits[user_id]

            one_minute_ago = now - timedelta(minutes=1)
            one_hour_ago = now - timedelta(hours=1)

            messages_last_minute = sum(
                1 for timestamp in user_messages
                if timestamp > one_minute_ago
            )
            messages_last_hour = sum(
                1 for timestamp in user_messages
                if timestamp > one_hour_ago
            )

            return {
                "messages_last_minute": messages_last_minute,
                "messages_last_hour": messages_last_hour,
                "remaining_minute": max(0, self.MESSAGES_PER_MINUTE - messages_last_minute),
                "remaining_hour": max(0, self.MESSAGES_PER_HOUR - messages_last_hour)
            }


# Global rate limit service instance
rate_limit_service = RateLimitService()
