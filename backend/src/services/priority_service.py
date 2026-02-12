"""
Priority validation service.

Validates priority values and handles priority-related business logic.
"""

from typing import List, Literal
from enum import Enum


class PriorityLevel(str, Enum):
    """Priority level enumeration."""
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


VALID_PRIORITIES = [p.value for p in PriorityLevel]
DEFAULT_PRIORITY = PriorityLevel.MEDIUM.value


class PriorityService:
    """Service for priority validation and management."""

    @staticmethod
    def validate_priority(priority: str) -> bool:
        """
        Validate that priority is one of the allowed values.

        Args:
            priority: Priority string to validate

        Returns:
            True if valid, False otherwise
        """
        return priority in VALID_PRIORITIES

    @staticmethod
    def get_default_priority() -> str:
        """
        Get the default priority for new tasks.

        Returns:
            Default priority value (Medium)
        """
        return DEFAULT_PRIORITY

    @staticmethod
    def get_valid_priorities() -> List[str]:
        """
        Get list of all valid priority values.

        Returns:
            List of valid priority strings
        """
        return VALID_PRIORITIES

    @staticmethod
    def normalize_priority(priority: str) -> str:
        """
        Normalize priority string to standard format.

        Args:
            priority: Priority string (case-insensitive)

        Returns:
            Normalized priority string

        Raises:
            ValueError: If priority is invalid
        """
        normalized = priority.capitalize()
        if normalized not in VALID_PRIORITIES:
            raise ValueError(f"Invalid priority: {priority}. Must be one of {VALID_PRIORITIES}")
        return normalized

    @staticmethod
    def get_priority_order(priority: str) -> int:
        """
        Get numeric order for priority (for sorting).

        Args:
            priority: Priority string

        Returns:
            Numeric order (1=High, 2=Medium, 3=Low)
        """
        order_map = {
            PriorityLevel.HIGH.value: 1,
            PriorityLevel.MEDIUM.value: 2,
            PriorityLevel.LOW.value: 3
        }
        return order_map.get(priority, 2)

    @staticmethod
    def compare_priorities(priority1: str, priority2: str) -> int:
        """
        Compare two priorities.

        Args:
            priority1: First priority
            priority2: Second priority

        Returns:
            -1 if priority1 > priority2 (higher priority)
            0 if equal
            1 if priority1 < priority2 (lower priority)
        """
        order1 = PriorityService.get_priority_order(priority1)
        order2 = PriorityService.get_priority_order(priority2)

        if order1 < order2:
            return -1
        elif order1 > order2:
            return 1
        else:
            return 0


def validate_priority(priority: str) -> str:
    """
    Convenience function to validate and normalize priority.

    Args:
        priority: Priority string to validate

    Returns:
        Normalized priority string

    Raises:
        ValueError: If priority is invalid
    """
    service = PriorityService()
    return service.normalize_priority(priority)


def get_default_priority() -> str:
    """
    Convenience function to get default priority.

    Returns:
        Default priority value
    """
    return PriorityService.get_default_priority()
