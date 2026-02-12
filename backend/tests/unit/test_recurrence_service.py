"""
Unit tests for recurrence date calculation service.

Tests Daily, Weekly, and Monthly recurrence patterns with edge cases.
"""

import pytest
from datetime import datetime, timedelta
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.services.recurrence_service import (
    calculate_next_due_date,
    calculate_next_occurrence_from_completion,
    get_recurrence_description
)


class TestDailyRecurrence:
    """Test Daily recurrence pattern calculations."""

    def test_daily_recurrence_basic(self):
        """Test basic daily recurrence calculation."""
        current_date = datetime(2026, 2, 11, 10, 0, 0)
        base_time = datetime(2026, 2, 11, 9, 0, 0)

        next_date = calculate_next_due_date(
            recurrence='Daily',
            current_date=current_date,
            base_time=base_time
        )

        expected = datetime(2026, 2, 12, 9, 0, 0)
        assert next_date == expected

    def test_daily_recurrence_preserves_time(self):
        """Test that daily recurrence preserves the original time."""
        current_date = datetime(2026, 2, 11, 14, 30, 0)
        base_time = datetime(2026, 2, 11, 8, 15, 0)

        next_date = calculate_next_due_date(
            recurrence='Daily',
            current_date=current_date,
            base_time=base_time
        )

        assert next_date.hour == 8
        assert next_date.minute == 15
        assert next_date.day == 12

    def test_daily_recurrence_month_boundary(self):
        """Test daily recurrence crossing month boundary."""
        current_date = datetime(2026, 2, 28, 10, 0, 0)
        base_time = datetime(2026, 2, 28, 9, 0, 0)

        next_date = calculate_next_due_date(
            recurrence='Daily',
            current_date=current_date,
            base_time=base_time
        )

        expected = datetime(2026, 3, 1, 9, 0, 0)
        assert next_date == expected


class TestWeeklyRecurrence:
    """Test Weekly recurrence pattern calculations."""

    def test_weekly_recurrence_same_day(self):
        """Test weekly recurrence on the same day of week."""
        current_date = datetime(2026, 2, 11, 10, 0, 0)  # Wednesday
        base_time = datetime(2026, 2, 11, 9, 0, 0)

        next_date = calculate_next_due_date(
            recurrence='Weekly',
            current_date=current_date,
            base_time=base_time,
            recurrence_day_of_week=3  # Wednesday
        )

        expected = datetime(2026, 2, 18, 9, 0, 0)
        assert next_date == expected

    def test_weekly_recurrence_different_day(self):
        """Test weekly recurrence on a different day of week."""
        current_date = datetime(2026, 2, 11, 10, 0, 0)  # Wednesday
        base_time = datetime(2026, 2, 11, 9, 0, 0)

        next_date = calculate_next_due_date(
            recurrence='Weekly',
            current_date=current_date,
            base_time=base_time,
            recurrence_day_of_week=5  # Friday
        )

        expected = datetime(2026, 2, 13, 9, 0, 0)
        assert next_date == expected

    def test_weekly_recurrence_wraps_to_next_week(self):
        """Test weekly recurrence wrapping to next week."""
        current_date = datetime(2026, 2, 13, 10, 0, 0)  # Friday
        base_time = datetime(2026, 2, 13, 9, 0, 0)

        next_date = calculate_next_due_date(
            recurrence='Weekly',
            current_date=current_date,
            base_time=base_time,
            recurrence_day_of_week=1  # Monday
        )

        expected = datetime(2026, 2, 16, 9, 0, 0)
        assert next_date == expected

    def test_weekly_recurrence_missing_day_of_week(self):
        """Test weekly recurrence without day_of_week raises error."""
        current_date = datetime(2026, 2, 11, 10, 0, 0)
        base_time = datetime(2026, 2, 11, 9, 0, 0)

        with pytest.raises(ValueError, match="day_of_week required"):
            calculate_next_due_date(
                recurrence='Weekly',
                current_date=current_date,
                base_time=base_time
            )


