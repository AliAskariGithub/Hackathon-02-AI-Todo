"""
Audit Event Handler

Handles all system events from Kafka topics and stores them in audit log.
Subscribes to all topics for comprehensive audit trail.
"""

import logging
from typing import Dict, Any
from datetime import datetime
from ..models.audit_log import AuditLogCreate
from ..storage.audit_storage import AuditStorage

logger = logging.getLogger(__name__)


class AuditHandler:
    """
    Handler for capturing and storing all system events.
    """

    def __init__(self, audit_storage: AuditStorage):
        """
        Initialize the handler.

        Args:
            audit_storage: Storage service for audit logs
        """
        self.audit_storage = audit_storage

    async def handle_event(self, event: Dict[str, Any], topic: str) -> Dict[str, str]:
        """
        Handle a system event and store it in audit log.

        Args:
            event: The event data
            topic: The Kafka topic the event came from

        Returns:
            Response dictionary with status and message
        """
        try:
            # Extract event data
            event_type = event.get("event_type")
            payload = event.get("payload", {})
            correlation_id = event.get("correlation_id")
            timestamp_str = event.get("timestamp")

            logger.info(
                f"Received event for audit: event_type={event_type}, "
                f"topic={topic}, correlation_id={correlation_id}"
            )

            # Validate required fields
            if not event_type:
                logger.error(f"Missing event_type in event: {event}")
                return {"status": "error", "message": "Missing event_type"}

            # Check for duplicate event using correlation_id
            if correlation_id:
                is_duplicate = await self.audit_storage.check_duplicate_event(correlation_id)
                if is_duplicate:
                    logger.info(
                        f"Duplicate event detected for correlation_id {correlation_id}, skipping"
                    )
                    return {"status": "skipped", "message": "Duplicate event"}

            # Extract user_id from payload
            user_id = payload.get("user_id")

            # Parse timestamp
            if timestamp_str:
                try:
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                except ValueError:
                    timestamp = datetime.utcnow()
            else:
                timestamp = datetime.utcnow()

            # Determine service name from event type or topic
            service_name = self._extract_service_name(event_type, topic)

            # Create audit log entry
            audit_data = AuditLogCreate(
                event_type=event_type,
                event_payload=event,  # Store entire event for full context
                user_id=user_id,
                correlation_id=correlation_id,
                service_name=service_name,
                timestamp=timestamp
            )

            # Store in database
            audit_log = await self.audit_storage.store_audit_log(audit_data)

            logger.info(
                f"Successfully stored audit log: id={audit_log.id}, "
                f"event_type={event_type}"
            )

            return {
                "status": "success",
                "message": "Event audited successfully",
                "audit_log_id": str(audit_log.id)
            }

        except Exception as e:
            logger.error(f"Error handling audit event: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                "status": "error",
                "message": f"Error handling event: {str(e)}"
            }

    def _extract_service_name(self, event_type: str, topic: str) -> str:
        """
        Extract service name from event type or topic.

        Args:
            event_type: The event type
            topic: The Kafka topic

        Returns:
            Service name
        """
        # Try to extract from event type (e.g., "todo.task.created" -> "task")
        if event_type:
            parts = event_type.split('.')
            if len(parts) >= 2:
                return parts[1]  # e.g., "task", "reminder", "notification"

        # Fallback to topic name
        if topic:
            if "task" in topic.lower():
                return "task"
            elif "reminder" in topic.lower():
                return "reminder"
            elif "notification" in topic.lower():
                return "notification"
            elif "audit" in topic.lower():
                return "audit"

        return "unknown"
