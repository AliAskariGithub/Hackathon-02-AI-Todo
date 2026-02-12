"""
Recurrence Service - Date Calculation Logic

This service provides business logic for calculating next occurrence dates
for recurring tasks (Daily, Weekly, Monthly).

Key Features:
- Calculate next occurrence based on recurrence pattern
- Validate recurrence parameters
- Handle edge cases (month-end dates, leap years)
- Integration with RecurrencePattern model
"""

from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from ..models.recurrence import RecurrencePattern, RecurrenceType, create_recurrence_pattern


class RecurrenceService:
    """
    Service for managing recurring task date calculations.
    """

    @staticmethod
    def calculate_next_due_date(
        recurrence_type: str,
        current_due_date: datetime,
        recurrence_day_of_week: Optional[int] = None,
        recurrence_day_of_month: Optional[int] = None
    ) -> datetime:
        """
        Calculate the next due date for a recurring task.

        Args:
            recurrence_type: "Daily", "Weekly", or "Monthly"
            current_due_date: Current task due date
            recurrence_day_of_week: Day of week for Weekly (0-6)
            recurrence_day_of_month: Day of month for Monthly (1-31)

        Returns:
            Next due date

        Raises:
            ValueError: If recurrence parameters are invalid

        Example:
            >>> service = RecurrenceService()
            >>> next_date = service.calculate_next_due_date(
            ...     recurrence_type="Daily",
            ...     current_due_date=datetime(2026, 2, 11, 10, 0, 0)
            ... )
            >>> # Returns: datetime(2026, 2, 12, 10, 0, 0)
        """
        # Create recurrence pattern
        pattern = create_recurrence_pattern(
            recurrence_type=recurrence_type,
            day_of_week=recurrence_day_of_week,
            day_of_month=recurrence_day_of_month
        )

        # Calculate next occurrence
        return pattern.calculate_next_occurrence(
            current_date=current_due_date,
            base_time=current_due_date
        )

    @staticmethod
    def calculate_next_occurrence_from_completion(
        recurrence_type: str,
        completion_time: datetime,
        original_due_date: Optional[datetime] = None,
        recurrence_day_of_week: Optional[int] = None,
        recurrence_day_of_month: Optional[int] = None
    ) -> datetime:
        """
        Calculate the next occurrence date based on task completion time.

        This method is used when a recurring task is completed to determine
        when the next instance should be due.

        Args:
            recurrence_type: "Daily", "Weekly", or "Monthly"
            completion_time: When the task was completed
            original_due_date: Original due date (used to preserve time)
            recurrence_day_of_week: Day of week for Weekly (0-6)
            recurrence_day_of_month: Day of month for Monthly (1-31)

        Returns:
            Next occurrence date

        Example:
            >>> service = RecurrenceService()
            >>> # Task completed on Feb 11, original due date was Feb 10 at 10:00 AM
            >>> next_date = service.calculate_next_occurrence_from_completion(
            ...     recurrence_type="Daily",
            ...     completion_time=datetime(2026, 2, 11, 15, 30, 0),
            ...     original_due_date=datetime(2026, 2, 10, 10, 0, 0)
            ... )
            >>> # Returns: datetime(2026, 2, 12, 10, 0, 0)
        """
        # Create recurrence pattern
        pattern = create_recurrence_pattern(
            recurrence_type=recurrence_type,
            day_of_week=recurrence_day_of_week,
            day_of_month=recurrence_day_of_month
        )

        # Use original due date time if available, otherwise use completion time
        time_to_preserve = original_due_date or completion_time

        # Calculate next occurrence from completion time
        return pattern.calculate_next_occurrence(
            current_date=completion_time,
            base_time=time_to_preserve
        )

    @staticmethod
    def validate_recurrence_parameters(
        recurrence_type: str,
        recurrence_day_of_week: Optional[int] = None,
        recurrence_day_of_month: Optional[int] = None
    ) -> bool:
        """
        Validate recurrence parameters.

        Args:
            recurrence_type: "Daily", "Weekly", or "Monthly"
            recurrence_day_of_week: Day of week for Weekly (0-6)
            recurrence_day_of_month: Day of month for Monthly (1-31)

        Returns:
            True if parameters are valid

        Raises:
            ValueError: If parameters are invalid
        """
        # Validate recurrence type
        if recurrence_type not in ['Daily', 'Weekly', 'Monthly']:
            raise ValueError(f"Invalid recurrence type: {recurrence_type}")

        # Validate Weekly parameters
        if recurrence_type == 'Weekly':
            if recurrence_day_of_week is None:
                raise ValueError("recurrence_day_of_week is required for Weekly recurrence")
            if not (0 <= recurrence_day_of_week <= 6):
                raise ValueError("recurrence_day_of_week must be between 0 and 6")

        # Validate Monthly parameters
        if recurrence_type == 'Monthly':
            if recurrence_day_of_month is None:
                raise ValueError("recurrence_day_of_month is required for Monthly recurrence")
            if not (1 <= recurrence_day_of_month <= 31):
                raise ValueError("recurrence_day_of_month must be between 1 and 31")

        return True

    @staticmethod
    def get_recurrence_description(
        recurrence_type: str,
        recurrence_day_of_week: Optional[int] = None,
        recurrence_day_of_month: Optional[int] = None
    ) -> str:
        """
        Get a human-readable description of the recurrence pattern.

        Args:
            recurrence_type: "Daily", "Weekly", or "Monthly"
            recurrence_day_of_week: Day of week for Weekly (0-6)
            recurrence_day_of_month: Day of month for Monthly (1-31)

        Returns:
            Human-readable description

        Example:
            >>> service = RecurrenceService()
            >>> desc = service.get_recurrence_description("Daily")
            >>> # Returns: "Every day"
            >>> desc = service.get_recurrence_description("Weekly", recurrence_day_of_week=0)
            >>> # Returns: "Every Monday"
            >>> desc = service.get_recurrence_description("Monthly", recurrence_day_of_month=15)
            >>> # Returns: "Every month on the 15th"
        """
        if recurrence_type == 'Daily':
            return "Every day"

        if recurrence_type == 'Weekly':
            day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            if recurrence_day_of_week is not None:
                return f"Every {day_names[recurrence_day_of_week]}"
            return "Every week"

        if recurrence_type == 'Monthly':
            if recurrence_day_of_month is not None:
                # Add ordinal suffix (1st, 2nd, 3rd, etc.)
                suffix = 'th'
                if recurrence_day_of_month in [1, 21, 31]:
                    suffix = 'st'
                elif recurrence_day_of_month in [2, 22]:
                    suffix = 'nd'
                elif recurrence_day_of_month in [3, 23]:
                    suffix = 'rd'
                return f"Every month on the {recurrence_day_of_month}{suffix}"
            return "Every month"

        return "Unknown recurrence pattern"

    @staticmethod
    def should_generate_next_instance(
        task_status: str,
        has_recurrence: bool
    ) -> bool:
        """
        Determine if a next recurring instance should be generated.

        Args:
            task_status: Current task status
            has_recurrence: Whether task has recurrence pattern

        Returns:
            True if next instance should be generated

        Example:
            >>> service = RecurrenceService()
            >>> should_generate = service.should_generate_next_instance(
            ...     task_status="completed",
            ...     has_recurrence=True
            ... )
            >>> # Returns: True
        """
        # Only generate next instance if:
        # 1. Task is completed
        # 2. Task has a recurrence pattern
        return task_status == "completed" and has_recurrence


