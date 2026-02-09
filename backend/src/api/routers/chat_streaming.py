"""Streaming chat endpoint for Server-Sent Events."""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator
from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession
from ...models import MessageCreate, ConversationCreate
from ...services.chat_service import ChatService
from ...utils.database import get_async_session
from ...utils.logging_config import get_logger
from ...api.deps import get_current_user, verify_user_owns_resource
from ...mcp.runners.task_runner import run_task_agent
from ...mcp.agents.todo_agent import get_todo_agent
import json
import asyncio

logger = get_logger(__name__)

streaming_router = APIRouter(prefix="/api/{user_id}", tags=["chat-streaming"])


async def generate_sse_stream(
    user_id: str,
    conversation_id: UUID,
    user_message_content: str,
    session: AsyncSession
) -> AsyncGenerator[str, None]:
    """
    Generate Server-Sent Events stream for AI response.

    Yields SSE-formatted chunks of the AI response.
    """
    try:
        # Get conversation history for context
        history_messages = await ChatService.get_recent_conversation_messages(
            session, conversation_id, limit=15
        )

        # Prepare context
        context = []
        for msg in history_messages:
            context.append({
                "role": msg.role,
                "content": msg.content
            })

        # Run the AI agent
        agent_response = await asyncio.wait_for(
            run_task_agent(user_message_content, user_id, context),
            timeout=30.0
        )

        if agent_response["success"]:
            ai_response = agent_response["response"]

            # Stream the response in chunks
            chunk_size = 10  # Characters per chunk
            for i in range(0, len(ai_response), chunk_size):
                chunk = ai_response[i:i + chunk_size]
                yield f"data: {json.dumps({'type': 'content', 'content': chunk})}\n\n"
                await asyncio.sleep(0.05)  # Small delay for streaming effect

            # Send completion event
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
        else:
            # Send error event
            error_msg = "Sorry, I encountered an error processing your request."
            yield f"data: {json.dumps({'type': 'error', 'message': error_msg})}\n\n"

    except asyncio.TimeoutError:
        logger.error(f"Streaming timeout for user {user_id}")
        yield f"data: {json.dumps({'type': 'error', 'message': 'Request timed out'})}\n\n"
    except Exception as e:
        logger.error(f"Streaming error for user {user_id}: {str(e)}")
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"


@streaming_router.post("/chat/stream")
async def chat_stream_endpoint(
    request: Request,
    user_id: UUID,
    message_data: MessageCreate,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Streaming chat endpoint that returns Server-Sent Events.
    """
    # Verify user owns resource
    await verify_user_owns_resource(request, str(user_id))

    try:
        logger.info(f"Received streaming chat request from user {user_id}")

        # Create or get conversation
        conversation_id = message_data.conversation_id
        if not conversation_id:
            conversation_data = ConversationCreate(
                title=message_data.content[:50] + "..." if len(message_data.content) > 50 else message_data.content,
                user_id=user_id
            )
            conversation = await ChatService.create_conversation(session, conversation_data)
            conversation_id = conversation.id
        else:
            conversation = await ChatService.get_conversation_by_id(session, user_id, conversation_id)
            if not conversation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found"
                )

        # Save user message
        user_message_data = MessageCreate(
            conversation_id=conversation_id,
            role="user",
            content=message_data.content,
            tool_calls=None
        )
        await ChatService.add_message_to_conversation(session, user_message_data)

        # Return streaming response
        return StreamingResponse(
            generate_sse_stream(str(user_id), conversation_id, message_data.content, session),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"  # Disable nginx buffering
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in streaming chat for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing streaming chat request"
        )
