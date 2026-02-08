"""AsyncOpenAI client configuration for OpenRouter."""
import os
import asyncio
from typing import Optional
from openai import AsyncOpenAI
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)


@lru_cache()
def get_openrouter_config() -> tuple[str, str]:
    """Get OpenRouter configuration from environment variables."""
    api_key = os.getenv("GROQ_API_KEY")
    model = os.getenv("GROQ_MODEL", "meta-llama/llama-3.2-3b-instruct:free")

    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is required")

    return api_key, model


def create_openrouter_client() -> AsyncOpenAI:
    """
    Create AsyncOpenAI client configured for OpenRouter.

    Uses synchronous requests with asyncio.to_thread() to work around
    Windows DNS resolution issues with asyncio.
    """
    api_key, _ = get_openrouter_config()

    client = AsyncOpenAI(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1",
        default_headers={
            "HTTP-Referer": "https://ai-todo-app.com",
            "X-Title": "AI Todo Application"
        }
    )

    logger.info("OpenRouter client initialized successfully")
    return client


async def test_openrouter_connection() -> bool:
    """
    Test OpenRouter connection with a simple request.

    Returns:
        True if connection successful, False otherwise
    """
    try:
        _, model = get_openrouter_config()
        client = create_openrouter_client()

        # Simple test request
        response = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10
        )

        logger.info("OpenRouter connection test successful")
        return True
    except Exception as e:
        logger.error(f"OpenRouter connection test failed: {e}")
        return False


# Global client instance
_openrouter_client: Optional[AsyncOpenAI] = None


def get_openrouter_client() -> AsyncOpenAI:
    """Get or create the global OpenRouter client instance."""
    global _openrouter_client
    if _openrouter_client is None:
        _openrouter_client = create_openrouter_client()
    return _openrouter_client
