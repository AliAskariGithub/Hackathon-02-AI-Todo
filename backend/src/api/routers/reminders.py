"""
API endpoints for reminder management.

Handles reminder scheduling, retrieval, cancellation, and Dapr Jobs callbacks.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from backend.src.database import get_session
from backend.src.models.reminder import Reminder, ReminderCreate, ReminderRead
from backend.src.services.reminder_service import ReminderService
from backend.src.services.reminder_callback_service import process_reminder_callback
from backend.src.middleware.correlation import get_correlation_id_uuid
from backend.src.deps import get_current_user


router = APIRouter(prefix="/api/reminders", tags=["reminders"])


@router.post("", response_model=ReminderRead, status_code=status.HTTP_201_CREATED)
async def create_reminder(
    reminder_data: ReminderCreate,
    db: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
    correlation_id: UUID = Depends(get_correlation_id_uuid)
):
    """
    Schedule a new reminder using Dapr Jobs API.

    - **task_id**: The task to remind about
    - **scheduled_time**: When to send the reminder (ISO 8601 format)
    - **user_id**: The user to remind (must match authenticated user)
    """
    user_id = UUID(current_user["id"])

    # Verify user_id matches authenticated user
    if reminder_data.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create reminder for another user"
        )

    service = ReminderService(db)

    try:
        reminder = await service.schedule_reminder(
            task_id=reminder_data.task_id,
            user_id=user_id,
            scheduled_time=reminder_data.scheduled_time,
            correlation_id=correlation_id
        )
        return reminder
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("", response_model=List[ReminderRead])
async def get_reminders(
    task_id: Optional[UUID] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """
    Get reminders for the authenticated user with optional filtering.

    - **task_id**: Filter by task ID
    - **status**: Filter by status (scheduled/sent/cancelled)
    """
    user_id = UUID(current_user["id"])
    service = ReminderService(db)

    reminders = service.get_reminders(
        user_id=user_id,
        task_id=task_id,
        status=status
    )

    return reminders


@router.get("/{reminder_id}", response_model=ReminderRead)
async def get_reminder(
    reminder_id: UUID,
    db: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """
    Get a specific reminder by ID.
    """
    user_id = UUID(current_user["id"])
    service = ReminderService(db)

    reminder = service.get_reminder_by_id(reminder_id, user_id)
    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found"
        )

    return reminder


@router.delete("/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_reminder(
    reminder_id: UUID,
    db: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """
    Cancel a scheduled reminder and delete the Dapr Job.
    """
    user_id = UUID(current_user["id"])
    service = ReminderService(db)

    try:
        await service.cancel_reminder(reminder_id, user_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/callback/{reminder_id}")
async def reminder_callback(
    reminder_id: UUID,
    callback_data: dict,
    db: Session = Depends(get_session)
):
    """
    Callback endpoint for Dapr Jobs API.

    This endpoint is called by Dapr Jobs when a reminder fires.
    No authentication required as it's called by Dapr sidecar.
    """
    result = await process_reminder_callback(
        db=db,
        reminder_id=reminder_id,
        callback_data=callback_data
    )

    if result["status"] == "error":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result
        )

    return result
