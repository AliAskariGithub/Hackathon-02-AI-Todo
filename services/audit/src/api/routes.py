"""
Audit Service API Routes

Provides endpoints for querying audit logs and statistics.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime
from uuid import UUID
from sqlmodel import Session
from ..models.audit_log import AuditLog, AuditLogRead, AuditLogQuery, AuditStats
from ..storage.audit_storage import AuditStorage

router = APIRouter(prefix="/audit", tags=["audit"])


def get_audit_storage(db: Session = Depends(get_db_session)) -> AuditStorage:
    """Dependency to get audit storage service."""
    return AuditStorage(db_session=db)


@router.get("/logs", response_model=List[AuditLogRead])
async def get_audit_logs(
    user_id: Optional[UUID] = Query(None, description="Filter by user ID"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    correlation_id: Optional[UUID] = Query(None, description="Filter by correlation ID"),
    service_name: Optional[str] = Query(None, description="Filter by service name"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date (ISO 8601)"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date (ISO 8601)"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    storage: AuditStorage = Depends(get_audit_storage)
) -> List[AuditLogRead]:
    """
    Query audit logs with filtering and pagination.

    Returns audit log entries matching the specified filters, ordered by timestamp descending.
    """
    try:
        query = AuditLogQuery(
            user_id=user_id,
            event_type=event_type,
            correlation_id=correlation_id,
            service_name=service_name,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset
        )

        audit_logs = await storage.query_audit_logs(query)
        return [AuditLogRead.from_orm(log) for log in audit_logs]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error querying audit logs: {str(e)}"
        )


@router.get("/stats", response_model=AuditStats)
async def get_audit_statistics(
    start_date: Optional[datetime] = Query(None, description="Filter by start date (ISO 8601)"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date (ISO 8601)"),
    storage: AuditStorage = Depends(get_audit_storage)
) -> AuditStats:
    """
    Get audit log statistics.

    Returns aggregated statistics about audit logs including:
    - Total event count
    - Events by type
    - Events by service
    - Unique users
    - Unique correlations
    - Date range
    """
    try:
        stats = await storage.get_audit_statistics(
            start_date=start_date,
            end_date=end_date
        )
        return stats

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting audit statistics: {str(e)}"
        )


@router.get("/validate-chronology")
async def validate_chronological_order(
    start_date: datetime = Query(..., description="Start date for validation (ISO 8601)"),
    end_date: datetime = Query(..., description="End date for validation (ISO 8601)"),
    storage: AuditStorage = Depends(get_audit_storage)
) -> dict:
    """
    Validate that audit logs are in chronological order with no gaps.

    Returns validation results including:
    - Whether logs are in chronological order
    - Total number of logs checked
    - Number of gaps found
    - Details of any gaps
    """
    try:
        validation_result = await storage.validate_chronological_order(
            start_date=start_date,
            end_date=end_date
        )
        return validation_result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error validating chronological order: {str(e)}"
        )


@router.get("/health")
async def health_check() -> dict:
    """
    Health check endpoint for audit service.
    """
    return {
        "status": "healthy",
        "service": "audit-service",
        "timestamp": datetime.utcnow().isoformat()
    }


# Placeholder for database session dependency
# This should be implemented based on your database setup
def get_db_session():
    """Get database session - implement based on your setup."""
    # TODO: Implement database session management
    pass