# Module-level convenience functions for backward compatibility
def calculate_next_due_date(
    recurrence: str,
    current_date: datetime,
    base_time: Optional[datetime] = None,
    recurrence_day_of_week: Optional[int] = None,
    recurrence_day_of_month: Optional[int] = None
) -> datetime:
    """Calculate next due date for a recurring task."""
    try:
        # Create recurrence pattern
        pattern = create_recurrence_pattern(
            recurrence_type=recurrence,
            day_of_week=recurrence_day_of_week,
            day_of_month=recurrence_day_of_month
        )
    except Exception as e:
        # Convert Pydantic ValidationError to ValueError for backward compatibility
        error_msg = str(e)
        if "day_of_week" in error_msg and "required" in error_msg:
            raise ValueError("day_of_week required for Weekly recurrence")
        elif "day_of_month" in error_msg and "required" in error_msg:
            raise ValueError("day_of_month required for Monthly recurrence")
        else:
            raise ValueError(str(e))

    # Use base_time if provided, otherwise use current_date
    time_to_preserve = base_time if base_time is not None else current_date

    # Calculate next occurrence
    return pattern.calculate_next_occurrence(
        current_date=current_date,
        base_time=time_to_preserve
    )


def calculate_next_occurrence_from_completion(
    recurrence: str,
    completion_time: datetime,
    original_due_date: Optional[datetime] = None,
    recurrence_day_of_week: Optional[int] = None,
    recurrence_day_of_month: Optional[int] = None
) -> datetime:
    """Calculate next occurrence from completion time."""
    return RecurrenceService.calculate_next_occurrence_from_completion(
        recurrence_type=recurrence,
        completion_time=completion_time,
        original_due_date=original_due_date,
        recurrence_day_of_week=recurrence_day_of_week,
        recurrence_day_of_month=recurrence_day_of_month
    )


def get_recurrence_description(
    recurrence: str,
    recurrence_day_of_week: Optional[int] = None,
    recurrence_day_of_month: Optional[int] = None
) -> str:
    """Get human-readable recurrence description."""
    # Validate recurrence type first
    if recurrence not in ['Daily', 'Weekly', 'Monthly']:
        raise ValueError(f"Invalid recurrence type: {recurrence}")

    if recurrence == 'Daily':
        return "Repeats daily"

    if recurrence == 'Weekly':
        # Sunday-first indexing: 0=Sunday, 1=Monday, ..., 6=Saturday
        day_names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        if recurrence_day_of_week is not None:
            return f"Repeats weekly on {day_names[recurrence_day_of_week]}"
        return "Repeats weekly"

    if recurrence == 'Monthly':
        if recurrence_day_of_month is not None:
            # Add ordinal suffix (1st, 2nd, 3rd, etc.)
            suffix = 'th'
            if recurrence_day_of_month in [1, 21, 31]:
                suffix = 'st'
            elif recurrence_day_of_month in [2, 22]:
                suffix = 'nd'
            elif recurrence_day_of_month in [3, 23]:
                suffix = 'rd'
            return f"Repeats monthly on the {recurrence_day_of_month}{suffix}"
        return "Repeats monthly"

    return "Unknown recurrence pattern"
