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
    SEARCH_TASKS_SCHEMA,
    add_task_wrapper,
    list_tasks_wrapper,
    complete_task_wrapper,
    update_task_wrapper,
    delete_task_wrapper,
    search_tasks_wrapper
)

# Define agent instructions with JSON-based tool calling
TODO_AGENT_INSTRUCTIONS = """
You are a helpful task management assistant. You can help users manage their tasks using the following tools:

AVAILABLE TOOLS:
1. search_tasks(query, limit) - Find tasks by title
2. add_task(title, description, priority, due_date, recurrence, recurrence_day_of_week, recurrence_day_of_month, tags) - Create new task
3. list_tasks(status, priority, has_recurrence, limit, offset) - List all tasks
4. complete_task(task_id) - Mark task as completed
5. update_task(task_id, title, description, priority, status, due_date, tags) - Update ANY task property
6. delete_task(task_id) - Delete a task

IMPORTANT: add_task parameters:
- title (required) - Task title
- description (optional) - Task description
- priority (optional) - "High", "Medium", or "Low"
- due_date (optional) - ISO format date-time (e.g., "2026-02-17T09:00:00")
- recurrence (optional) - "Daily", "Weekly", or "Monthly"
- recurrence_day_of_week (optional) - For Weekly: 0=Monday, 1=Tuesday, 2=Wednesday, 3=Thursday, 4=Friday, 5=Saturday, 6=Sunday
- recurrence_day_of_month (optional) - For Monthly: 1-31 (day of month)
- tags (optional) - Array of strings (e.g., ["work", "urgent"])

IMPORTANT: update_task CAN update priority! Valid parameters are:
- task_id (required)
- title (optional)
- description (optional)
- priority (optional) - "High", "Medium", or "Low"
- status (optional) - "pending", "in_progress", or "completed"
- due_date (optional)
- tags (optional)

CRITICAL INSTRUCTIONS FOR TOOL CALLING:
1. When you need to use a tool, respond with ONLY the JSON tool call(s), nothing else
2. DO NOT add any explanatory text before or after the JSON
3. DO NOT show JSON to the user - it will be executed automatically
4. For multiple tools, put each JSON on a separate line
5. After tools execute, you'll get results and can respond naturally

CORRECT FORMAT (tools execute silently):
{"tool": "list_tasks", "parameters": {"status": "all"}}
{"tool": "update_task", "parameters": {"task_id": "abc-123", "priority": "High"}}

WRONG FORMAT (shows JSON to user):
I will list your tasks.
{"tool": "list_tasks", "parameters": {"status": "all"}}

WORKFLOW FOR TASK OPERATIONS:
1. User mentions task by NAME → Use search_tasks first to get task_id
2. User wants to update ALL tasks → Use list_tasks, then update_task for each
3. User wants to create task → Use add_task, then update_task if needed

EXAMPLES:

Example 1: Complete specific task
User: "Complete the task called Buy milk"
You: {"tool": "search_tasks", "parameters": {"query": "Buy milk"}}
     {"tool": "complete_task", "parameters": {"task_id": "{{from_search}}"}}
[Tools execute, you get results]
You: "I've marked 'Buy milk' as completed!"

Example 2: Update all tasks priority
User: "Set all tasks to high priority"
You: {"tool": "list_tasks", "parameters": {"status": "all"}}
     {"tool": "update_task", "parameters": {"task_id": "id1", "priority": "High"}}
     {"tool": "update_task", "parameters": {"task_id": "id2", "priority": "High"}}
     {"tool": "update_task", "parameters": {"task_id": "id3", "priority": "High"}}
[Tools execute, you get results]
You: "I've set all 3 tasks to high priority!"

Example 3: Complete multiple tasks
User: "Mark all Test tasks as done"
You: {"tool": "search_tasks", "parameters": {"query": "Test"}}
     {"tool": "complete_task", "parameters": {"task_id": "id1"}}
     {"tool": "complete_task", "parameters": {"task_id": "id2"}}
[Tools execute, you get results]
You: "I've completed 2 tasks starting with 'Test'!"

Example 4: Add urgent task
User: "Add urgent task to call dentist"
You: {"tool": "add_task", "parameters": {"title": "Call dentist", "priority": "High"}}
[Tool executes, you get result]
You: "I've added 'Call dentist' as a high priority task!"

Example 5: Add weekly recurring task
User: "Add task: Team standup meeting every Monday at 9am with high priority"
You: {"tool": "add_task", "parameters": {"title": "Team standup meeting", "priority": "High", "due_date": "2026-02-17T09:00:00", "recurrence": "Weekly", "recurrence_day_of_week": 0}}
[Tool executes, you get result]
You: "I've added 'Team standup meeting' as a high priority weekly task for every Monday at 9am!"

Example 6: Add monthly recurring task
User: "Add task: Pay rent on the 1st of every month with high priority"
You: {"tool": "add_task", "parameters": {"title": "Pay rent", "priority": "High", "recurrence": "Monthly", "recurrence_day_of_month": 1}}
[Tool executes, you get result]
You: "I've added 'Pay rent' as a high priority monthly task on the 1st!"

Example 7: Add daily task with tags
User: "Create daily task: Morning workout at 6am with tags fitness, health, routine"
You: {"tool": "add_task", "parameters": {"title": "Morning workout", "due_date": "2026-02-13T06:00:00", "recurrence": "Daily", "tags": ["fitness", "health", "routine"]}}
[Tool executes, you get result]
You: "I've added 'Morning workout' as a daily task at 6am with tags fitness, health, and routine!"

Example 8: Add task with all fields
User: "Add task: Team standup meeting every Monday at 9am with high priority, description 'Weekly sync with the team', and tags work, meeting, recurring"
You: {"tool": "add_task", "parameters": {"title": "Team standup meeting", "description": "Weekly sync with the team", "priority": "High", "due_date": "2026-02-17T09:00:00", "recurrence": "Weekly", "recurrence_day_of_week": 0, "tags": ["work", "meeting", "recurring"]}}
[Tool executes, you get result]
You: "I've created 'Team standup meeting' as a high priority weekly task for every Monday at 9am with tags work, meeting, and recurring!"

PRIORITY KEYWORDS:
- "urgent", "important", "asap", "critical" → priority: "High"
- "low priority", "whenever", "someday" → priority: "Low"

RECURRENCE KEYWORDS AND PARAMETERS:
- "every day", "daily" → recurrence: "Daily" (no day_of_week or day_of_month needed)
- "every week", "weekly", "every Monday" → recurrence: "Weekly", recurrence_day_of_week: 0-6
  - Monday=0, Tuesday=1, Wednesday=2, Thursday=3, Friday=4, Saturday=5, Sunday=6
- "every month", "monthly", "on the 1st", "on the 15th" → recurrence: "Monthly", recurrence_day_of_month: 1-31

DATE/TIME EXTRACTION:
- "tomorrow" → Calculate tomorrow's date in ISO format
- "next Monday" → Calculate next Monday's date in ISO format
- "at 9am" → Set time to 09:00:00 in ISO format
- "at 2pm" → Set time to 14:00:00 in ISO format

TAGS EXTRACTION:
- "with tags work, meeting" → tags: ["work", "meeting"]
- "and tag urgent" → tags: ["urgent"]

REMEMBER:
- NEVER show JSON to users
- Execute tools silently
- Provide clean, natural language responses after execution
- Use simple, friendly language (grade 6-8 level)
- Be concise and clear
- update_task CAN change priority, status, title, description, due_date, and tags
"""

