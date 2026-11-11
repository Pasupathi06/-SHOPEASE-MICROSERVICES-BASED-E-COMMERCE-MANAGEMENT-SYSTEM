"""
User Profile REST API Router.
Endpoints for Customer Profile CRUD operations scoped to JWT identity.
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.core.security import get_current_auth_user
from app.schemas.user_schema import (
    UserProfileCreate,
    UserProfileUpdate,
    UserProfilePatch,
    UserProfileResponse,
    MessageResponse,
)
from app.services.user_service import user_service

router = APIRouter(
    prefix="/profile",
    tags=["User Profile"],
)


@router.post(
    "",
    response_model=UserProfileResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create user profile",
    description="Creates a profile for the currently authenticated user based on JWT token.",
)
def create_profile(
    profile_in: UserProfileCreate,
    auth_user: Dict[str, Any] = Depends(get_current_auth_user),
    db: Session = Depends(get_db)
):
    """Create profile endpoint."""
    profile = user_service.create_profile(db, auth_user["auth_user_id"], profile_in)
    return profile


@router.get(
    "",
    response_model=UserProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user profile",
    description="Fetches profile information for the authenticated user.",
)
def get_profile(
    auth_user: Dict[str, Any] = Depends(get_current_auth_user),
    db: Session = Depends(get_db)
):
    """Get current profile endpoint."""
    return user_service.get_profile(db, auth_user["auth_user_id"])


@router.put(
    "",
    response_model=UserProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Update user profile",
    description="Updates all profile fields for the authenticated user.",
)
def update_profile(
    profile_in: UserProfileUpdate,
    auth_user: Dict[str, Any] = Depends(get_current_auth_user),
    db: Session = Depends(get_db)
):
    """Full update profile endpoint."""
    return user_service.update_profile(db, auth_user["auth_user_id"], profile_in, is_patch=False)


@router.patch(
    "",
    response_model=UserProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Partially update user profile",
    description="Updates only provided fields of the authenticated user's profile.",
)
def patch_profile(
    profile_in: UserProfilePatch,
    auth_user: Dict[str, Any] = Depends(get_current_auth_user),
    db: Session = Depends(get_db)
):
    """Partial update profile endpoint."""
    return user_service.update_profile(db, auth_user["auth_user_id"], profile_in, is_patch=True)


@router.delete(
    "",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Deactivate user profile",
    description="Deactivates the customer profile in the User Service.",
)
def delete_profile(
    auth_user: Dict[str, Any] = Depends(get_current_auth_user),
    db: Session = Depends(get_db)
):
    """Deactivate profile endpoint."""
    user_service.deactivate_or_delete_profile(db, auth_user["auth_user_id"])
    return MessageResponse(
        success=True,
        message="User profile deactivated successfully."
    )
