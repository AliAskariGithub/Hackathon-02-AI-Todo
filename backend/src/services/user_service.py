from typing import Optional
from sqlmodel import select
from uuid import UUID
from ..models import User, UserBase
from ..utils.logging_config import get_logger
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
import bcrypt
from datetime import datetime


logger = get_logger(__name__)


class UserService:
    @staticmethod
    async def register_user(session: AsyncSession, user_data: UserBase) -> Optional[User]:
        """Register a new user with hashed password."""
        logger.info(f"Registering new user with email: {user_data.email}")

        try:
            # Hash the password
            hashed_password = bcrypt.hashpw(
                user_data.password.encode('utf-8'),
                bcrypt.gensalt()
            ).decode('utf-8')

            # Create user with hashed password and timestamps
            user = User(
                email=user_data.email,
                user_name=user_data.user_name,
                password=hashed_password,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            session.add(user)
            await session.commit()
            await session.refresh(user)

            logger.info(f"User {user.id} registered successfully with email: {user.email}")
            return user

        except IntegrityError as e:
            logger.error(f"Error registering user {user_data.email}: {str(e)}")
            await session.rollback()
            return None
        except Exception as e:
            logger.error(f"Unexpected error registering user {user_data.email}: {str(e)}")
            await session.rollback()
            return None

    @staticmethod
    async def get_user_by_email(session: AsyncSession, email: str) -> Optional[User]:
        """Get a user by email."""
        logger.info(f"Retrieving user by email: {email}")

        try:
            statement = select(User).where(User.email == email)
            result = await session.execute(statement)
            user = result.scalar_one_or_none()

            if user:
                logger.info(f"User {user.id} found for email: {email}")
            else:
                logger.info(f"No user found for email: {email}")

            return user
        except Exception as e:
            logger.error(f"Error retrieving user by email {email}: {str(e)}")
            return None

    @staticmethod
    async def get_user_by_id(session: AsyncSession, user_id: UUID) -> Optional[User]:
        """Get a user by ID."""
        logger.info(f"Retrieving user by ID: {user_id}")

        try:
            statement = select(User).where(User.id == user_id)
            result = await session.execute(statement)
            user = result.scalar_one_or_none()

            if user:
                logger.info(f"User {user.id} found")
            else:
                logger.info(f"No user found for ID: {user_id}")

            return user
        except Exception as e:
            logger.error(f"Error retrieving user by ID {user_id}: {str(e)}")
            return None

    @staticmethod
    async def get_user_by_username(session: AsyncSession, username: str) -> Optional[User]:
        """Get a user by username."""
        logger.info(f"Retrieving user by username: {username}")

        try:
            statement = select(User).where(User.user_name == username)
            result = await session.execute(statement)
            user = result.scalar_one_or_none()

            if user:
                logger.info(f"User {user.id} found for username: {username}")
            else:
                logger.info(f"No user found for username: {username}")

            return user
        except Exception as e:
            logger.error(f"Error retrieving user by username {username}: {str(e)}")
            return None

    @staticmethod
    async def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a plain password against a hashed password."""
        try:
            return bcrypt.checkpw(
                plain_password.encode('utf-8'),
                hashed_password.encode('utf-8')
            )
        except Exception as e:
            logger.error(f"Error verifying password: {str(e)}")
            return False