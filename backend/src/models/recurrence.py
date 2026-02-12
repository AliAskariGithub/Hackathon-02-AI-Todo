"""
Recurrence Pattern Model and Calculation Logic

This module defines the RecurrencePattern model and provides calculation logic
for generating next occurrence dates for Daily, Weekly, and Monthly recurring tasks.

Key Features:
- Daily recurrence: Next day at same time
- Weekly recurrence: Next occurrence on specified day of week
- Monthly recurrence: Next occurrence on specified day of month
- Edge case handling: Month-end dates, leap years, invalid dates
"""

from datetime import datetime, timedelta
from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class RecurrenceType(str, Enum):
    """Recurrence type enumeration."""
    DAILY = "Daily"
    WEEKLY = "Weekly"
    MONTHLY = "Monthly"


class RecurrencePattern(BaseModel):
    """
    Recurrence pattern for recurring tasks.

    This model encapsulates the recurrence logic and provides methods
    to calculate the next occurrence date.
    """
    recurrence_type: RecurrenceType = Field(
        ...,
        description="Type of recurrence (Daily, Weekly, Monthly)"
    )
    day_of_week: Optional[int] = Field(
        default=None,
        ge=0,
        le=6,
        description="Day of week for Weekly recurrence (0=Sunday, 1=Monday, ..., 6=Saturday)"
    )
    day_of_month: Optional[int] = Field(
        default=None,
        ge=1,
        le=31,
        description="Day of month for Monthly recurrence (1-31)"
    )

    @field_validator('day_of_week')
    @classmethod
    def validate_day_of_week(cls, v, info):
        """Validate day_of_week is provided for Weekly recurrence."""
        if info.data.get('recurrence_type') == RecurrenceType.WEEKLY and v is None:
            raise ValueError("day_of_week is required for Weekly recurrence")
        if info.data.get('recurrence_type') != RecurrenceType.WEEKLY and v is not None:
            raise ValueError("day_of_week should only be set for Weekly recurrence")
        return v

    @field_validator('day_of_month')
    @classmethod
    def validate_day_of_month(cls, v, info):
        """Validate day_of_month is provided for Monthly recurrence."""
        if info.data.get('recurrence_type') == RecurrenceType.MONTHLY and v is None:
            raise ValueError("day_of_month is required for Monthly recurrence")
        if info.data.get('recurrence_type') != RecurrenceType.MONTHLY and v is not None:
            raise ValueError("day_of_month should only be set for Monthly recurrence")
        return v

    def calculate_next_occurrence(
        self,
        current_date: datetime,
        base_time: Optional[datetime] = None
    ) -> datetime:
        """
        Calculate the next occurrence date based on recurrence pattern.

        Args:
            current_date: Current date/time (typically task completion time)
            base_time: Optional base time to preserve (hour, minute, second)
                      If not provided, uses current_date's time

        Returns:
            Next occurrence datetime

        Example:
            >>> pattern = RecurrencePattern(recurrence_type=RecurrenceType.DAILY)
            >>> next_date = pattern.calculate_next_occurrence(datetime(2026, 2, 11, 10, 0, 0))
            >>> # Returns: datetime(2026, 2, 12, 10, 0, 0)
        """
        # Use base_time if provided, otherwise use current_date's time
        time_to_preserve = base_time or current_date

        if self.recurrence_type == RecurrenceType.DAILY:
            return self._calculate_daily(current_date, time_to_preserve)
        elif self.recurrence_type == RecurrenceType.WEEKLY:
            return self._calculate_weekly(current_date, time_to_preserve)
        elif self.recurrence_type == RecurrenceType.MONTHLY:
            return self._calculate_monthly(current_date, time_to_preserve)
        else:
            raise ValueError(f"Unknown recurrence type: {self.recurrence_type}")

    def _calculate_daily(
        self,
        current_date: datetime,
        time_to_preserve: datetime
    ) -> datetime:
        """
        Calculate next occurrence for Daily recurrence.

        Simply adds 1 day to the current date while preserving the time.

        Args:
            current_date: Current date
            time_to_preserve: Time to preserve (hour, minute, second)

        Returns:
            Next day at same time
        """
        next_date = current_date + timedelta(days=1)
        return next_date.replace(
            hour=time_to_preserve.hour,
            minute=time_to_preserve.minute,
            second=time_to_preserve.second,
            microsecond=time_to_preserve.microsecond
        )

    def _calculate_weekly(
        self,
        current_date: datetime,
        time_to_preserve: datetime
    ) -> datetime:
        """
        Calculate next occurrence for Weekly recurrence.

        Finds the next occurrence of the specified day of week.
        Note: day_of_week uses Sunday-first indexing (0=Sunday, 1=Monday, ..., 6=Saturday)
        but Python's weekday() uses Monday-first (0=Monday, ..., 6=Sunday)

        Args:
            current_date: Current date
            time_to_preserve: Time to preserve (hour, minute, second)

        Returns:
            Next occurrence on specified day of week

        Example:
            If today is Wednesday and day_of_week is 1 (Monday in Sunday-first):
            - Convert to Monday-first: 1 -> 0 (Monday)
            - Calculate days until next Monday
        """
        if self.day_of_week is None:
            raise ValueError("day_of_week must be set for Weekly recurrence")

        # Convert from Sunday-first (0=Sunday) to Monday-first (0=Monday)
        # Sunday-first: 0=Sun, 1=Mon, 2=Tue, 3=Wed, 4=Thu, 5=Fri, 6=Sat
        # Monday-first: 0=Mon, 1=Tue, 2=Wed, 3=Thu, 4=Fri, 5=Sat, 6=Sun
        target_day_monday_first = (self.day_of_week - 1) % 7

        current_day_of_week = current_date.weekday()
        days_until_target = (target_day_monday_first - current_day_of_week) % 7

        # If target day is today, schedule for next week
        if days_until_target == 0:
            days_until_target = 7

        next_date = current_date + timedelta(days=days_until_target)
        return next_date.replace(
            hour=time_to_preserve.hour,
            minute=time_to_preserve.minute,
            second=time_to_preserve.second,
            microsecond=time_to_preserve.microsecond
        )

    def _calculate_monthly(
        self,
        current_date: datetime,
        time_to_preserve: datetime
    ) -> datetime:
        """
        Calculate next occurrence for Monthly recurrence.

        Finds the next occurrence of the specified day of month.
        Handles edge cases:
        - If day_of_month > days in target month, uses last day of month
        - Example: day_of_month=31 in February -> February 28/29

        Args:
            current_date: Current date
            time_to_preserve: Time to preserve (hour, minute, second)

        Returns:
            Next occurrence on specified day of month

        Example:
            If today is Feb 15 and day_of_month is 10:
            - Next occurrence: March 10
            If today is Feb 15 and day_of_month is 31:
            - Next occurrence: February 28/29 (last day of February)
        """
        if self.day_of_month is None:
            raise ValueError("day_of_month must be set for Monthly recurrence")

        # Start with next month
        if current_date.month == 12:
            next_year = current_date.year + 1
            next_month = 1
        else:
            next_year = current_date.year
            next_month = current_date.month + 1

        # Handle day_of_month > days in target month
        next_date = self._get_valid_date_for_month(
            next_year,
            next_month,
            self.day_of_month
        )

        return next_date.replace(
            hour=time_to_preserve.hour,
            minute=time_to_preserve.minute,
            second=time_to_preserve.second,
            microsecond=time_to_preserve.microsecond
        )

    def _get_valid_date_for_month(
        self,
        year: int,
        month: int,
        day: int
    ) -> datetime:
        """
        Get a valid date for the given year, month, and day.

        If the day is invalid for the month (e.g., Feb 31), returns the
        last valid day of that month.

        Args:
            year: Year
            month: Month (1-12)
            day: Day of month (1-31)

        Returns:
            Valid datetime for the given year/month/day
        """
        # Get the last day of the month
        if month == 12:
            next_month_first = datetime(year + 1, 1, 1)
        else:
            next_month_first = datetime(year, month + 1, 1)

        last_day_of_month = (next_month_first - timedelta(days=1)).day

        # Use the smaller of requested day or last day of month
        valid_day = min(day, last_day_of_month)

        return datetime(year, month, valid_day)


def create_recurrence_pattern(
    recurrence_type: str,
    day_of_week: Optional[int] = None,
    day_of_month: Optional[int] = None
) -> RecurrencePattern:
    """
    Factory function to create a RecurrencePattern.

    Args:
        recurrence_type: "Daily", "Weekly", or "Monthly"
        day_of_week: Day of week for Weekly (0-6)
        day_of_month: Day of month for Monthly (1-31)

    Returns:
        RecurrencePattern instance

    Example:
        >>> pattern = create_recurrence_pattern("Daily")
        >>> pattern = create_recurrence_pattern("Weekly", day_of_week=0)  # Monday
        >>> pattern = create_recurrence_pattern("Monthly", day_of_month=15)
    """
    return RecurrencePattern(
        recurrence_type=RecurrenceType(recurrence_type),
        day_of_week=day_of_week,
        day_of_month=day_of_month
    )
