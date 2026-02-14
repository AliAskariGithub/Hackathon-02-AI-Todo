"""
Notification Service - Handles reminder notifications via Dapr Jobs API callbacks

This microservice:
- Subscribes to reminder.scheduled events
- Receives callbacks from Dapr Jobs API when reminders fire
- Publishes notification.sent events
- Implements idempotency for exactly-once delivery
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from dapr.ext.fastapi import DaprApp
import uvicorn
import os
from datetime import datetime
import logging
from .handlers.job_callback_handler import JobCallbackHandler
from .utils.idempotency import IdempotencyChecker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Notification Service",
    description="Handles reminder notifications for AI Todo application",
    version="1.0.0"
)

# Initialize Dapr app
dapr_app = DaprApp(app)

# Configuration
DAPR_HTTP_PORT = int(os.getenv("DAPR_HTTP_PORT", "3500"))
SERVICE_PORT = int(os.getenv("SERVICE_PORT", "8001"))
PUBSUB_NAME = os.getenv("PUBSUB_NAME", "kafka-pubsub")

# Initialize services
idempotency_checker = IdempotencyChecker()
job_callback_handler = JobCallbackHandler(idempotency_checker=idempotency_checker)


@app.get("/health")
async def health_check():
    """Health check endpoint for Kubernetes liveness probe"""
    return {
        "status": "healthy",
        "service": "notification-service",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint for Kubernetes readiness probe"""
    # TODO: Add Dapr connectivity check
    return {
        "status": "ready",
        "service": "notification-service",
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
            "topic": "todo.reminders",
            "route": "/events/reminder"
        }
    ]
    logger.info(f"Dapr subscriptions configured: {subscriptions}")
    return subscriptions


@app.post("/events/reminder")
async def handle_reminder_event(request: Request):
    """
    Handle reminder.scheduled events from Dapr Pub/Sub

    This endpoint receives reminder events and logs them for processing.
    """
    try:
        event_data = await request.json()
        logger.info(f"Received reminder event: {event_data}")

        # TODO: Implement reminder event processing
        # - Extract event data
        # - Check idempotency
        # - Log reminder details

        return JSONResponse(
            status_code=200,
            content={"status": "success", "message": "Reminder event received"}
        )
    except Exception as e:
        logger.error(f"Error processing reminder event: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )


@app.post("/jobs/reminder-callback")
async def handle_reminder_callback(request: Request):
    """
    Dapr Jobs API callback endpoint

    Called by Dapr Jobs API when a scheduled reminder time arrives.
    """
    try:
        callback_data = await request.json()
        logger.info(f"Received Dapr Jobs callback: {callback_data}")

        # Delegate to handler
        result = await job_callback_handler.handle_reminder_callback(callback_data)

        # Return appropriate status code based on result
        if result.get("status") == "error":
            # Return 500 to trigger Dapr retry
            return JSONResponse(
                status_code=500,
                content=result
            )
        else:
            # Return 200 for success or skipped callbacks
            return JSONResponse(
                status_code=200,
                content=result
            )

    except Exception as e:
        logger.error(f"Error processing reminder callback: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )


if __name__ == "__main__":
    logger.info(f"Starting Notification Service on port {SERVICE_PORT}")
    logger.info(f"Dapr HTTP port: {DAPR_HTTP_PORT}")
    uvicorn.run(app, host="0.0.0.0", port=SERVICE_PORT)
