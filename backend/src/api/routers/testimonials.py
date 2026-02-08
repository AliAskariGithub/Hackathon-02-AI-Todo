from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import List
from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession
from ...models import (
    Testimonial, TestimonialCreate, TestimonialUpdate, TestimonialPublic,
    User
)
from ...services.testimonial_service import TestimonialService
from ...utils.database import get_async_session
from ...utils.logging_config import get_logger
from ...api.deps import get_current_user, verify_user_owns_resource

router = APIRouter(prefix="/api", tags=["testimonials"])
logger = get_logger(__name__)


@router.post("/testimonials", response_model=TestimonialPublic, status_code=status.HTTP_201_CREATED)
async def create_testimonial(
    request: Request,
    testimonial_data: TestimonialCreate,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
) -> TestimonialPublic:
    """
    Create a new testimonial for the authenticated user.

    Args:
        request: The incoming request object
        testimonial_data: The testimonial data to create
        current_user: The authenticated user from JWT token
        session: Database session

    Returns:
        The created testimonial
    """
    try:
        logger.info(f"Received request to create testimonial for user {current_user['sub']}")

        # Get the user_id from the current user's session (stored as 'sub' in JWT)
        user_id = UUID(current_user['sub'])

        testimonial = await TestimonialService.create_testimonial(session, user_id, testimonial_data)
        logger.info(f"Successfully created testimonial {testimonial.id} for user {user_id}")
        return testimonial
    except ValueError as ve:
        logger.error(f"Invalid user ID format: {str(ve)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    except Exception as e:
        logger.error(f"Error creating testimonial for user {current_user['sub']}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating testimonial"
        )


@router.get("/testimonials", response_model=List[TestimonialPublic])
async def get_all_testimonials(
    session: AsyncSession = Depends(get_async_session)
) -> List[TestimonialPublic]:
    """
    Get all testimonials from all users.

    Args:
        session: Database session

    Returns:
        A list of all testimonials
    """
    try:
        logger.info("Received request to get all testimonials")
        testimonials = await TestimonialService.get_testimonials(session)
        logger.info(f"Returning {len(testimonials)} testimonials")
        return testimonials
    except Exception as e:
        logger.error(f"Error retrieving testimonials: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving testimonials"
        )


@router.get("/{user_id}/testimonials", response_model=List[TestimonialPublic])
async def get_user_testimonials(
    request: Request,
    user_id: UUID,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
) -> List[TestimonialPublic]:
    """
    Get all testimonials for a specific user.

    Args:
        request: The incoming request object
        user_id: The ID of the user whose testimonials to retrieve
        current_user: The authenticated user from JWT token
        session: Database session

    Returns:
        A list of testimonials for the user
    """
    # Verify that the user_id in the token matches the user_id in the URL path
    await verify_user_owns_resource(request, str(user_id))

    try:
        logger.info(f"Received request to get testimonials for user {user_id}")
        testimonials = await TestimonialService.get_user_testimonials(session, user_id)
        logger.info(f"Returning {len(testimonials)} testimonials for user {user_id}")
        return testimonials
    except Exception as e:
        logger.error(f"Error retrieving testimonials for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving testimonials"
        )


@router.get("/{user_id}/testimonials/{testimonial_id}", response_model=TestimonialPublic)
async def get_testimonial(
    request: Request,
    user_id: UUID,
    testimonial_id: UUID,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
) -> TestimonialPublic:
    """
    Get a specific testimonial by ID for a user.

    Args:
        request: The incoming request object
        user_id: The ID of the user
        testimonial_id: The ID of the testimonial to retrieve
        current_user: The authenticated user from JWT token
        session: Database session

    Returns:
        The requested testimonial
    """
    # Verify that the user_id in the token matches the user_id in the URL path
    await verify_user_owns_resource(request, str(user_id))

    try:
        logger.info(f"Received request to get testimonial {testimonial_id} for user {user_id}")
        testimonial = await TestimonialService.get_testimonial_by_id(session, user_id, testimonial_id)

        if not testimonial:
            logger.warning(f"Testimonial {testimonial_id} not found for user {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Testimonial not found"
            )

        logger.info(f"Successfully retrieved testimonial {testimonial_id} for user {user_id}")
        return testimonial
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving testimonial {testimonial_id} for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving testimonial"
        )


@router.put("/{user_id}/testimonials/{testimonial_id}", response_model=TestimonialPublic)
async def update_testimonial(
    request: Request,
    user_id: UUID,
    testimonial_id: UUID,
    testimonial_data: TestimonialUpdate,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
) -> TestimonialPublic:
    """
    Update a specific testimonial for a user.

    Args:
        request: The incoming request object
        user_id: The ID of the user
        testimonial_id: The ID of the testimonial to update
        testimonial_data: The updated testimonial data
        current_user: The authenticated user from JWT token
        session: Database session

    Returns:
        The updated testimonial
    """
    # Verify that the user_id in the token matches the user_id in the URL path
    await verify_user_owns_resource(request, str(user_id))

    try:
        logger.info(f"Received request to update testimonial {testimonial_id} for user {user_id}")
        updated_testimonial = await TestimonialService.update_testimonial(session, user_id, testimonial_id, testimonial_data)

        if not updated_testimonial:
            logger.warning(f"Testimonial {testimonial_id} not found for user {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Testimonial not found"
            )

        logger.info(f"Successfully updated testimonial {testimonial_id} for user {user_id}")
        return updated_testimonial
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating testimonial {testimonial_id} for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating testimonial"
        )


@router.delete("/{user_id}/testimonials/{testimonial_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_testimonial(
    request: Request,
    user_id: UUID,
    testimonial_id: UUID,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
) -> None:
    """
    Delete a specific testimonial for a user.

    Args:
        request: The incoming request object
        user_id: The ID of the user
        testimonial_id: The ID of the testimonial to delete
        current_user: The authenticated user from JWT token
        session: Database session
    """
    # Verify that the user_id in the token matches the user_id in the URL path
    await verify_user_owns_resource(request, str(user_id))

    try:
        logger.info(f"Received request to delete testimonial {testimonial_id} for user {user_id}")
        success = await TestimonialService.delete_testimonial(session, user_id, testimonial_id)

        if not success:
            logger.warning(f"Testimonial {testimonial_id} not found for user {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Testimonial not found"
            )

        logger.info(f"Successfully deleted testimonial {testimonial_id} for user {user_id}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting testimonial {testimonial_id} for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting testimonial"
        )