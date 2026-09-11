"""
Utility functions for running the task agent.
Implements the run_task_agent function to process user queries with proper authentication context.
Supports native Groq/OpenAI tool calling, XML tool calling (<tool_call><function=...>), and JSON tool calling.
"""
import os
import requests
import asyncio
import json
import re
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

# Define agent instructions with concise, token-efficient prompt
TODO_AGENT_INSTRUCTIONS = """You are a helpful AI assistant for managing todo tasks.
Use the provided tools to add, list, complete, update, search, or delete tasks for the authenticated user.
When creating tasks, infer appropriate priority (High, Medium, Low) and description if not specified.
Always call the appropriate tool when asked to manage tasks."""

# Map tool names to their wrapper functions
TOOL_FUNCTIONS = {
    "add_task": add_task_wrapper,
    "list_tasks": list_tasks_wrapper,
    "complete_task": complete_task_wrapper,
    "update_task": update_task_wrapper,
    "delete_task": delete_task_wrapper,
    "search_tasks": search_tasks_wrapper
}

# Aliases for common model hallucinations in tool names
TOOL_ALIASES = {
    "add_task": "add_task",
    "taskcreate": "add_task",
    "task_create": "add_task",
    "create_task": "add_task",
    "createtask": "add_task",
    "new_task": "add_task",
    "addtask": "add_task",
    "list_tasks": "list_tasks",
    "tasklist": "list_tasks",
    "task_list": "list_tasks",
    "get_tasks": "list_tasks",
    "listtasks": "list_tasks",
    "show_tasks": "list_tasks",
    "complete_task": "complete_task",
    "taskcomplete": "complete_task",
    "task_complete": "complete_task",
    "completetask": "complete_task",
    "mark_completed": "complete_task",
    "update_task": "update_task",
    "taskupdate": "update_task",
    "task_update": "update_task",
    "updatetask": "update_task",
    "edit_task": "update_task",
    "delete_task": "delete_task",
    "taskdelete": "delete_task",
    "task_delete": "delete_task",
    "deletetask": "delete_task",
    "remove_task": "delete_task",
    "search_tasks": "search_tasks",
    "tasksearch": "search_tasks",
    "task_search": "search_tasks",
    "searchtasks": "search_tasks",
    "find_tasks": "search_tasks"
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


def parse_xml_tool_calls(content: str) -> List[Dict[str, Any]]:
    """Parse XML-style tool calls (e.g. <tool_call><function=TaskCreate>...</function></tool_call>)."""
    calls = []
    if not content:
        return calls

    blocks = re.findall(r'<tool_call>(.*?)</tool_call>', content, re.DOTALL | re.IGNORECASE)
    if not blocks and ('<function=' in content or '<function ' in content):
        blocks = [content]

    for block in blocks:
        func_match = re.search(r'<function[=\s]+([a-zA-Z0-9_-]+)>(.*?)</function>', block, re.DOTALL | re.IGNORECASE)
        if func_match:
            func_name = func_match.group(1).strip()
            body = func_match.group(2)
            param_matches = re.findall(r'<parameter[=\s]+([a-zA-Z0-9_-]+)>(.*?)</parameter>', body, re.DOTALL | re.IGNORECASE)
            params = {}
            for p_name, p_val in param_matches:
                val = p_val.strip()
                try:
                    params[p_name] = json.loads(val)
                except Exception:
                    params[p_name] = val
            calls.append({"tool": func_name, "parameters": params})
    return calls


def parse_json_tool_calls(content: str) -> List[Dict[str, Any]]:
    """Parse JSON-style tool calls from text."""
    calls = []
    if not content:
        return calls

    p1 = r'\{[^{}]*"tool"\s*:\s*"[^"]+"\s*,\s*"parameters"\s*:\s*\{[^}]*\}\s*\}'
    for match in re.finditer(p1, content, re.DOTALL):
        try:
            parsed = json.loads(match.group(0))
            if "tool" in parsed and "parameters" in parsed:
                calls.append(parsed)
        except Exception:
            pass

    p2 = r'\{[^{}]*"name"\s*:\s*"[^"]+"\s*,\s*"arguments"\s*:\s*\{[^}]*\}\s*\}'
    for match in re.finditer(p2, content, re.DOTALL):
        try:
            parsed = json.loads(match.group(0))
            if "name" in parsed and "arguments" in parsed:
                calls.append({"tool": parsed["name"], "parameters": parsed["arguments"]})
        except Exception:
            pass

    return calls


def clean_llm_response(text: str) -> str:
    """Clean all tool call markup and tags from LLM responses."""
    if not text:
        return ""
    text = re.sub(r'<tool_call>.*?</tool_call>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<function[=\s]+[a-zA-Z0-9_-]+>.*?</function>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<parameter[=\s]+[a-zA-Z0-9_-]+>.*?</parameter>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'\{[^{}]*"tool"\s*:[^{}]*\}', '', text, flags=re.DOTALL)
    # Remove leading/trailing empty lines
    return text.strip()


async def run_task_agent(user_query: str, user_id: str, conversation_history: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """
    Process a user's natural language query using the task management AI agent.
    Supports native Groq tool calling as well as XML/JSON prompt fallbacks.

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

        model_name = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")

        # Create the system message with instructions and user context
        system_message = f"{TODO_AGENT_INSTRUCTIONS}\n\nContext: The current user ID is {user_id}. All operations must be performed for this user only."

        # Build messages array with conversation history
        messages = [{"role": "system", "content": system_message}]
        if conversation_history:
            messages.extend(conversation_history)
        messages.append({"role": "user", "content": user_query})

        # Request helper to Groq
        def make_request(request_messages, use_tools=True):
            payload = {
                "model": model_name,
                "messages": request_messages,
                "temperature": 0.3,
                "max_tokens": 1000
            }
            if use_tools:
                payload["tools"] = ALL_TOOLS
                payload["tool_choice"] = "auto"

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
        result = await asyncio.to_thread(make_request, messages, True)

        # Extract the assistant's message
        assistant_message = result["choices"][0]["message"]
        assistant_content = assistant_message.get("content", "") or ""

        # Extract tool calls from all possible formats
        extracted_tool_calls: List[Dict[str, Any]] = []

        # Format 1: Native OpenAI / Groq tool_calls
        raw_native_calls = assistant_message.get("tool_calls") or []
        for tc in raw_native_calls:
            fn = tc.get("function", {})
            fn_name = fn.get("name")
            fn_args_raw = fn.get("arguments", "{}")
            if isinstance(fn_args_raw, str):
                try:
                    fn_args = json.loads(fn_args_raw)
                except Exception:
                    fn_args = {}
            else:
                fn_args = fn_args_raw or {}
            if fn_name:
                extracted_tool_calls.append({"tool": fn_name, "parameters": fn_args})

        # Format 2: XML tool calls (<tool_call><function=...>) in text
        if not extracted_tool_calls:
            xml_calls = parse_xml_tool_calls(assistant_content)
            if xml_calls:
                extracted_tool_calls.extend(xml_calls)

        # Format 3: JSON tool calls ({"tool": ...}) in text
        if not extracted_tool_calls:
            json_calls = parse_json_tool_calls(assistant_content)
            if json_calls:
                extracted_tool_calls.extend(json_calls)

        tool_call_executed = False
        executed_tools = []

        # Execute any discovered tool calls
        if extracted_tool_calls:
            for tc in extracted_tool_calls:
                raw_name = str(tc.get("tool", "")).strip()
                normalized_key = raw_name.lower().replace("-", "_").replace(" ", "_")
                tool_name = TOOL_ALIASES.get(normalized_key, raw_name)
                tool_params = tc.get("parameters", {}) or {}

                # Parameter normalization
                if "name" in tool_params and "title" not in tool_params:
                    tool_params["title"] = tool_params["name"]
                if "task_title" in tool_params and "title" not in tool_params:
                    tool_params["title"] = tool_params["task_title"]
                if "priority" in tool_params and isinstance(tool_params["priority"], str):
                    tool_params["priority"] = tool_params["priority"].strip().capitalize()
                if "recurrence" in tool_params and isinstance(tool_params["recurrence"], str):
                    tool_params["recurrence"] = tool_params["recurrence"].strip().capitalize()

                # Inject user_id
                tool_params["user_id"] = user_id

                if tool_name in TOOL_FUNCTIONS:
                    tool_func = TOOL_FUNCTIONS[tool_name]
                    try:
                        tool_result = await tool_func(tool_params)
                        executed_tools.append({
                            "name": tool_name,
                            "arguments": tool_params,
                            "result": tool_result
                        })
                        tool_call_executed = True
                    except Exception as e:
                        print(f"Error executing tool {tool_name}: {e}")
                        executed_tools.append({
                            "name": tool_name,
                            "arguments": tool_params,
                            "result": {"success": False, "message": str(e)}
                        })

            # If tools were executed, generate a clean natural language confirmation
            if tool_call_executed:
                results_summary = []
                for tool in executed_tools:
                    t_name = tool['name']
                    result = tool['result']

                    if result.get('success'):
                        if t_name == 'add_task':
                            task_info = result.get('task', {})
                            results_summary.append(f"Created task '{task_info.get('title', 'New Task')}' with priority {task_info.get('priority', 'Medium')}")
                        elif t_name == 'complete_task':
                            results_summary.append("Completed task successfully")
                        elif t_name == 'update_task':
                            results_summary.append("Updated task successfully")
                        elif t_name == 'delete_task':
                            results_summary.append("Deleted task successfully")
                        elif t_name == 'search_tasks':
                            tasks = result.get('tasks', [])
                            results_summary.append(f"Found {len(tasks)} tasks")
                        elif t_name == 'list_tasks':
                            count = result.get('returned_count', 0)
                            results_summary.append(f"Retrieved {count} tasks")
                    else:
                        results_summary.append(f"{t_name} error: {result.get('message', 'Operation failed')}")

                final_clean = None
                try:
                    confirm_messages = [
                        {"role": "system", "content": "You are a helpful task assistant. Respond in 1 friendly sentence."},
                        {"role": "user", "content": f"The operations completed: {'; '.join(results_summary)}. Provide a 1-sentence friendly confirmation to the user. Do not show technical terms, XML, or JSON."}
                    ]
                    final_result = await asyncio.to_thread(make_request, confirm_messages, False)
                    final_content = final_result["choices"][0]["message"]["content"]
                    final_clean = clean_llm_response(final_content)
                except Exception:
                    # Fallback to direct summary message if LLM is rate-limited
                    final_clean = "; ".join(results_summary) + "."

                return {
                    "success": True,
                    "response": final_clean or "I've successfully performed the requested task operation.",
                    "tool_calls": executed_tools,
                    "user_id": user_id,
                    "status": "completed"
                }

        # If no tool call was found or executed, return the cleaned assistant response
        clean_response = clean_llm_response(assistant_content)
        return {
            "success": True,
            "response": clean_response if clean_response else "I understand, but I'm not sure how to help with that. Could you clarify?",
            "tool_calls": executed_tools if executed_tools else None,
            "user_id": user_id,
            "status": "completed"
        }

    except requests.exceptions.HTTPError as e:
        error_msg = f"API error: {str(e)}"
        status_text = "error"

        try:
            error_json = e.response.json()
            if isinstance(error_json, dict) and "error" in error_json:
                err_detail = error_json["error"]
                if isinstance(err_detail, dict) and "message" in err_detail:
                    error_msg = f"AI Service Error: {err_detail['message']}"
        except Exception:
            pass

        if e.response.status_code == 429:
            error_msg = "Rate limit exceeded. Please try again after 24 hours."
            status_text = "rate_limited"

        return {
            "success": False,
            "response": error_msg,
            "tool_calls": None,
            "user_id": user_id,
            "status": status_text,
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
    Alternative implementation for running the agent with context.
    """
    return await run_task_agent(user_query, user_id)