from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Any
from datetime import timedelta
from ...models import UserRegistration, UserPublic
from ...services.user_service import UserService
from ...utils.database import get_async_session
from ...utils.logging_config import get_logger
from ...utils.jwt import create_access_token, create_refresh_token
from ...api.deps import get_current_user
from ...config import settings
from uuid import UUID
import logging
import os

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/api/users", tags=["users"])
logger = get_logger(__name__)


@router.post("/register", response_model=dict)
async def register_user(
    response: Response,
    user_data: UserRegistration,
    session: AsyncSession = Depends(get_async_session)
) -> Any:
    """
    Register a new user and automatically log them in with HTTP-only cookies.
    """
    logger.info(f"Received request to register user: {user_data.email}")

    try:
        # Check if user already exists
        existing_user = await UserService.get_user_by_email(session, user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email already exists"
            )

        # Register the new user
        user = await UserService.register_user(session, user_data)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to register user"
            )

        logger.info(f"User {user.id} registered successfully")

        # Auto-login: Create access token (15 minutes) and refresh token (7 days)
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email, "name": user.user_name},
            expires_delta=timedelta(minutes=15)
        )

        refresh_token = create_refresh_token(
            data={"sub": str(user.id)},
            expires_delta=timedelta(days=7)
        )

        # Determine if we're in production
        is_production = os.getenv("ENVIRONMENT", "development") == "production"

        # Set access token cookie (15 minutes)
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=is_production,
            samesite="lax",
            max_age=900,  # 15 minutes
            path="/"
        )

        # Set refresh token cookie (7 days)
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=is_production,
            samesite="lax",
            max_age=604800,  # 7 days
            path="/api/auth/refresh"
        )

        logger.info(f"User {user.id} auto-logged in after registration")

        # Return user info and token (token for backward compatibility)
        return {
            "user": {
                "id": str(user.id),
                "email": user.email,
                "user_name": user.user_name,
                "created_at": user.created_at.isoformat() if user.created_at else None
            },
            "access_token": access_token,  # Temporary: for backward compatibility
            "token_type": "bearer"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering user {user_data.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while registering the user"
        )


@router.post("/login")
async def login_user(
    response: Response,
    user_data: UserRegistration,
    session: AsyncSession = Depends(get_async_session)
) -> Any:
    """
    Login a user and set HTTP-only cookies with access and refresh tokens.
    Returns user information (not tokens in body for security).
    """
    logger.info(f"Login attempt for user: {user_data.email or user_data.user_name}")

    try:
        # Try to get user by email first if email is provided
        user = None
        if user_data.email:
            user = await UserService.get_user_by_email(session, user_data.email)

        # If not found by email and user_name is provided, try to get by username
        if not user and user_data.user_name:
            user = await UserService.get_user_by_username(session, user_data.user_name)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        # Verify password
        if not await UserService.verify_password(user_data.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        # Create access token (15 minutes) and refresh token (7 days)
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email, "name": user.user_name},
            expires_delta=timedelta(minutes=15)
        )

        refresh_token = create_refresh_token(
            data={"sub": str(user.id)},
            expires_delta=timedelta(days=7)
        )

        # Determine if we're in production (HTTPS required for Secure flag)
        is_production = os.getenv("ENVIRONMENT", "development") == "production"

        # Set access token cookie (15 minutes)
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=is_production,  # Only send over HTTPS in production
            samesite="lax",
            max_age=900,  # 15 minutes in seconds
            path="/"
        )

        # Set refresh token cookie (7 days)
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=is_production,
            samesite="lax",
            max_age=604800,  # 7 days in seconds
            path="/api/auth/refresh"  # Only sent to refresh endpoint
        )

        logger.info(f"User {user.id} logged in successfully with cookie-based auth")

        # Return user info and token (token for backward compatibility during migration)
        return {
            "user": {
                "id": str(user.id),
                "email": user.email,
                "user_name": user.user_name,
                "created_at": user.created_at.isoformat() if user.created_at else None
            },
            "access_token": access_token,  # Temporary: for backward compatibility
            "token_type": "bearer"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error logging in user {user_data.email or user_data.user_name}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during login"
        )


@router.get("/me", response_model=UserPublic)
async def get_current_user_info(
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
) -> Any:
    """
    Get the current authenticated user's information from JWT token.
    This endpoint uses the access_token cookie to identify the user.
    """
    logger.info(f"Retrieving current user info for user: {current_user['sub']}")

    try:
        user_uuid = UUID(current_user['sub'])
        user = await UserService.get_user_by_id(session, user_uuid)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        logger.info(f"Current user {user.id} retrieved successfully")
        return user

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID in token"
        )
    except Exception as e:
        logger.error(f"Error retrieving current user {current_user['sub']}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving user information"
        )


@router.get("/{user_id}", response_model=UserPublic)
async def get_user(
    user_id: str,
    session: AsyncSession = Depends(get_async_session)
) -> Any:
    """
    Get user by ID.
    """
    logger.info(f"Retrieving user by ID: {user_id}")

    try:
        user_uuid = UUID(user_id)
        user = await UserService.get_user_by_id(session, user_uuid)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        logger.info(f"User {user.id} retrieved successfully")
        return user

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    except Exception as e:
        logger.error(f"Error retrieving user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the user"
        )