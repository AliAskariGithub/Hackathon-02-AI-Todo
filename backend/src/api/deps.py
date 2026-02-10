import jwt
from fastapi import Depends, HTTPException, status, Request, Cookie, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any, Optional
from ..utils.jwt import decode_jwt_token, verify_user_id_match
import os
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer(auto_error=False)  # Make auto_error False for optional auth

async def get_current_user(
    request: Request,
    access_token: Optional[str] = Cookie(None),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Dict[str, Any]:
    """
    Dependency to get the current user from the JWT token.
    Supports both cookie-based (new) and header-based (legacy) authentication.
    Cookie takes priority over Authorization header during migration.

    Args:
        request: The incoming request object
        access_token: JWT token from HTTP-only cookie (new method)
        credentials: The authorization credentials from header (legacy method)

    Returns:
        Decoded JWT payload containing user information

    Raises:
        HTTPException: If the token is invalid, expired, or missing
    """
    # DEBUG: Log all headers
    logger.info(f"[AUTH DEBUG] Request path: {request.url.path}")
    logger.info(f"[AUTH DEBUG] Request headers: {dict(request.headers)}")
    logger.info(f"[AUTH DEBUG] Cookie access_token: {access_token[:30] if access_token else 'None'}...")
    logger.info(f"[AUTH DEBUG] HTTPBearer credentials: {credentials.credentials[:30] if credentials else 'None'}...")

    token = None
    auth_method = None

    # Priority 1: Check for cookie-based token (new system)
    if access_token:
        token = access_token
        auth_method = "cookie"
        logger.info("[AUTH DEBUG] Using cookie-based authentication")

    # Priority 2: Fall back to Authorization header (legacy system)
    elif credentials:
        token = credentials.credentials
        auth_method = "header"
        logger.info("[AUTH DEBUG] Using Authorization header authentication")

    # No authentication provided
    if not token:
        logger.error("[AUTH DEBUG] NO TOKEN FOUND - Neither cookie nor Authorization header present")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Please log in."
        )

    try:
        payload = decode_jwt_token(token)

        # Store user info in request state for later use
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID"
            )

        request.state.user_id = user_id
        request.state.user_email = payload.get("email", "")
        request.state.auth_method = auth_method  # Track which method was used

        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired. Please log in again."
        )
    except ValueError as e:
        # Token type validation error
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )
    except jwt.PyJWTError as e:
        logger.error(f"JWT validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token. Please log in again."
        )


async def verify_user_owns_resource(
    request: Request,
    user_id_from_path: str
) -> bool:
    """
    Verify that the user identified in the JWT token owns the resource
    specified by the user_id in the URL path.

    Args:
        request: The incoming request object (contains user info from JWT)
        user_id_from_path: The user_id from the URL path parameter

    Returns:
        True if the user owns the resource, raises HTTPException otherwise

    Raises:
        HTTPException: If the user doesn't own the resource (403 Forbidden)
    """
    token_user_id = getattr(request.state, 'user_id', None)

    if not token_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )

    if not verify_user_id_match(str(token_user_id), str(user_id_from_path)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have access to this resource"
        )

    return True