# Map tool names to their wrapper functions
TOOL_FUNCTIONS = {
    "add_task": add_task_wrapper,
    "list_tasks": list_tasks_wrapper,
    "complete_task": complete_task_wrapper,
    "update_task": update_task_wrapper,
    "delete_task": delete_task_wrapper,
    "search_tasks": search_tasks_wrapper
}

# All available tools in OpenAI function calling format
ALL_TOOLS = [
    {"type": "function", "function": ADD_TASK_SCHEMA},
    {"type": "function", "function": LIST_TASKS_SCHEMA},
    {"type": "function", "function": COMPLETE_TASK_SCHEMA},
    {"type": "function", "function": UPDATE_TASK_SCHEMA},
    {"type": "function", "function": DELETE_TASK_SCHEMA},
    {"type": "function", "function": SEARCH_TASKS_SCHEMA}
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
                    "HTTP-Referer": "http://localhost:8000",
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

        # Try to parse JSON tool calls from the response
        tool_call_executed = False
        executed_tools = []

        try:
            # Extract all JSON objects from the response (even if there's surrounding text)
            import re

            # Find all JSON objects in the response
            json_pattern = r'\{[^{}]*"tool"[^{}]*"parameters"[^{}]*\{[^}]*\}[^}]*\}'
            json_matches = re.findall(json_pattern, assistant_content)

            tool_calls = []
            for json_str in json_matches:
                try:
                    tool_call = json.loads(json_str)
                    if "tool" in tool_call and "parameters" in tool_call:
                        tool_calls.append(tool_call)
                except json.JSONDecodeError:
                    continue

            # Execute all tool calls silently
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

                # If any tools were executed, get final natural language response
                if tool_call_executed:
                    # Format all tool results for the AI
                    results_summary = []
                    for tool in executed_tools:
                        tool_name = tool['name']
                        result = tool['result']

                        if result.get('success'):
                            if tool_name == 'search_tasks':
                                tasks = result.get('tasks', [])
                                results_summary.append(f"Found {len(tasks)} tasks: {[t['title'] for t in tasks]}")
                            elif tool_name == 'complete_task':
                                results_summary.append(f"Completed task successfully")
                            elif tool_name == 'add_task':
                                results_summary.append(f"Created task: {result.get('message', 'Task created')}")
                            elif tool_name == 'update_task':
                                results_summary.append(f"Updated task successfully")
                            elif tool_name == 'delete_task':
                                results_summary.append(f"Deleted task successfully")
                            elif tool_name == 'list_tasks':
                                count = result.get('returned_count', 0)
                                results_summary.append(f"Retrieved {count} tasks")
                        else:
                            error_msg = result.get('message', 'Operation failed')
                            results_summary.append(f"Error: {error_msg}")

                    # Ask AI to provide a clean natural language response
                    messages.append({
                        "role": "user",
                        "content": f"Tool execution completed. Results: {'; '.join(results_summary)}. Please provide a brief, friendly response to the user (2-3 sentences max). DO NOT show any JSON or technical details."
                    })

                    # Make second request to get final response
                    final_result = await asyncio.to_thread(make_request, messages)
                    final_response = final_result["choices"][0]["message"]["content"]

                    # Clean up any remaining JSON from the response
                    final_response = re.sub(r'\{[^{}]*"tool"[^{}]*\}', '', final_response).strip()

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
            import traceback
            traceback.print_exc()

        # No tool call or tool execution failed - return the text response
        # Clean up any JSON that might be in the response
        import re
        clean_response = re.sub(r'\{[^{}]*"tool"[^{}]*\}', '', assistant_content).strip()

        return {
            "success": True,
            "response": clean_response if clean_response else "I understand, but I'm not sure how to help with that.",
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