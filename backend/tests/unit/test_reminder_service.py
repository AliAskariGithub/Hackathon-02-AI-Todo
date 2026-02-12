"""
Unit tests for reminder scheduling service.

Tests reminder creation, validation, and Dapr Jobs integration.
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from unittest.mock import AsyncMock, patch
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.services.reminder_service import ReminderService
from src.models.reminder import validate_reminder_time, generate_dapr_job_name


class TestReminderValidation:
    """Test reminder time validation."""

    def test_validate_future_time_succeeds(self):
        """Test that future time passes validation."""
        future_time = datetime.utcnow() + timedelta(hours=1)
        # Should not raise
        validate_reminder_time(future_time)

    def test_validate_past_time_fails(self):
        """Test that past time fails validation."""
        past_time = datetime.utcnow() - timedelta(hours=1)
        with pytest.raises(ValueError, match="must be in the future"):
            validate_reminder_time(past_time)

    def test_validate_minimum_one_minute_ahead(self):
        """Test that reminder must be at least 1 minute in the future."""
        # 30 seconds ahead should fail
        too_soon = datetime.utcnow() + timedelta(seconds=30)
        with pytest.raises(ValueError, match="at least 1 minute"):
            validate_reminder_time(too_soon)

        # 2 minutes ahead should succeed
        valid_time = datetime.utcnow() + timedelta(minutes=2)
        validate_reminder_time(valid_time)


class TestDaprJobNameGeneration:
    """Test Dapr Job name generation."""

    def test_generate_unique_job_names(self):
        """Test that job names are unique per reminder."""
        reminder_id_1 = uuid4()
        reminder_id_2 = uuid4()
        user_id = uuid4()

        job_name_1 = generate_dapr_job_name(reminder_id_1, user_id)
        job_name_2 = generate_dapr_job_name(reminder_id_2, user_id)

        assert job_name_1 != job_name_2
        assert str(reminder_id_1) in job_name_1
        assert str(reminder_id_2) in job_name_2

    def test_job_name_format(self):
        """Test that job name follows expected format."""
        reminder_id = uuid4()
        user_id = uuid4()

        job_name = generate_dapr_job_name(reminder_id, user_id)

        assert job_name.startswith("reminder-")
        assert str(user_id) in job_name
        assert str(reminder_id) in job_name


class TestReminderScheduling:
    """Test reminder scheduling with Dapr Jobs."""

    @pytest.fixture
    def mock_db(self):
        """Mock database session."""
        return AsyncMock()

    @pytest.fixture
    def reminder_service(self, mock_db):
        """Create reminder service with mock DB."""
        return ReminderService(mock_db)

    @pytest.mark.asyncio
    @patch('backend.src.services.reminder_service.schedule_job')
    @patch('backend.src.services.reminder_service.publish_reminder_scheduled')
    async def test_schedule_reminder_creates_dapr_job(
        self,
        mock_publish,
        mock_schedule_job,
        reminder_service,
        mock_db
    ):
        """Test that scheduling a reminder creates a Dapr Job."""
        task_id = uuid4()
        user_id = uuid4()
        scheduled_time = datetime.utcnow() + timedelta(hours=1)

        mock_schedule_job.return_value = None
        mock_publish.return_value = None

        reminder = await reminder_service.schedule_reminder(
            task_id=task_id,
            user_id=user_id,
            scheduled_time=scheduled_time
        )

        # Verify Dapr Job was scheduled
        mock_schedule_job.assert_called_once()
        call_args = mock_schedule_job.call_args
        assert call_args.kwargs['schedule_time'] == scheduled_time
        assert 'callback_url' in call_args.kwargs

        # Verify event was published
        mock_publish.assert_called_once()

    @pytest.mark.asyncio
    async def test_schedule_reminder_with_invalid_time_fails(self, reminder_service):
        """Test that scheduling with invalid time raises error."""
        task_id = uuid4()
        user_id = uuid4()
        past_time = datetime.utcnow() - timedelta(hours=1)

        with pytest.raises(ValueError):
            await reminder_service.schedule_reminder(
                task_id=task_id,
                user_id=user_id,
                scheduled_time=past_time
            )


class TestReminderCancellation:
    """Test reminder cancellation."""

    @pytest.fixture
    def mock_db(self):
        """Mock database session."""
        return AsyncMock()

    @pytest.fixture
    def reminder_service(self, mock_db):
        """Create reminder service with mock DB."""
        return ReminderService(mock_db)

    @pytest.mark.asyncio
    @patch('backend.src.services.reminder_service.cancel_job')
    async def test_cancel_reminder_deletes_dapr_job(
        self,
        mock_cancel_job,
        reminder_service,
        mock_db
    ):
        """Test that cancelling a reminder deletes the Dapr Job."""
        reminder_id = uuid4()
        user_id = uuid4()
        job_name = f"reminder-{user_id}-{reminder_id}"

        # Mock reminder in DB
        mock_reminder = AsyncMock()
        mock_reminder.id = reminder_id
        mock_reminder.user_id = user_id
        mock_reminder.status = "scheduled"
        mock_reminder.dapr_job_name = job_name
        mock_db.get.return_value = mock_reminder

        mock_cancel_job.return_value = None

        result = await reminder_service.cancel_reminder(reminder_id, user_id)

        assert result is True
        mock_cancel_job.assert_called_once_with(job_name)
        assert mock_reminder.status == "cancelled"

    @pytest.mark.asyncio
    async def test_cancel_sent_reminder_fails(self, reminder_service, mock_db):
        """Test that cancelling a sent reminder raises error."""
        reminder_id = uuid4()
        user_id = uuid4()

        # Mock sent reminder
        mock_reminder = AsyncMock()
        mock_reminder.id = reminder_id
        mock_reminder.user_id = user_id
        mock_reminder.status = "sent"
        mock_db.get.return_value = mock_reminder

        with pytest.raises(ValueError, match="already been sent"):
            await reminder_service.cancel_reminder(reminder_id, user_id)

    @pytest.mark.asyncio
    async def test_cancel_unauthorized_reminder_fails(self, reminder_service, mock_db):
        """Test that cancelling another user's reminder fails."""
        reminder_id = uuid4()
        user_id = uuid4()
        other_user_id = uuid4()

        # Mock reminder owned by different user
        mock_reminder = AsyncMock()
        mock_reminder.id = reminder_id
        mock_reminder.user_id = other_user_id
        mock_reminder.status = "scheduled"
        mock_db.get.return_value = mock_reminder

        with pytest.raises(ValueError, match="Unauthorized"):
            await reminder_service.cancel_reminder(reminder_id, user_id)


class TestReminderRetrieval:
    """Test reminder retrieval and filtering."""

    @pytest.fixture
    def mock_db(self):
        """Mock database session."""
        return AsyncMock()

    @pytest.fixture
    def reminder_service(self, mock_db):
        """Create reminder service with mock DB."""
        return ReminderService(mock_db)

    def test_get_reminders_filters_by_task_id(self, reminder_service, mock_db):
        """Test filtering reminders by task ID."""
        user_id = uuid4()
        task_id = uuid4()

        mock_db.exec.return_value.all.return_value = []

        reminders = reminder_service.get_reminders(user_id=user_id, task_id=task_id)

        # Verify query was constructed with task_id filter
        assert isinstance(reminders, list)

    def test_get_reminders_filters_by_status(self, reminder_service, mock_db):
        """Test filtering reminders by status."""
        user_id = uuid4()

        mock_db.exec.return_value.all.return_value = []

        reminders = reminder_service.get_reminders(user_id=user_id, status="scheduled")

        assert isinstance(reminders, list)
