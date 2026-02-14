"""
Recurring Task Service - Handles automatic recurring task generation

This microservice:
- Subscribes to task.completed events
- Generates next instance of recurring tasks
- Implements idempotency for exactly-once task creation
- Uses Dapr Service Invocation to create tasks via backend API
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from dapr.ext.fastapi import DaprApp
import uvicorn
import os
from datetime import datetime, timedelta
import logging
from .handlers.task_completed_handler import TaskCompletedHandler
from .services.task_creator import TaskCreator
from .utils.idempotency import IdempotencyChecker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Recurring Task Service",
    description="Handles automatic recurring task generation for AI Todo application",
    version="1.0.0"
)

# Initialize Dapr app
dapr_app = DaprApp(app)

# Configuration
DAPR_HTTP_PORT = int(os.getenv("DAPR_HTTP_PORT", "3500"))
SERVICE_PORT = int(os.getenv("SERVICE_PORT", "8002"))
PUBSUB_NAME = os.getenv("PUBSUB_NAME", "kafka-pubsub")
BACKEND_APP_ID = os.getenv("BACKEND_APP_ID", "backend-api")

# Initialize services
task_creator = TaskCreator(dapr_http_port=DAPR_HTTP_PORT, backend_app_id=BACKEND_APP_ID)
idempotency_checker = IdempotencyChecker()
task_completed_handler = TaskCompletedHandler(
    task_creator=task_creator,
    idempotency_checker=idempotency_checker
)


@app.get("/health")
async def health_check():
    """Health check endpoint for Kubernetes liveness probe"""
    return {
        "status": "healthy",
        "service": "recurring-service",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint for Kubernetes readiness probe"""
    # TODO: Add Dapr connectivity check
    return {
        "status": "ready",
        "service": "recurring-service",
        "dapr_connected": True,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/dapr/subscribe")
async def subscribe():
    """
    Dapr subscription endpoint - returns list of topics to subscribe to

    This endpoint is called by Dapr to discover which topics this service
    wants to subscribe to.
    """
    subscriptions = [
        {
            "pubsubname": PUBSUB_NAME,
            "topic": "todo.task.events",
            "route": "/events/task-completed"
        }
    ]
    logger.info(f"Dapr subscriptions configured: {subscriptions}")
    return subscriptions


@app.post("/events/task-completed")
async def handle_task_completed_event(request: Request):
    """
    Handle task.completed events from Dapr Pub/Sub

    This endpoint receives task completion events and generates the next
    instance for recurring tasks.
    """
    try:
        event_data = await request.json()
        logger.info(f"Received task event: {event_data}")

        # Extract event data (Dapr wraps in CloudEvent format)
        data = event_data.get("data", {})
        event_type = data.get("event_type")

        # Only process task.completed events
        if event_type != "todo.task.completed":
            logger.info(f"Ignoring non-completion event: {event_type}")
            return JSONResponse(
                status_code=200,
                content={"status": "success", "message": "Event ignored"}
            )

        # Delegate to handler
        result = await task_completed_handler.handle_task_completed(data)

        # Return appropriate status code based on result
        if result.get("status") == "error":
            # Return 500 to trigger Dapr retry
            return JSONResponse(
                status_code=500,
                content=result
            )
        else:
            # Return 200 for success or skipped events
            return JSONResponse(
                status_code=200,
                content=result
            )

    except Exception as e:
        logger.error(f"Error processing task.completed event: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )


if __name__ == "__main__":
    logger.info(f"Starting Recurring Task Service on port {SERVICE_PORT}")
    logger.info(f"Dapr HTTP port: {DAPR_HTTP_PORT}")
    uvicorn.run(app, host="0.0.0.0", port=SERVICE_PORT)
