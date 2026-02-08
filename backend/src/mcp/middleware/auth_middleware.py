import jwt
from typing import Dict, Any, Optional
from fastapi import HTTPException, status, Request
from src.utils.jwt import decode_jwt_token, verify_user_id_match
import os


def extract_user_id_from_token(authorization_header: str) -> str:
    """
    Extract user_id from the authorization header containing the JWT token.

    Args:
        authorization_header: Authorization header string (format: "Bearer <token>")

    Returns:
        user_id: The extracted user_id from the JWT token

    Raises:
        HTTPException: If the token is invalid or missing user_id
    """
    if not authorization_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is missing"
        )

    try:
        # Extract token from "Bearer <token>" format
        scheme, token = authorization_header.split(" ", 1)
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme"
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format"
        )

    try:
        payload = decode_jwt_token(token)
        user_id = payload.get("sub")  # Using "sub" as the user identifier (standard JWT claim)

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token does not contain user ID"
            )

        return str(user_id)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


def verify_authorized_user(request: Request) -> str:
    """
    Verify that the request has a valid JWT token and extract the user_id.

    Args:
        request: FastAPI request object containing the authorization header

    Returns:
        user_id: The extracted and validated user_id

    Raises:
        HTTPException: If authentication fails
    """
    authorization = request.headers.get("Authorization")
    return extract_user_id_from_token(authorization)


def validate_user_access(user_id: str, requested_user_id: str) -> bool:
    """
    Validate that the authenticated user can access the requested resource.

    Args:
        user_id: The user_id from the authenticated user's JWT
        requested_user_id: The user_id of the resource being accessed

    Returns:
        bool: True if access is authorized, raises HTTPException otherwise
    """
    if not verify_user_id_match(user_id, requested_user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have access to this resource"
        )
    return True


def handle_unauthorized_access() -> None:
    """
    Handle unauthorized access by raising HTTP 401 error.

    Raises:
        HTTPException: Always raises 401 Unauthorized error
    """
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized access - valid JWT required"
    )


def validate_jwt_token(token: str) -> Dict[str, Any]:
    """
    Validate the JWT token and return its payload.

    Args:
        token: JWT token string

    Returns:
        Dict containing the decoded JWT payload

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = decode_jwt_token(token)
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


def prevent_cross_user_access(tool_user_id: str, authenticated_user_id: str) -> bool:
    """
    Prevent cross-user data access by validating user identity.

    Args:
        tool_user_id: The user_id passed to the tool
        authenticated_user_id: The user_id from the authenticated session

    Returns:
        bool: True if access is allowed, raises HTTPException otherwise
    """
    if str(tool_user_id) != str(authenticated_user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cross-user access not allowed"
        )
    return True