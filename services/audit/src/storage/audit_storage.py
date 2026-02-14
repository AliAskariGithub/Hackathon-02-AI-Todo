"""
Audit Storage Service

Handles persistence of audit log entries to PostgreSQL database.
Provides query capabilities with filtering, pagination, and statistics.
"""

import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlmodel import select, func, Session
from sqlalchemy import and_, or_
from ..models.audit_log import AuditLog, AuditLogCreate, AuditLogQuery, AuditStats

logger = logging.getLogger(__name__)


class AuditStorage:
    """
    Service for persisting and querying audit logs.
    """

    def __init__(self, db_session: Session):
        """
        Initialize the storage service.

        Args:
            db_session: Database session
        """
        self.db = db_session

    async def store_audit_log(self, audit_data: AuditLogCreate) -> AuditLog:
        """
        Store an audit log entry in the database.

        Args:
            audit_data: Audit log data to store

        Returns:
            Created audit log entry

        Raises:
            Exception: If storage fails
        """
        try:
            audit_log = AuditLog(**audit_data.dict())
            self.db.add(audit_log)
            self.db.commit()
            self.db.refresh(audit_log)

            logger.info(
                f"Stored audit log: event_type={audit_log.event_type}, "
                f"correlation_id={audit_log.correlation_id}"
            )

            return audit_log

        except Exception as e:
            logger.error(f"Error storing audit log: {str(e)}")
            self.db.rollback()
            raise

    async def query_audit_logs(self, query: AuditLogQuery) -> List[AuditLog]:
        """
        Query audit logs with filtering and pagination.

        Args:
            query: Query parameters with filters

        Returns:
            List of audit log entries matching the query
        """
        try:
            # Build query with filters
            statement = select(AuditLog)

            # Apply filters
            filters = []

            if query.user_id:
                filters.append(AuditLog.user_id == query.user_id)

            if query.event_type:
                filters.append(AuditLog.event_type == query.event_type)

            if query.correlation_id:
                filters.append(AuditLog.correlation_id == query.correlation_id)

            if query.service_name:
                filters.append(AuditLog.service_name == query.service_name)

            if query.start_date:
                filters.append(AuditLog.timestamp >= query.start_date)

            if query.end_date:
                filters.append(AuditLog.timestamp <= query.end_date)

            if filters:
                statement = statement.where(and_(*filters))

            # Order by timestamp descending (most recent first)
            statement = statement.order_by(AuditLog.timestamp.desc())

            # Apply pagination
            statement = statement.offset(query.offset).limit(query.limit)

            # Execute query
            result = self.db.exec(statement)
            audit_logs = list(result.all())

            logger.info(
                f"Retrieved {len(audit_logs)} audit logs with filters: "
                f"user_id={query.user_id}, event_type={query.event_type}, "
                f"correlation_id={query.correlation_id}"
            )

            return audit_logs

        except Exception as e:
            logger.error(f"Error querying audit logs: {str(e)}")
            raise

    async def get_audit_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> AuditStats:
        """
        Get audit log statistics.

        Args:
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            Audit statistics
        """
        try:
            # Build base query
            base_query = select(AuditLog)

            # Apply date filters
            filters = []
            if start_date:
                filters.append(AuditLog.timestamp >= start_date)
            if end_date:
                filters.append(AuditLog.timestamp <= end_date)

            if filters:
                base_query = base_query.where(and_(*filters))

            # Total events
            total_events = self.db.exec(
                select(func.count(AuditLog.id)).select_from(AuditLog).where(
                    and_(*filters) if filters else True
                )
            ).one()

            # Events by type
            events_by_type_query = select(
                AuditLog.event_type,
                func.count(AuditLog.id).label('count')
            ).group_by(AuditLog.event_type)

            if filters:
                events_by_type_query = events_by_type_query.where(and_(*filters))

            events_by_type_result = self.db.exec(events_by_type_query).all()
            events_by_type = {row[0]: row[1] for row in events_by_type_result}

            # Events by service
            events_by_service_query = select(
                AuditLog.service_name,
                func.count(AuditLog.id).label('count')
            ).group_by(AuditLog.service_name)

            if filters:
                events_by_service_query = events_by_service_query.where(and_(*filters))

            events_by_service_result = self.db.exec(events_by_service_query).all()
            events_by_service = {row[0]: row[1] for row in events_by_service_result}

            # Unique users
            unique_users_query = select(func.count(func.distinct(AuditLog.user_id)))
            if filters:
                unique_users_query = unique_users_query.where(and_(*filters))

            unique_users = self.db.exec(unique_users_query).one()

            # Unique correlations
            unique_correlations_query = select(func.count(func.distinct(AuditLog.correlation_id)))
            if filters:
                unique_correlations_query = unique_correlations_query.where(and_(*filters))

            unique_correlations = self.db.exec(unique_correlations_query).one()

            # Date range
            date_range_query = select(
                func.min(AuditLog.timestamp),
                func.max(AuditLog.timestamp)
            )
            if filters:
                date_range_query = date_range_query.where(and_(*filters))

            date_range_result = self.db.exec(date_range_query).one()
            min_date, max_date = date_range_result

            date_range = {
                "start": min_date.isoformat() if min_date else None,
                "end": max_date.isoformat() if max_date else None
            }

            stats = AuditStats(
                total_events=total_events,
                events_by_type=events_by_type,
                events_by_service=events_by_service,
                unique_users=unique_users,
                unique_correlations=unique_correlations,
                date_range=date_range
            )

            logger.info(f"Retrieved audit statistics: total_events={total_events}")

            return stats

        except Exception as e:
            logger.error(f"Error getting audit statistics: {str(e)}")
            raise

    async def check_duplicate_event(self, correlation_id: UUID) -> bool:
        """
        Check if an event with the given correlation_id already exists.

        Args:
            correlation_id: Correlation ID to check

        Returns:
            True if duplicate exists, False otherwise
        """
        try:
            statement = select(AuditLog).where(
                AuditLog.correlation_id == correlation_id
            ).limit(1)

            result = self.db.exec(statement)
            existing = result.first()

            return existing is not None

        except Exception as e:
            logger.error(f"Error checking duplicate event: {str(e)}")
            return False

    async def validate_chronological_order(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Validate that audit logs are in chronological order with no gaps.

        Args:
            start_date: Start date for validation
            end_date: End date for validation

        Returns:
            Dictionary with validation results
        """
        try:
            # Get all audit logs in the date range ordered by timestamp
            statement = select(AuditLog).where(
                and_(
                    AuditLog.timestamp >= start_date,
                    AuditLog.timestamp <= end_date
                )
            ).order_by(AuditLog.timestamp.asc())

            result = self.db.exec(statement)
            audit_logs = list(result.all())

            if len(audit_logs) < 2:
                return {
                    "is_valid": True,
                    "total_logs": len(audit_logs),
                    "gaps_found": 0,
                    "message": "Insufficient logs for validation"
                }

            # Check for chronological order and gaps
            gaps = []
            for i in range(1, len(audit_logs)):
                prev_log = audit_logs[i - 1]
                curr_log = audit_logs[i]

                # Check if timestamps are in order
                if curr_log.timestamp < prev_log.timestamp:
                    gaps.append({
                        "type": "out_of_order",
                        "prev_id": str(prev_log.id),
                        "curr_id": str(curr_log.id),
                        "prev_timestamp": prev_log.timestamp.isoformat(),
                        "curr_timestamp": curr_log.timestamp.isoformat()
                    })

            is_valid = len(gaps) == 0

            return {
                "is_valid": is_valid,
                "total_logs": len(audit_logs),
                "gaps_found": len(gaps),
                "gaps": gaps[:10],  # Return first 10 gaps
                "message": "Chronological order validated" if is_valid else "Gaps found in chronological order"
            }

        except Exception as e:
            logger.error(f"Error validating chronological order: {str(e)}")
            return {
                "is_valid": False,
                "error": str(e)
            }
