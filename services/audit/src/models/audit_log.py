"""
Audit Log Model

Represents a system event captured for audit trail purposes.
Stores all events chronologically for debugging, compliance, and analytics.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel, JSON, Column
from sqlalchemy import Index


class AuditLogBase(SQLModel):
    """Base Audit Log model with shared fields."""
    event_type: str = Field(index=True)
    event_payload: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    user_id: Optional[UUID] = Field(default=None, index=True)
    correlation_id: Optional[UUID] = Field(default=None, index=True)
    service_name: str = Field(default="unknown", index=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)


class AuditLog(AuditLogBase, table=True):
    """Audit Log entity stored in database."""
    __tablename__ = "audit_logs"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Composite indexes for common query patterns
    __table_args__ = (
        Index('idx_audit_user_timestamp', 'user_id', 'timestamp'),
        Index('idx_audit_event_timestamp', 'event_type', 'timestamp'),
        Index('idx_audit_correlation', 'correlation_id'),
        Index('idx_audit_service_timestamp', 'service_name', 'timestamp'),
    )


class AuditLogCreate(AuditLogBase):
    """Schema for creating a new audit log entry."""
    pass


class AuditLogRead(AuditLogBase):
    """Schema for reading an audit log entry."""
    id: UUID
    created_at: datetime


class AuditLogQuery(SQLModel):
    """Schema for querying audit logs with filters."""
    user_id: Optional[UUID] = None
    event_type: Optional[str] = None
    correlation_id: Optional[UUID] = None
    service_name: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


class AuditStats(SQLModel):
    """Schema for audit statistics."""
    total_events: int
    events_by_type: Dict[str, int]
    events_by_service: Dict[str, int]
    unique_users: int
    unique_correlations: int
    date_range: Dict[str, str]
