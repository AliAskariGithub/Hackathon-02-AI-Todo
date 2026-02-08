from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import List, Optional
from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession
from ...models import (
    Conversation, Message, ConversationCreate, ConversationUpdate, ConversationPublic,
    MessageCreate, MessagePublic, User
)
from ...services.chat_service import ChatService
from ...utils.database import get_async_session
from ...utils.logging_config import get_logger
from ...api.deps import get_current_user, verify_user_owns_resource

router = APIRouter(prefix="/api/{user_id}", tags=["chat"])
logger = get_logger(__name__)


@router.post("/conversations", response_model=ConversationPublic, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    request: Request,
    user_id: UUID,
    conversation_data: ConversationCreate,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
) -> ConversationPublic:
    """
    Create a new conversation for a user.
    """
    # Verify that the user_id in the token matches the user_id in the URL path
    await verify_user_owns_resource(request, str(user_id))

    try:
        logger.info(f"Received request to create conversation for user {user_id}")

        # Override the user_id from the path to prevent mismatch
        conversation_data.user_id = user_id

        conversation = await ChatService.create_conversation(session, conversation_data)
        logger.info(f"Successfully created conversation {conversation.id} for user {user_id}")
        return conversation
    except Exception as e:
        logger.error(f"Error creating conversation for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating conversation"
        )


@router.get("/conversations", response_model=List[ConversationPublic])
async def get_user_conversations(
    request: Request,
    user_id: UUID,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
) -> List[ConversationPublic]:
    """
    Get all conversations for a specific user.
    """
    # Verify that the user_id in the token matches the user_id in the URL path
    await verify_user_owns_resource(request, str(user_id))

    try:
        logger.info(f"Received request to get conversations for user {user_id}")
        conversations = await ChatService.get_user_conversations(session, user_id)
        logger.info(f"Returning {len(conversations)} conversations for user {user_id}")
        return conversations
    except Exception as e:
        logger.error(f"Error retrieving conversations for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving conversations"
        )


@router.get("/conversations/{conversation_id}", response_model=ConversationPublic)
async def get_conversation(
    request: Request,
    user_id: UUID,
    conversation_id: UUID,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
) -> ConversationPublic:
    """
    Get a specific conversation by ID for a user.
    """
    # Verify that the user_id in the token matches the user_id in the URL path
    await verify_user_owns_resource(request, str(user_id))

    try:
        logger.info(f"Received request to get conversation {conversation_id} for user {user_id}")
        conversation = await ChatService.get_conversation_by_id(session, user_id, conversation_id)

        if not conversation:
            logger.warning(f"Conversation {conversation_id} not found for user {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        logger.info(f"Successfully retrieved conversation {conversation_id} for user {user_id}")
        return conversation
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving conversation {conversation_id} for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving conversation"
        )


@router.patch("/conversations/{conversation_id}", response_model=ConversationPublic)
async def update_conversation(
    request: Request,
    user_id: UUID,
    conversation_id: UUID,
    update_data: ConversationUpdate,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
) -> ConversationPublic:
    """
    Update a conversation's details (e.g., rename title).
    """
    # Verify that the user_id in the token matches the user_id in the URL path
    await verify_user_owns_resource(request, str(user_id))

    try:
        logger.info(f"Received request to update conversation {conversation_id} for user {user_id}")
        conversation = await ChatService.update_conversation(session, user_id, conversation_id, update_data)

        if not conversation:
            logger.warning(f"Conversation {conversation_id} not found for user {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        logger.info(f"Successfully updated conversation {conversation_id} for user {user_id}")
        return conversation
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating conversation {conversation_id} for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating conversation"
        )


@router.post("/conversations/{conversation_id}/messages", response_model=MessagePublic)
async def add_message_to_conversation(
    request: Request,
    user_id: UUID,
    conversation_id: UUID,
    message_data: MessageCreate,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
) -> MessagePublic:
    """
    Add a message to a specific conversation.
    """
    # Verify that the user_id in the token matches the user_id in the URL path
    await verify_user_owns_resource(request, str(user_id))

    try:
        logger.info(f"Received request to add message to conversation {conversation_id} for user {user_id}")

        # Override the conversation_id from the path to prevent mismatch
        message_data.conversation_id = conversation_id

        # Validate role is either 'user' or 'assistant'
        if message_data.role not in ['user', 'assistant']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role must be either 'user' or 'assistant'"
            )

        message = await ChatService.add_message_to_conversation(session, message_data)
        logger.info(f"Successfully added message {message.id} to conversation {conversation_id}")
        return message
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding message to conversation {conversation_id} for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error adding message to conversation"
        )


