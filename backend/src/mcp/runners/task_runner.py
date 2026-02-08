"""
Utility functions for running the task agent.
Implements the run_task_agent function to process user queries with proper authentication context.
Uses OpenRouter's chat completions API with function calling support.
"""
import os
import requests
import asyncio
import json
from typing import Dict, Any, List, Optional

# Import MCP tool schemas and wrapper functions
from src.mcp.tools.task_tools import (
    ADD_TASK_SCHEMA,
    LIST_TASKS_SCHEMA,
    COMPLETE_TASK_SCHEMA,
    UPDATE_TASK_SCHEMA,
    DELETE_TASK_SCHEMA,
    add_task_wrapper,
    list_tasks_wrapper,
    complete_task_wrapper,
    update_task_wrapper,
    delete_task_wrapper
)

# Define agent instructions with JSON-based tool calling
TODO_AGENT_INSTRUCTIONS = """
You are a helpful task management assistant. You can help users manage their tasks using the following tools:

AVAILABLE TOOLS:
1. add_task - Add a new task
   Parameters: {"title": "string (required)", "description": "string (optional)"}

2. list_tasks - List all tasks
   Parameters: {"status": "all|pending|completed (optional, default: all)"}

3. complete_task - Mark a task as completed
   Parameters: {"task_id": "string (required)"}

4. update_task - Update task details
   Parameters: {"task_id": "string (required)", "title": "string (optional)", "description": "string (optional)", "status": "pending|completed (optional)"}

5. delete_task - Delete a task
   Parameters: {"task_id": "string (required)"}

INSTRUCTIONS:
- When you need to call a tool, respond with ONLY a JSON object in this format:
  {"tool": "tool_name", "parameters": {...}}
- After receiving tool results, provide a natural language response to the user
- Always confirm with the user before deleting tasks
- Be concise and clear in your responses

LANGUAGE GUIDELINES:
- Use simple, clear English at a grade 6-8 reading level
- Avoid technical jargon and complex vocabulary
- Use short sentences (15-20 words maximum)
- Break complex ideas into simple steps
- Use everyday words instead of fancy terms
- Example: Say "finish" instead of "complete", "change" instead of "modify"
- Keep your tone friendly and conversational
"""

# Map tool names to their wrapper functions
TOOL_FUNCTIONS = {
    "add_task": add_task_wrapper,
    "list_tasks": list_tasks_wrapper,
    "complete_task": complete_task_wrapper,
    "update_task": update_task_wrapper,
    "delete_task": delete_task_wrapper
}

# All available tools in OpenAI function calling format
ALL_TOOLS = [
    {"type": "function", "function": ADD_TASK_SCHEMA},
    {"type": "function", "function": LIST_TASKS_SCHEMA},
    {"type": "function", "function": COMPLETE_TASK_SCHEMA},
    {"type": "function", "function": UPDATE_TASK_SCHEMA},
    {"type": "function", "function": DELETE_TASK_SCHEMA}
]


