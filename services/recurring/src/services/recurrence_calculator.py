"""
Recurrence Calculator Service

Calculates the next due date for recurring tasks based on their recurrence pattern.
Supports daily, weekly, and monthly recurrence patterns.
"""

from datetime import datetime, timedelta
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class RecurrenceCalculator:
    """
    Service for calculating next due dates for recurring tasks.
    """

    @staticmethod
    def calculate_next_due_date(
        current_due_date: datetime,
        recurrence: str,
        recurrence_day_of_week: Optional[int] = None,
        recurrence_day_of_month: Optional[int] = None
    ) -> datetime:
        """
        Calculate the next due date based on recurrence pattern.

        Args:
            current_due_date: The current/completed task's due date
            recurrence: Recurrence pattern ('Daily', 'Weekly', 'Monthly')
            recurrence_day_of_week: Day of week for weekly recurrence (0=Monday, 6=Sunday)
            recurrence_day_of_month: Day of month for monthly recurrence (1-31)

        Returns:
            The next due date as a datetime object

        Raises:
            ValueError: If recurrence pattern is invalid or required parameters are missing
        """
        if not recurrence:
            raise ValueError("Recurrence pattern is required")

        recurrence = recurrence.lower()

        if recurrence == 'daily':
            return RecurrenceCalculator._calculate_daily(current_due_date)
        elif recurrence == 'weekly':
            return RecurrenceCalculator._calculate_weekly(
                current_due_date,
                recurrence_day_of_week
            )
        elif recurrence == 'monthly':
            return RecurrenceCalculator._calculate_monthly(
                current_due_date,
                recurrence_day_of_month
            )
        else:
            raise ValueError(f"Invalid recurrence pattern: {recurrence}")

    @staticmethod
    def _calculate_daily(current_due_date: datetime) -> datetime:
        """
        Calculate next due date for daily recurrence.

        Args:
            current_due_date: The current task's due date

        Returns:
            Due date + 1 day
        """
        next_due_date = current_due_date + timedelta(days=1)
        logger.info(f"Daily recurrence: {current_due_date} -> {next_due_date}")
        return next_due_date

    @staticmethod
    def _calculate_weekly(
        current_due_date: datetime,
        recurrence_day_of_week: Optional[int]
    ) -> datetime:
        """
        Calculate next due date for weekly recurrence.

        Args:
            current_due_date: The current task's due date
            recurrence_day_of_week: Target day of week (0=Monday, 6=Sunday)

        Returns:
            Next occurrence of the specified day of week

        Raises:
            ValueError: If recurrence_day_of_week is not provided or invalid
        """
        if recurrence_day_of_week is None:
            raise ValueError("recurrence_day_of_week is required for weekly recurrence")

        if not 0 <= recurrence_day_of_week <= 6:
            raise ValueError(f"Invalid day of week: {recurrence_day_of_week}. Must be 0-6.")

        # Calculate days until next occurrence of target day
        current_day = current_due_date.weekday()
        days_ahead = recurrence_day_of_week - current_day

        # If target day is today or in the past this week, schedule for next week
        if days_ahead <= 0:
            days_ahead += 7

        next_due_date = current_due_date + timedelta(days=days_ahead)
        logger.info(
            f"Weekly recurrence (day {recurrence_day_of_week}): "
            f"{current_due_date} -> {next_due_date}"
        )
        return next_due_date

    @staticmethod
    def _calculate_monthly(
        current_due_date: datetime,
        recurrence_day_of_month: Optional[int]
    ) -> datetime:
        """
        Calculate next due date for monthly recurrence.

        Args:
            current_due_date: The current task's due date
            recurrence_day_of_month: Target day of month (1-31)

        Returns:
            Next occurrence of the specified day of month

        Raises:
            ValueError: If recurrence_day_of_month is not provided or invalid
        """
        if recurrence_day_of_month is None:
            raise ValueError("recurrence_day_of_month is required for monthly recurrence")

        if not 1 <= recurrence_day_of_month <= 31:
            raise ValueError(
                f"Invalid day of month: {recurrence_day_of_month}. Must be 1-31."
            )

        # Start with next month
        if current_due_date.month == 12:
            next_month = 1
            next_year = current_due_date.year + 1
        else:
            next_month = current_due_date.month + 1
            next_year = current_due_date.year

        # Handle months with fewer days (e.g., February, April)
        # If target day doesn't exist in next month, use last day of month
        try:
            next_due_date = current_due_date.replace(
                year=next_year,
                month=next_month,
                day=recurrence_day_of_month
            )
        except ValueError:
            # Day doesn't exist in this month (e.g., Feb 31)
            # Use last day of the month instead
            if next_month == 12:
                next_due_date = datetime(next_year, next_month, 31)
            else:
                # Get last day by going to first day of next month and subtracting 1 day
                first_of_next_month = datetime(next_year, next_month + 1, 1)
                next_due_date = first_of_next_month - timedelta(days=1)

            logger.warning(
                f"Day {recurrence_day_of_month} doesn't exist in month {next_month}, "
                f"using last day: {next_due_date.day}"
            )

        # Preserve time from original due date
        next_due_date = next_due_date.replace(
            hour=current_due_date.hour,
            minute=current_due_date.minute,
            second=current_due_date.second,
            microsecond=current_due_date.microsecond
        )

        logger.info(
            f"Monthly recurrence (day {recurrence_day_of_month}): "
            f"{current_due_date} -> {next_due_date}"
        )
        return next_due_date

    @staticmethod
    def validate_recurrence_pattern(
        recurrence: str,
        recurrence_day_of_week: Optional[int] = None,
        recurrence_day_of_month: Optional[int] = None
    ) -> bool:
        """
        Validate that a recurrence pattern has all required parameters.

        Args:
            recurrence: Recurrence pattern ('Daily', 'Weekly', 'Monthly')
            recurrence_day_of_week: Day of week for weekly recurrence
            recurrence_day_of_month: Day of month for monthly recurrence

        Returns:
            True if valid, False otherwise
        """
        try:
            recurrence = recurrence.lower()

            if recurrence == 'daily':
                return True
            elif recurrence == 'weekly':
                return recurrence_day_of_week is not None and 0 <= recurrence_day_of_week <= 6
            elif recurrence == 'monthly':
                return recurrence_day_of_month is not None and 1 <= recurrence_day_of_month <= 31
            else:
                return False
        except Exception:
            return False
