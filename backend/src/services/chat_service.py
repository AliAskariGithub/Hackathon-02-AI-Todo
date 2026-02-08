from typing import List, Optional
from datetime import datetime
from sqlmodel import select, func, desc
from uuid import UUID
from ..models import Conversation, Message, ConversationCreate, ConversationUpdate, MessageCreate
from ..utils.logging_config import get_logger
from sqlalchemy.exc import IntegrityError, DisconnectionError, OperationalError
from sqlalchemy.ext.asyncio import AsyncSession


logger = get_logger(__name__)


class ChatService:
    @staticmethod
    async def create_conversation(session: AsyncSession, conversation_data: ConversationCreate) -> Conversation:
        """Create a new conversation for a user."""
        logger.info(f"Creating conversation for user {conversation_data.user_id}")

        conversation = Conversation(
            title=conversation_data.title,
            user_id=conversation_data.user_id
        )
        session.add(conversation)
        await session.commit()
        await session.refresh(conversation)

        logger.info(f"Conversation {conversation.id} created successfully for user {conversation.user_id}")
        return conversation

    @staticmethod
    async def get_user_conversations(session: AsyncSession, user_id: UUID) -> List[Conversation]:
        """Get all conversations for a specific user."""
        logger.info(f"Retrieving conversations for user {user_id}")

        statement = select(Conversation).where(Conversation.user_id == user_id).order_by(desc(Conversation.created_at))
        result = await session.execute(statement)
        conversations = result.scalars().all()

        logger.info(f"Found {len(conversations)} conversations for user {user_id}")
        return conversations

    @staticmethod
    async def get_conversation_by_id(session: AsyncSession, user_id: UUID, conversation_id: UUID) -> Optional[Conversation]:
        """Get a specific conversation by ID for a user."""
        logger.info(f"Retrieving conversation {conversation_id} for user {user_id}")

        statement = select(Conversation).where(Conversation.id == conversation_id, Conversation.user_id == user_id)
        result = await session.execute(statement)
        conversation = result.scalar_one_or_none()

        if conversation:
            logger.info(f"Conversation {conversation_id} found for user {user_id}")
        else:
            logger.info(f"Conversation {conversation_id} not found for user {user_id}")

        return conversation

    @staticmethod
    async def add_message_to_conversation(session: AsyncSession, message_data: MessageCreate) -> Message:
        """Add a message to a specific conversation."""
        logger.info(f"Adding message to conversation {message_data.conversation_id}")

        message = Message(
            conversation_id=message_data.conversation_id,
            role=message_data.role,
            content=message_data.content,
            tool_calls=message_data.tool_calls
        )
        session.add(message)
        await session.commit()
        await session.refresh(message)

        # Update conversation's updated_at timestamp
        conversation_statement = select(Conversation).where(Conversation.id == message_data.conversation_id)
        conversation_result = await session.execute(conversation_statement)
        conversation = conversation_result.scalar_one_or_none()

        if conversation:
            conversation.updated_at = func.now()
            await session.commit()

        logger.info(f"Message {message.id} added successfully to conversation {message_data.conversation_id}")
        return message

    @staticmethod
    async def get_conversation_messages(session: AsyncSession, user_id: UUID, conversation_id: UUID) -> List[Message]:
        """Get all messages for a specific conversation belonging to a user."""
        logger.info(f"Retrieving messages for conversation {conversation_id} for user {user_id}")

        # First verify that the conversation belongs to the user
        conversation_statement = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
        conversation_result = await session.execute(conversation_statement)
        conversation = conversation_result.scalar_one_or_none()

        if not conversation:
            logger.warning(f"Conversation {conversation_id} does not belong to user {user_id}")
            return []

        # Get messages for the conversation
        statement = select(Message).where(Message.conversation_id == conversation_id).order_by(Message.created_at)
        result = await session.execute(statement)
        messages = result.scalars().all()

        logger.info(f"Found {len(messages)} messages for conversation {conversation_id}")
        return messages

    @staticmethod
    async def get_recent_conversation_messages(session: AsyncSession, conversation_id: UUID, limit: int = 15) -> List[Message]:
        """Get recent messages for a specific conversation, limited by count."""
        logger.info(f"Retrieving last {limit} messages for conversation {conversation_id}")

        statement = select(Message).where(
            Message.conversation_id == conversation_id
        ).order_by(desc(Message.created_at)).limit(limit)

        result = await session.execute(statement)
        messages = result.scalars().all()

        # Reverse the list to return in chronological order (oldest first)
        messages.reverse()

        logger.info(f"Found {len(messages)} recent messages for conversation {conversation_id}")
        return messages

    @staticmethod
    async def update_conversation(
        session: AsyncSession,
        user_id: UUID,
        conversation_id: UUID,
        update_data: ConversationUpdate
    ) -> Optional[Conversation]:
        """Update a conversation's details (e.g., title)."""
        logger.info(f"Updating conversation {conversation_id} for user {user_id}")

        # Get the conversation and verify ownership
        statement = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
        result = await session.execute(statement)
        conversation = result.scalar_one_or_none()

        if not conversation:
            logger.warning(f"Conversation {conversation_id} not found for user {user_id}")
            return None

        # Update fields if provided
        if update_data.title is not None:
            conversation.title = update_data.title

        conversation.updated_at = datetime.utcnow()

        await session.commit()
        await session.refresh(conversation)

        logger.info(f"Conversation {conversation_id} updated successfully")
        return conversation