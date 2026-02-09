"""
Logging utilities for MCP tools and agent interactions.
Provides consistent logging for all MCP-related operations.
"""
import logging
from typing import Dict, Any
from datetime import datetime


def setup_mcp_logging():
    """
    Set up logging configuration for MCP tools and agent interactions.
    """
    logger = logging.getLogger("mcp")
    logger.setLevel(logging.INFO)

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Create console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)

    # Add handler to logger if not already added
    if not logger.handlers:
        logger.addHandler(ch)

    return logger


def log_tool_execution(tool_name: str, user_id: str, success: bool, duration_ms: float = None):
    """
    Log the execution of an MCP tool.

    Args:
        tool_name: Name of the tool that was executed
        user_id: ID of the user who executed the tool
        success: Whether the tool execution was successful
        duration_ms: Duration of the execution in milliseconds (optional)
    """
    logger = logging.getLogger("mcp")

    duration_str = f" (duration: {duration_ms}ms)" if duration_ms else ""
    status_str = "SUCCESS" if success else "FAILED"

    logger.info(
        f"MCP Tool Execution - Tool: {tool_name}, User: {user_id}, "
        f"Status: {status_str}{duration_str}"
    )


def log_agent_interaction(user_id: str, query: str, response: str, success: bool):
    """
    Log an interaction with the AI agent.

    Args:
        user_id: ID of the user who interacted with the agent
        query: The user's query to the agent
        response: The agent's response to the user
        success: Whether the interaction was successful
    """
    logger = logging.getLogger("mcp")

    status_str = "SUCCESS" if success else "FAILED"

    logger.info(
        f"Agent Interaction - User: {user_id}, Status: {status_str}, "
        f"Query: {query[:100]}..." if len(query) > 100 else f"Query: {query}"
    )


def log_authentication_attempt(user_id: str, token_valid: bool, endpoint: str = None):
    """
    Log an authentication attempt for MCP tools.

    Args:
        user_id: ID of the user attempting authentication
        token_valid: Whether the authentication token was valid
        endpoint: The endpoint being accessed (optional)
    """
    logger = logging.getLogger("mcp")

    validity_str = "VALID" if token_valid else "INVALID"
    endpoint_str = f", Endpoint: {endpoint}" if endpoint else ""

    logger.info(
        f"Authentication Attempt - User: {user_id}, Token: {validity_str}{endpoint_str}"
    )