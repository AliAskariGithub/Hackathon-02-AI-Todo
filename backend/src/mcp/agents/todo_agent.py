"""
OpenRouter Agent configuration for the Todo Application.
Defines the agent with task management instructions and registers MCP tools.
Uses OpenAI SDK with OpenRouter API.
"""
import os
from openai import OpenAI
from src.mcp.mcp_server import get_mcp_server

# Get the MCP server instance to access tools
mcp_server = get_mcp_server()

# Define the system instructions for the task management assistant
TODO_AGENT_INSTRUCTIONS = """
You are a helpful task management assistant. You can help users manage their tasks by:
- Adding new tasks
- Listing existing tasks
- Updating task details
- Marking tasks as complete
- Deleting tasks

Always confirm with the user before performing irreversible actions like deleting tasks.
If you cannot find a task that the user mentions, let them know specifically.
Be concise and clear in your responses.
Respect the user's context - you can only help with their own tasks.
"""

# Global variable to hold the agent instance
todo_agent = None

def get_openrouter_client():
    """Create and return an OpenRouter client instance."""
    from openai import OpenAI

    return OpenAI(
        api_key=os.getenv("GROQ_API_KEY"),
        base_url=os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1"),
        default_headers={
            "HTTP-Referer": "http://localhost:8001",
            "X-Title": "AI Todo App"
        }
    )

def get_todo_agent():
    """
    Returns the configured todo_agent instance.

    Creates the agent instance on first call, then caches it.
    Uses lazy initialization to avoid errors during module import.

    Returns:
        Agent: The OpenRouter agent configured for task management
    """
    global todo_agent

    if todo_agent is not None:
        return todo_agent

    # Initialize OpenRouter client only when needed
    client = get_openrouter_client()

    # OpenRouter doesn't support Assistants API, so create a dummy agent object that can be used in the runners
    # We'll return a dummy agent object that contains the instructions and model info
    class DummyAgent:
        def __init__(self, name, instructions, model):
            self.name = name
            self.instructions = instructions
            self.model = model

    todo_agent = DummyAgent(
        name="Todo Task Manager",
        instructions=TODO_AGENT_INSTRUCTIONS,
        model=os.getenv("GROQ_MODEL", "meta-llama/llama-3.2-3b-instruct:free")
    )

