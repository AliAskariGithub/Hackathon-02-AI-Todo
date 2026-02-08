import jwt
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any
from ..utils.jwt import decode_jwt_token, verify_user_id_match
import os

security = HTTPBearer()

async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    Dependency to get the current user from the JWT token.

    Args:
        request: The incoming request object
        credentials: The authorization credentials from the request

    Returns:
        Decoded JWT payload containing user information

    Raises:
        HTTPException: If the token is invalid or expired
    """
    try:
        token = credentials.credentials
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