"""
Standardized error codes for MCP tools to ensure consistent error mapping
and help the agent understand and communicate specific failure reasons to users.
"""

# Task-related errors
TASK_NOT_FOUND = "TASK_NOT_FOUND"
"""When a requested task doesn't exist or doesn't belong to user"""

# Authentication/Authorization errors
UNAUTHORIZED_ACCESS = "UNAUTHORIZED_ACCESS"
"""Attempt to access another user's resource"""

INVALID_INPUT = "INVALID_INPUT"
"""Tool parameters don't match schema"""

DATABASE_ERROR = "DATABASE_ERROR"
"""Database operation failed"""

AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
"""Invalid or missing authentication"""

# Generic errors
UNKNOWN_ERROR = "UNKNOWN_ERROR"
"""Catch-all for unexpected errors"""

ERROR_MESSAGES = {
    TASK_NOT_FOUND: "The requested task was not found or does not belong to you.",
    UNAUTHORIZED_ACCESS: "You do not have permission to access this resource.",
    INVALID_INPUT: "The input parameters are invalid or do not match the required format.",
    DATABASE_ERROR: "A database error occurred while processing your request.",
    AUTHENTICATION_ERROR: "Authentication is required or the provided credentials are invalid.",
    UNKNOWN_ERROR: "An unexpected error occurred while processing your request."
}