from typing import List, Optional
from sqlmodel import select, func
from uuid import UUID
from ..models import Testimonial, TestimonialCreate, TestimonialUpdate
from ..utils.logging_config import get_logger
from sqlalchemy.exc import IntegrityError, DisconnectionError, OperationalError
from sqlalchemy.ext.asyncio import AsyncSession


logger = get_logger(__name__)


class TestimonialService:
    @staticmethod
    async def create_testimonial(session: AsyncSession, user_id: UUID, testimonial_data: TestimonialCreate) -> Testimonial:
        """Create a new testimonial for a user."""
        logger.info(f"Creating testimonial for user {user_id}")

        # Create testimonial with user_id from authentication context
        testimonial = Testimonial(
            name=testimonial_data.name,
            email=testimonial_data.email,
            rating=testimonial_data.rating,
            message=testimonial_data.message,
            user_id=user_id
        )
        session.add(testimonial)
        await session.commit()
        await session.refresh(testimonial)

        logger.info(f"Testimonial {testimonial.id} created successfully for user {user_id}")
        return testimonial

    @staticmethod
    async def get_user_testimonials(session: AsyncSession, user_id: UUID) -> List[Testimonial]:
        """Get all testimonials for a specific user."""
        logger.info(f"Retrieving testimonials for user {user_id}")

        statement = select(Testimonial).where(Testimonial.user_id == user_id)
        result = await session.execute(statement)
        testimonials = result.scalars().all()

        logger.info(f"Found {len(testimonials)} testimonials for user {user_id}")
        return testimonials

    @staticmethod
    async def get_testimonials(session: AsyncSession) -> List[Testimonial]:
        """Get all testimonials from all users."""
        logger.info("Retrieving all testimonials")

        statement = select(Testimonial)
        result = await session.execute(statement)
        testimonials = result.scalars().all()

        logger.info(f"Found {len(testimonials)} testimonials")
        return testimonials

    @staticmethod
    async def get_testimonial_by_id(session: AsyncSession, user_id: UUID, testimonial_id: UUID) -> Optional[Testimonial]:
        """Get a specific testimonial by ID for a user."""
        logger.info(f"Retrieving testimonial {testimonial_id} for user {user_id}")

        statement = select(Testimonial).where(Testimonial.id == testimonial_id, Testimonial.user_id == user_id)
        result = await session.execute(statement)
        testimonial = result.scalar_one_or_none()

        if testimonial:
            logger.info(f"Testimonial {testimonial_id} found for user {user_id}")
        else:
            logger.info(f"Testimonial {testimonial_id} not found for user {user_id}")

        return testimonial

    @staticmethod
    async def update_testimonial(session: AsyncSession, user_id: UUID, testimonial_id: UUID, testimonial_data: TestimonialUpdate) -> Optional[Testimonial]:
        """Update a specific testimonial for a user."""
        logger.info(f"Updating testimonial {testimonial_id} for user {user_id}")

        statement = select(Testimonial).where(Testimonial.id == testimonial_id, Testimonial.user_id == user_id)
        result = await session.execute(statement)
        testimonial = result.scalar_one_or_none()

        if not testimonial:
            logger.warning(f"Testimonial {testimonial_id} not found for user {user_id}")
            return None

        # Update the testimonial with provided data
        update_data = testimonial_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(testimonial, field, value)

        testimonial.updated_at = func.now()  # Update timestamp

        try:
            await session.commit()
            await session.refresh(testimonial)
            logger.info(f"Testimonial {testimonial_id} updated successfully for user {user_id}")
            return testimonial
        except IntegrityError as e:
            logger.error(f"Error updating testimonial {testimonial_id}: {str(e)}")
            await session.rollback()
            raise

    @staticmethod
    async def delete_testimonial(session: AsyncSession, user_id: UUID, testimonial_id: UUID) -> bool:
        """Delete a specific testimonial for a user."""
        logger.info(f"Deleting testimonial {testimonial_id} for user {user_id}")

        statement = select(Testimonial).where(Testimonial.id == testimonial_id, Testimonial.user_id == user_id)
        result = await session.execute(statement)
        testimonial = result.scalar_one_or_none()

        if not testimonial:
            logger.warning(f"Testimonial {testimonial_id} not found for user {user_id}")
            return False

        await session.delete(testimonial)
        await session.commit()

        logger.info(f"Testimonial {testimonial_id} deleted successfully for user {user_id}")
        return True