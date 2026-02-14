from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator, Optional
from uuid import UUID
import asyncio
import json
from datetime import datetime
from ...utils.logging_config import get_logger
from ...api.deps import get_current_user, get_current_user_from_query
from ...dapr_sdk_utils.pubsub import DaprPubSub

router = APIRouter(prefix="/api/events", tags=["events"])
logger = get_logger(__name__)
pubsub = DaprPubSub()

# Store active SSE connections per user
active_connections: dict[str, list[asyncio.Queue]] = {}

# Rate limiting configuration
MAX_CONNECTIONS_PER_USER = 100


async def event_stream(user_id: str, queue: asyncio.Queue) -> AsyncGenerator[str, None]:
    """
    Generate SSE event stream for a specific user.

    Args:
        user_id: The user ID to filter events for
        queue: Queue to receive events from Kafka consumer

    Yields:
        SSE formatted event strings
    """
    try:
        # Send initial connection message
        yield f"data: {json.dumps({'type': 'connected', 'user_id': user_id, 'timestamp': datetime.utcnow().isoformat()})}\n\n"

        # Stream events from queue
        while True:
            try:
                # Wait for event with timeout for heartbeat
                event = await asyncio.wait_for(queue.get(), timeout=30.0)

                if event is None:  # Shutdown signal
                    break

                # Format as SSE event
                event_data = json.dumps(event)
                yield f"data: {event_data}\n\n"

            except asyncio.TimeoutError:
                # Send heartbeat to keep connection alive
                heartbeat = json.dumps({
                    'type': 'heartbeat',
                    'timestamp': datetime.utcnow().isoformat()
                })
                yield f"data: {heartbeat}\n\n"

    except asyncio.CancelledError:
        logger.info(f"SSE stream cancelled for user {user_id}")
    except Exception as e:
        logger.error(f"Error in event stream for user {user_id}: {str(e)}")
        error_msg = json.dumps({
            'type': 'error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat()
        })
        yield f"data: {error_msg}\n\n"
    finally:
        # Cleanup connection
        if user_id in active_connections:
            if queue in active_connections[user_id]:
                active_connections[user_id].remove(queue)
            if not active_connections[user_id]:
                del active_connections[user_id]


@router.get("/stream")
async def stream_events(
    request: Request,
    user_id: str,
    token: Optional[str] = None,
    current_user: dict = Depends(get_current_user_from_query)
) -> StreamingResponse:
    """
    SSE endpoint for streaming task events to authenticated clients.

    Rate limited to MAX_CONNECTIONS_PER_USER concurrent connections per user.
    Supports JWT token authentication via query parameter for EventSource API compatibility.

    Args:
        request: The incoming request object
        user_id: The user ID to filter events for
        token: JWT token from query parameter (required for EventSource API)
        current_user: The authenticated user from JWT token

    Returns:
        StreamingResponse with SSE events

    Raises:
        HTTPException: 401 if token invalid, 403 if user_id doesn't match token, 429 if rate limit exceeded
    """
    # Verify user_id matches authenticated user
    token_user_id = current_user.get("sub") or current_user.get("user_id")
    if str(token_user_id) != user_id:
        raise HTTPException(status_code=403, detail="Forbidden: Cannot access other user's events")

    # Check rate limit
    current_connections = len(active_connections.get(user_id, []))
    if current_connections >= MAX_CONNECTIONS_PER_USER:
        logger.warning(
            f"Rate limit exceeded for user {user_id}: {current_connections}/{MAX_CONNECTIONS_PER_USER} connections"
        )
        raise HTTPException(
            status_code=429,
            detail=f"Too many connections. Maximum {MAX_CONNECTIONS_PER_USER} concurrent connections allowed per user."
        )

    logger.info(f"Starting SSE stream for user {user_id} (connection {current_connections + 1}/{MAX_CONNECTIONS_PER_USER})")

    # Create queue for this connection
    queue: asyncio.Queue = asyncio.Queue(maxsize=100)

    # Register connection
    if user_id not in active_connections:
        active_connections[user_id] = []
    active_connections[user_id].append(queue)

    # Return streaming response
    return StreamingResponse(
        event_stream(user_id, queue),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


async def broadcast_event(event: dict) -> None:
    """
    Broadcast event to all connected SSE clients for the event's user.

    Args:
        event: The event to broadcast (must contain user_id in payload)
    """
    try:
        # Extract user_id from event
        user_id = event.get("payload", {}).get("user_id")
        if not user_id:
            logger.warning(f"Event missing user_id: {event.get('event_type')}")
            return

        user_id_str = str(user_id)

        # Get connections for this user
        connections = active_connections.get(user_id_str, [])
        if not connections:
            logger.debug(f"No active connections for user {user_id_str}")
            return

        logger.info(f"Broadcasting {event.get('event_type')} to {len(connections)} connections for user {user_id_str}")

        # Send event to all user's connections
        for queue in connections:
            try:
                # Non-blocking put with timeout
                await asyncio.wait_for(queue.put(event), timeout=1.0)
            except asyncio.TimeoutError:
                logger.warning(f"Queue full for user {user_id_str}, dropping event")
            except Exception as e:
                logger.error(f"Error broadcasting to queue: {str(e)}")

    except Exception as e:
        logger.error(f"Error in broadcast_event: {str(e)}")


@router.post("/webhook/task-events")
async def handle_task_event(request: Request) -> dict:
    """
    Dapr Pub/Sub webhook endpoint for task events.

    This endpoint receives events from Dapr Pub/Sub (Kafka) and broadcasts
    them to connected SSE clients.

    Args:
        request: The incoming request with event data

    Returns:
        Success response for Dapr
    """
    try:
        # Parse event from Dapr
        body = await request.json()

        # Dapr wraps the event in a CloudEvent format
        event_data = body.get("data", {})

        logger.info(f"Received task event: {event_data.get('event_type')}")

        # Broadcast to SSE clients
        await broadcast_event(event_data)

        return {"status": "success"}

    except Exception as e:
        logger.error(f"Error handling task event: {str(e)}")
        return {"status": "error", "message": str(e)}


@router.get("/subscriptions")
async def get_subscriptions() -> list[dict]:
    """
    Dapr Pub/Sub subscription endpoint.

    Tells Dapr which topics this service subscribes to and which
    endpoints to call for each topic.

    Returns:
        List of subscription configurations
    """
    return [
        {
            "pubsubname": "kafka-pubsub",
            "topic": "todo.task.events",
            "route": "/api/events/webhook/task-events",
            "metadata": {
                "rawPayload": "false"
            }
        }
    ]


@router.get("/health")
async def health_check() -> dict:
    """
    Health check endpoint for SSE bridge.

    Returns:
        Health status with active connection count
    """
    total_connections = sum(len(queues) for queues in active_connections.values())
    return {
        "status": "healthy",
        "active_users": len(active_connections),
        "total_connections": total_connections,
        "timestamp": datetime.utcnow().isoformat()
    }
