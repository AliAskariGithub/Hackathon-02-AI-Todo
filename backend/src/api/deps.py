import jwt
from fastapi import Depends, HTTPException, status, Request, Cookie, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any, Optional
from ..utils.jwt import decode_jwt_token, verify_user_id_match
import os
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer(auto_error=False)  # Make auto_error False for optional auth

from sqlalchemy import text
from ..utils.database import async_session_factory

async def validate_neon_auth_session(token: str) -> Optional[Dict[str, Any]]:
    """Validate opaque session token from Neon Auth."""
    if not token or len(token) > 256:
        return None
    try:
        async with async_session_factory() as db_session:
            query = text(
                """
                SELECT s."userId", s."expiresAt", u.name, u.email
                FROM neon_auth.session s
                JOIN neon_auth.user u ON s."userId" = u.id
                WHERE s.token = :token AND s."expiresAt" > NOW()
                LIMIT 1
                """
            )
            result = await db_session.execute(query, {"token": token})
            row = result.fetchone()
            if row:
                user_id, expires_at, name, email = row
                # Ensure user exists in public."user" table so task foreign keys don't break
                upsert = text(
                    """
                    INSERT INTO public."user" (id, email, user_name, password, created_at, updated_at)
                    VALUES (:id, :email, :name, '', NOW(), NOW())
                    ON CONFLICT (id) DO UPDATE SET updated_at = NOW()
                    """
                )
                await db_session.execute(upsert, {"id": user_id, "email": email, "name": name or email.split("@")[0]})
                await db_session.commit()
                return {
                    "sub": str(user_id),
                    "email": email,
                    "name": name,
                    "auth_provider": "neon_auth"
                }
    except Exception as e:
        logger.debug(f"Error checking neon_auth.session: {e}")
    return None

async def get_current_user(
    request: Request,
    access_token: Optional[str] = Cookie(None),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Dict[str, Any]:
    """
    Dependency to get the current user from the JWT or Neon Auth session token.
    Supports cookie-based, header-based, and Neon Auth session tokens.
    """
    token = None
    auth_method = None

    # Priority 1: Check for cookie-based token (local development)
    if access_token:
        token = access_token
        auth_method = "cookie"

    # Priority 2: Fall back to Authorization header (production)
    elif credentials:
        token = credentials.credentials
        auth_method = "header"

    # No authentication provided
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Please log in."
        )

    # First: Check Neon Auth session
    neon_user = await validate_neon_auth_session(token)
    if neon_user:
        request.state.user_id = neon_user["sub"]
        request.state.user_email = neon_user.get("email", "")
        request.state.auth_method = "neon_auth"
        return neon_user

    # Second: Check JWT token
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


async def get_current_user_from_query(
    request: Request,
    token: Optional[str] = None,
    access_token: Optional[str] = Cookie(None)
) -> Dict[str, Any]:
    """
    Dependency to get the current user from JWT token in query parameter or cookie.
    Used for SSE endpoints where EventSource API doesn't support custom headers.

    Args:
        request: The incoming request object
        token: JWT token from query parameter
        access_token: JWT token from cookie

    Returns:
        Decoded JWT payload containing user information

    Raises:
        HTTPException: If the token is invalid, expired, or missing
    """
    effective_token = token or access_token
    if not effective_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Token required in query parameter or cookie."
        )

    # First: Check Neon Auth session
    neon_user = await validate_neon_auth_session(effective_token)
    if neon_user:
        request.state.user_id = neon_user["sub"]
        request.state.user_email = neon_user.get("email", "")
        request.state.auth_method = "neon_auth_query"
        return neon_user

    # Second: Check JWT token
    try:
        payload = decode_jwt_token(effective_token)

        # Store user info in request state for later use
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID"
            )

        request.state.user_id = user_id
        request.state.user_email = payload.get("email", "")
        request.state.auth_method = "query"

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