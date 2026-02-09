from fastapi import APIRouter, HTTPException, status, Response, Cookie
from typing import Optional
import jwt
import os
import logging
from ...utils.jwt import decode_refresh_token, create_access_token
from datetime import timedelta

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post("/refresh")
async def refresh_token(
    response: Response,
    refresh_token: Optional[str] = Cookie(None)
):
    """
    Refresh the access token using a valid refresh token.

    The refresh token is read from the HTTP-only cookie.
    A new access token is generated and set as an HTTP-only cookie.

    Returns:
        Success message indicating token was refreshed

    Raises:
        HTTPException: If refresh token is missing, invalid, or expired
    """
    logger.info("Received token refresh request")

    if not refresh_token:
        logger.warning("Refresh token missing from request")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No refresh token provided. Please log in again."
        )

    try:
        # Decode and validate refresh token
        payload = decode_refresh_token(refresh_token)
        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token: missing user ID"
            )

        # Create new access token (15 minutes)
        new_access_token = create_access_token(
            data={"sub": user_id},
            expires_delta=timedelta(minutes=15)
        )

        # Determine if we're in production
        is_production = os.getenv("ENVIRONMENT", "development") == "production"

        # Set new access token cookie
        response.set_cookie(
            key="access_token",
            value=new_access_token,
            httponly=True,
            secure=is_production,
            samesite="lax",
            max_age=900,  # 15 minutes
            path="/"
        )

        logger.info(f"Access token refreshed successfully for user {user_id}")

        return {
            "refreshed": True,
            "message": "Access token refreshed successfully"
        }

    except jwt.ExpiredSignatureError:
        logger.warning("Refresh token has expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired. Please log in again."
        )
    except ValueError as e:
        logger.error(f"Token validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid refresh token: {str(e)}"
        )
    except jwt.PyJWTError as e:
        logger.error(f"JWT error during token refresh: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token. Please log in again."
        )
    except Exception as e:
        logger.error(f"Unexpected error during token refresh: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while refreshing the token"
        )


@router.post("/logout")
async def logout(response: Response):
    """
    Logout the user by clearing authentication cookies.

    This endpoint clears both the access_token and refresh_token cookies,
    effectively logging the user out. Works even if the user is not authenticated.

    Returns:
        Success message indicating logout was successful
    """
    logger.info("Received logout request")

    try:
        # Clear access token cookie
        response.delete_cookie(
            key="access_token",
            path="/"
        )

        # Clear refresh token cookie
        response.delete_cookie(
            key="refresh_token",
            path="/api/auth/refresh"
        )

        logger.info("User logged out successfully - cookies cleared")

        return {
            "logged_out": True,
            "message": "Logged out successfully"
        }

    except Exception as e:
        logger.error(f"Error during logout: {str(e)}")
        # Still return success even if there's an error
        # Logout should always succeed from the user's perspective
        return {
            "logged_out": True,
            "message": "Logged out successfully"
        }
