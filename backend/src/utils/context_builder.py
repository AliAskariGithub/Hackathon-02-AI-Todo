"""Context builder for loading conversation history into agent context."""
from typing import List, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from ..services.chat_service import ChatService
from ..models.message import Message, MessageRole
import logging

logger = logging.getLogger(__name__)


class ContextBuilder:
    """Build conversation context for AI agent."""

    @staticmethod
    async def build_context(
        session: AsyncSession,
        conversation_id: UUID,
        user_id: UUID,
        limit: int = 15
    ) -> List[Dict[str, str]]:
        """
        Build conversation context from recent messages.

        Args:
            session: Database session
            conversation_id: Conversation ID
            user_id: User ID for ownership verification
            limit: Number of recent messages to include (default 15)

        Returns:
            List of message dictionaries in OpenAI format
        """
        # Get recent messages from database
        messages = await ChatService.get_recent_conversation_messages(
            session=session,
            conversation_id=conversation_id,
            limit=limit
        )

        # Convert to OpenAI message format
        context = []
        for message in messages:
            context.append({
                "role": message.role.value,
                "content": message.content
            })

        logger.info(f"Built context with {len(context)} messages for conversation {conversation_id}")
        return context

    @staticmethod
    def format_message(role: MessageRole, content: str) -> Dict[str, str]:
        """Format a single message for OpenAI API."""
        return {
            "role": role.value,
            "content": content
        }

    @staticmethod
    def add_system_message(
        context: List[Dict[str, str]],
        system_message: str
    ) -> List[Dict[str, str]]:
        """Add system message at the beginning of context."""
        return [{"role": "system", "content": system_message}] + context

    @staticmethod
    def get_default_system_message() -> str:
        """Get default system message for task management agent."""
        return """You are a helpful AI assistant that helps users manage their tasks through natural language conversation.

You have access to the following tools:
- list_tasks: Get all tasks for the current user
- create_task: Create a new task
- update_task: Update a task's description or completion status
- delete_task: Delete a task permanently

IMPORTANT GUIDELINES:
1. Always call list_tasks BEFORE attempting to update or delete a task to get the correct task_id
2. Never guess or make up task IDs
3. If a user's request is ambiguous, ask for clarification
4. For destructive operations (delete), ask for confirmation
5. Provide clear, friendly responses
6. Extract clean, actionable task descriptions from user messages

When a user asks to manage tasks, use the appropriate tool and provide clear feedback about what was done."""


# Global context builder instance
context_builder = ContextBuilder()