class TestMonthlyRecurrence:
    """Test Monthly recurrence pattern calculations."""

    def test_monthly_recurrence_basic(self):
        """Test basic monthly recurrence calculation."""
        current_date = datetime(2026, 2, 15, 10, 0, 0)
        base_time = datetime(2026, 2, 15, 9, 0, 0)

        next_date = calculate_next_due_date(
            recurrence='Monthly',
            current_date=current_date,
            base_time=base_time,
            recurrence_day_of_month=15
        )

        expected = datetime(2026, 3, 15, 9, 0, 0)
        assert next_date == expected

    def test_monthly_recurrence_end_of_month(self):
        """Test monthly recurrence on day 31 in shorter months."""
        current_date = datetime(2026, 1, 31, 10, 0, 0)
        base_time = datetime(2026, 1, 31, 9, 0, 0)

        next_date = calculate_next_due_date(
            recurrence='Monthly',
            current_date=current_date,
            base_time=base_time,
            recurrence_day_of_month=31
        )

        # February only has 28 days, should use last day
        expected = datetime(2026, 2, 28, 9, 0, 0)
        assert next_date == expected

    def test_monthly_recurrence_february_to_march(self):
        """Test monthly recurrence from February to March."""
        current_date = datetime(2026, 2, 28, 10, 0, 0)
        base_time = datetime(2026, 2, 28, 9, 0, 0)

        next_date = calculate_next_due_date(
            recurrence='Monthly',
            current_date=current_date,
            base_time=base_time,
            recurrence_day_of_month=31
        )

        expected = datetime(2026, 3, 31, 9, 0, 0)
        assert next_date == expected

    def test_monthly_recurrence_missing_day_of_month(self):
        """Test monthly recurrence without day_of_month raises error."""
        current_date = datetime(2026, 2, 11, 10, 0, 0)
        base_time = datetime(2026, 2, 11, 9, 0, 0)

        with pytest.raises(ValueError, match="day_of_month required"):
            calculate_next_due_date(
                recurrence='Monthly',
                current_date=current_date,
                base_time=base_time
            )


class TestRecurrenceDescription:
    """Test recurrence description generation."""

    def test_daily_description(self):
        """Test daily recurrence description."""
        desc = get_recurrence_description('Daily')
        assert desc == "Repeats daily"

    def test_weekly_description_with_day(self):
        """Test weekly recurrence description with day."""
        desc = get_recurrence_description('Weekly', recurrence_day_of_week=1)
        assert "Monday" in desc

    def test_monthly_description_with_day(self):
        """Test monthly recurrence description with day."""
        desc = get_recurrence_description('Monthly', recurrence_day_of_month=15)
        assert "15th" in desc

    def test_invalid_recurrence_type(self):
        """Test invalid recurrence type."""
        with pytest.raises(ValueError):
            get_recurrence_description('Yearly')


class TestCompletionBasedRecurrence:
    """Test recurrence calculation from completion time."""

    def test_daily_from_completion(self):
        """Test daily recurrence calculated from completion time."""
        completion_time = datetime(2026, 2, 11, 15, 30, 0)

        next_date = calculate_next_occurrence_from_completion(
            recurrence='Daily',
            completion_time=completion_time
        )

        expected = datetime(2026, 2, 12, 15, 30, 0)
        assert next_date == expected

    def test_weekly_from_completion(self):
        """Test weekly recurrence calculated from completion time."""
        completion_time = datetime(2026, 2, 11, 15, 30, 0)  # Wednesday

        next_date = calculate_next_occurrence_from_completion(
            recurrence='Weekly',
            completion_time=completion_time,
            recurrence_day_of_week=3  # Wednesday
        )

        expected = datetime(2026, 2, 18, 15, 30, 0)
        assert next_date == expected
