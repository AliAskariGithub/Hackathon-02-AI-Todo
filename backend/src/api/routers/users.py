from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Any
from ...models import UserRegistration, UserPublic
from ...services.user_service import UserService
from ...utils.database import get_async_session
from ...utils.logging_config import get_logger
from ...utils.jwt import create_access_token
from uuid import UUID
import logging

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/api/users", tags=["users"])
logger = get_logger(__name__)


@router.post("/register", response_model=UserPublic)
async def register_user(
    user_data: UserRegistration,
    session: AsyncSession = Depends(get_async_session)
) -> Any:
    """
    Register a new user.
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
        return user

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
    user_data: UserRegistration,
    session: AsyncSession = Depends(get_async_session)
) -> Any:
    """
    Login a user and return access token.
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

        # Create access token
        from datetime import timedelta
        from ...utils.jwt import create_access_token
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email, "name": user.user_name},
            expires_delta=timedelta(minutes=30)  # Token expires in 30 minutes
        )

        logger.info(f"User {user.id} logged in successfully")
        return {"access_token": access_token, "token_type": "bearer"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error logging in user {user_data.email or user_data.user_name}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during login"
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