@router.get("/conversations/{conversation_id}/messages", response_model=List[MessagePublic])
async def get_conversation_messages(
    request: Request,
    user_id: UUID,
    conversation_id: UUID,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
) -> List[MessagePublic]:
    """
    Get all messages for a specific conversation.
    """
    # Verify that the user_id in the token matches the user_id in the URL path
    await verify_user_owns_resource(request, str(user_id))

    try:
        logger.info(f"Received request to get messages for conversation {conversation_id} for user {user_id}")
        messages = await ChatService.get_conversation_messages(session, user_id, conversation_id)

        logger.info(f"Returning {len(messages)} messages for conversation {conversation_id}")
        return messages
    except Exception as e:
        logger.error(f"Error retrieving messages for conversation {conversation_id} for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving messages"
        )


@router.post("/chat", response_model=MessagePublic)
async def chat_endpoint(
    request: Request,
    user_id: UUID,
    message_data: MessageCreate,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
) -> MessagePublic:
    """
    Main chat endpoint that handles conversation with AI agent.
    This endpoint creates or continues a conversation, runs the agent, and saves the exchange.
    """
    # Verify that the user_id in the token matches the user_id in the URL path
    await verify_user_owns_resource(request, str(user_id))

    try:
        logger.info(f"Received chat request from user {user_id}")

        # Create or get conversation based on message_data
        conversation_id = message_data.conversation_id
        if not conversation_id:
            # Create a new conversation
            conversation_data = ConversationCreate(
                title=message_data.content[:50] + "..." if len(message_data.content) > 50 else message_data.content,
                user_id=user_id
            )
            conversation = await ChatService.create_conversation(session, conversation_data)
            conversation_id = conversation.id
        else:
            # Verify the user owns this conversation
            conversation = await ChatService.get_conversation_by_id(session, user_id, conversation_id)
            if not conversation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found"
                )

        # Add user message to the conversation
        user_message_data = MessageCreate(
            conversation_id=conversation_id,
            role="user",
            content=message_data.content,
            tool_calls=message_data.tool_calls
        )
        user_message = await ChatService.add_message_to_conversation(session, user_message_data)

        # Get conversation history (last 15 messages for context)
        history_messages = await ChatService.get_recent_conversation_messages(session, conversation_id, limit=15)

        # Prepare context for the agent (convert SQLModel messages to dict format)
        # Exclude the just-added user message since we'll pass it separately
        context = []
        for msg in history_messages[:-1]:  # Exclude the last message (the one we just added)
            context.append({
                "role": msg.role,
                "content": msg.content
            })

        # Get AI response using the task agent with the conversation history
        from ...mcp.runners.task_runner import run_task_agent

        # Run the AI agent to process the user message with conversation history
        agent_response = await run_task_agent(
            user_query=user_message.content,
            user_id=str(user_id),
            conversation_history=context
        )

        if agent_response["success"]:
            ai_response = agent_response["response"]
            tool_calls_data = agent_response.get("tool_calls")
        else:
            # Check if it's a rate limit error
            if agent_response.get("status") == "rate_limited":
                logger.warning(f"Rate limit hit for user {user_id}")
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded. The AI service has reached its usage limit. Please try again after 24 hours."
                )

            # Handle other error cases
            ai_response = "Sorry, I encountered an error processing your request. Please try again."
            tool_calls_data = None
            logger.error(f"Agent error for user {user_id}: {agent_response['response']}")

        # Add AI response to the conversation with tool_calls data
        ai_message_data = MessageCreate(
            conversation_id=conversation_id,
            role="assistant",
            content=ai_response,
            tool_calls=tool_calls_data  # Save tool calls if any were executed
        )
        ai_message = await ChatService.add_message_to_conversation(session, ai_message_data)

        logger.info(f"Successfully processed chat request for user {user_id}, conversation {conversation_id}")

        # Use the in-memory tool_calls_data instead of retrieving from database
        # This avoids JSON serialization issues with PostgreSQL JSON columns
        return MessagePublic(
            id=ai_message.id,
            conversation_id=ai_message.conversation_id,
            role=ai_message.role,
            content=ai_message.content,
            created_at=ai_message.created_at,
            tool_calls=tool_calls_data  # Use the original in-memory data
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing chat request for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing chat request"
        )