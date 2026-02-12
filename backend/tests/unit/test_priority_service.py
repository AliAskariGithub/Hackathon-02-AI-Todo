"""
Unit tests for priority service.

Tests priority validation, normalization, and comparison.
"""

import pytest
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.services.priority_service import (
    PriorityService,
    PriorityLevel,
    validate_priority,
    get_default_priority
)


class TestPriorityValidation:
    """Test priority validation."""

    def test_validate_high_priority(self):
        """Test that High priority is valid."""
        assert PriorityService.validate_priority("High") is True

    def test_validate_medium_priority(self):
        """Test that Medium priority is valid."""
        assert PriorityService.validate_priority("Medium") is True

    def test_validate_low_priority(self):
        """Test that Low priority is valid."""
        assert PriorityService.validate_priority("Low") is True

    def test_validate_invalid_priority(self):
        """Test that invalid priority is rejected."""
        assert PriorityService.validate_priority("Critical") is False
        assert PriorityService.validate_priority("Urgent") is False
        assert PriorityService.validate_priority("") is False


class TestPriorityNormalization:
    """Test priority normalization."""

    def test_normalize_lowercase(self):
        """Test normalizing lowercase priority."""
        assert PriorityService.normalize_priority("high") == "High"
        assert PriorityService.normalize_priority("medium") == "Medium"
        assert PriorityService.normalize_priority("low") == "Low"

    def test_normalize_uppercase(self):
        """Test normalizing uppercase priority."""
        assert PriorityService.normalize_priority("HIGH") == "High"
        assert PriorityService.normalize_priority("MEDIUM") == "Medium"
        assert PriorityService.normalize_priority("LOW") == "Low"

    def test_normalize_mixed_case(self):
        """Test normalizing mixed case priority."""
        assert PriorityService.normalize_priority("HiGh") == "High"
        assert PriorityService.normalize_priority("MeDiUm") == "Medium"

    def test_normalize_invalid_raises_error(self):
        """Test that normalizing invalid priority raises error."""
        with pytest.raises(ValueError, match="Invalid priority"):
            PriorityService.normalize_priority("Critical")


class TestPriorityOrdering:
    """Test priority ordering and comparison."""

    def test_get_priority_order(self):
        """Test getting numeric order for priorities."""
        assert PriorityService.get_priority_order("High") == 1
        assert PriorityService.get_priority_order("Medium") == 2
        assert PriorityService.get_priority_order("Low") == 3

    def test_compare_priorities(self):
        """Test comparing two priorities."""
        # High > Medium
        assert PriorityService.compare_priorities("High", "Medium") == -1

        # Medium > Low
        assert PriorityService.compare_priorities("Medium", "Low") == -1

        # Low < High
        assert PriorityService.compare_priorities("Low", "High") == 1

        # Equal priorities
        assert PriorityService.compare_priorities("High", "High") == 0

    def test_priority_sorting(self):
        """Test that priorities can be sorted correctly."""
        priorities = ["Low", "High", "Medium", "High", "Low"]
        sorted_priorities = sorted(
            priorities,
            key=lambda p: PriorityService.get_priority_order(p)
        )

        assert sorted_priorities == ["High", "High", "Medium", "Low", "Low"]


class TestDefaultPriority:
    """Test default priority behavior."""

    def test_get_default_priority(self):
        """Test that default priority is Medium."""
        assert PriorityService.get_default_priority() == "Medium"
        assert get_default_priority() == "Medium"

    def test_default_priority_is_valid(self):
        """Test that default priority is a valid priority."""
        default = PriorityService.get_default_priority()
        assert PriorityService.validate_priority(default) is True


class TestPriorityEnum:
    """Test PriorityLevel enum."""

    def test_enum_values(self):
        """Test that enum has correct values."""
        assert PriorityLevel.HIGH.value == "High"
        assert PriorityLevel.MEDIUM.value == "Medium"
        assert PriorityLevel.LOW.value == "Low"

    def test_enum_iteration(self):
        """Test iterating over priority levels."""
        priorities = [p.value for p in PriorityLevel]
        assert len(priorities) == 3
        assert "High" in priorities
        assert "Medium" in priorities
        assert "Low" in priorities


class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_validate_priority_function(self):
        """Test validate_priority convenience function."""
        assert validate_priority("high") == "High"
        assert validate_priority("MEDIUM") == "Medium"

        with pytest.raises(ValueError):
            validate_priority("Invalid")

    def test_get_default_priority_function(self):
        """Test get_default_priority convenience function."""
        assert get_default_priority() == "Medium"
