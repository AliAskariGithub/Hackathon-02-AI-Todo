from fastapi import HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from jwt import PyJWTError
from typing import Optional
import os
from ..utils.jwt import decode_jwt_token

security = HTTPBearer()

async def jwt_middleware(request: Request, credentials: HTTPAuthorizationCredentials = security):
    """
    JWT verification middleware to validate incoming requests.

    Args:
        request: The incoming request object
        credentials: The authorization credentials from the request

    Raises:
        HTTPException: If the token is missing, invalid, or expired
    """
    try:
        # Extract token from credentials
        token = credentials.credentials

        # Decode and verify the JWT token
        payload = decode_jwt_token(token)

        # Store the user information in the request state for later use
        request.state.user_id = payload.get("sub")
        request.state.user_email = payload.get("email", "")

        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication error: {str(e)}"
        )