async def run_task_agent(user_query: str, user_id: str, conversation_history: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """
    Process a user's natural language query using the task management AI agent with JSON-based tool calling.
    Uses OpenRouter's chat completions API with prompt-based tool execution.

    Args:
        user_query: Natural language query from the user (e.g., "Add a task to buy milk")
        user_id: Authenticated user's ID to bind to all operations
        conversation_history: Optional list of previous messages for context

    Returns:
        Dict containing the agent's response, tool_calls, and execution status
    """
    try:
        # Get API key from environment
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")

        # Create the system message with instructions and user context
        system_message = f"{TODO_AGENT_INSTRUCTIONS}\n\nContext: The current user ID is {user_id}. All operations must be performed for this user only."

        # Build messages array with conversation history
        messages = [{"role": "system", "content": system_message}]
        if conversation_history:
            messages.extend(conversation_history)
        messages.append({"role": "user", "content": user_query})

        # Make initial request to Groq
        def make_request(request_messages):
            payload = {
                "model": os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
                "messages": request_messages,
                "temperature": 0.7,
                "max_tokens": 1000
            }

            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "http://localhost:8001",
                    "X-Title": "AI Todo App"
                },
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()

        # Run the synchronous request in a thread pool to avoid blocking
        result = await asyncio.to_thread(make_request, messages)

        # Extract the assistant's message
        assistant_message = result["choices"][0]["message"]
        assistant_content = assistant_message.get("content", "")

        # Try to parse JSON tool calls from the response (can be multiple, one per line)
        tool_call_executed = False
        executed_tools = []

        try:
            # Check if the response contains JSON tool calls
            if assistant_content.strip().startswith("{") and "tool" in assistant_content:
                # Split by newlines to handle multiple tool calls
                lines = assistant_content.strip().split('\n')
                tool_calls = []

                for line in lines:
                    line = line.strip()
                    if line.startswith("{") and "tool" in line:
                        try:
                            tool_call = json.loads(line)
                            if "tool" in tool_call and "parameters" in tool_call:
                                tool_calls.append(tool_call)
                        except json.JSONDecodeError:
                            continue

                # Execute all tool calls
                if tool_calls:
                    for tool_call in tool_calls:
                        tool_name = tool_call["tool"]
                        tool_params = tool_call["parameters"]

                        # Inject user_id into tool parameters
                        tool_params["user_id"] = user_id

                        # Execute the tool
                        if tool_name in TOOL_FUNCTIONS:
                            tool_function = TOOL_FUNCTIONS[tool_name]
                            tool_result = await tool_function(tool_params)

                            # Store tool execution info
                            executed_tools.append({
                                "name": tool_name,
                                "arguments": tool_params,
                                "result": tool_result
                            })

                            tool_call_executed = True

                    # If any tools were executed, get final response
                    if tool_call_executed:
                        # Add tool results to messages and get final response
                        messages.append({"role": "assistant", "content": assistant_content})

                        # Format all tool results
                        results_text = "\n\n".join([
                            f"Tool: {tool['name']}\nResult: {json.dumps(tool['result'])}"
                            for tool in executed_tools
                        ])

                        messages.append({
                            "role": "user",
                            "content": f"Tool execution results:\n{results_text}\n\nPlease provide a natural language response to the user based on these results."
                        })

                        # Make second request to get final response
                        final_result = await asyncio.to_thread(make_request, messages)
                        final_response = final_result["choices"][0]["message"]["content"]

                        return {
                            "success": True,
                            "response": final_response,
                            "tool_calls": executed_tools,
                            "user_id": user_id,
                            "status": "completed"
                        }
        except json.JSONDecodeError:
            # Not a JSON tool call, treat as regular response
            pass
        except Exception as e:
            # Tool execution failed, but continue with the response
            print(f"Tool execution error: {str(e)}")

        # No tool call or tool execution failed - return the text response
        return {
            "success": True,
            "response": assistant_content if assistant_content else "I understand, but I'm not sure how to help with that.",
            "tool_calls": executed_tools if executed_tools else None,
            "user_id": user_id,
            "status": "completed"
        }

    except requests.exceptions.HTTPError as e:
        error_msg = f"API error: {str(e)}"
        status = "error"

        # Check if it's a rate limit error (429)
        if e.response.status_code == 429:
            error_msg = "Rate limit exceeded. Please try again after 24 hours."
            status = "rate_limited"

        return {
            "success": False,
            "response": error_msg,
            "tool_calls": None,
            "user_id": user_id,
            "status": status,
            "http_status": e.response.status_code if hasattr(e, 'response') else 500
        }
    except Exception as e:
        return {
            "success": False,
            "response": f"An error occurred while processing your request: {str(e)}",
            "tool_calls": None,
            "user_id": user_id,
            "status": "error"
        }


async def run_task_agent_with_context(user_query: str, user_id: str) -> Dict[str, Any]:
    """
    Alternative implementation that might be better for the MCP context.
    Processes a user's query with authentication context using MCP tools.

    Args:
        user_query: Natural language query from the user
        user_id: Authenticated user's ID to bind to all operations

    Returns:
        Dict containing the response from the agent
    """
    # This would integrate with the MCP framework to run tools with the proper context
    # For now, it delegates to the main run_task_agent function
    return await run_task_agent(user_query, user_id)