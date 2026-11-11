"""
User Profile Business Logic Service.
Handles profile creation, retrieval, updates, and account deactivation.
"""

from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user_model import UserProfile
from app.schemas.user_schema import UserProfileCreate, UserProfileUpdate, UserProfilePatch


class UserService:
    """Service providing profile operations scoped to the authenticated user ID."""

    @staticmethod
    def get_profile_by_auth_id(db: Session, auth_user_id: int) -> Optional[UserProfile]:
        """Fetch profile by foreign auth user ID."""
        return db.query(UserProfile).filter(UserProfile.auth_user_id == auth_user_id).first()

    @staticmethod
    def create_profile(db: Session, auth_user_id: int, profile_in: UserProfileCreate) -> UserProfile:
        """
        Create a new customer profile.
        Rejects creation if a profile already exists for the given auth_user_id.
        """
        existing = db.query(UserProfile).filter(UserProfile.auth_user_id == auth_user_id).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User profile already exists for authenticated user ID {auth_user_id}."
            )

        new_profile = UserProfile(
            auth_user_id=auth_user_id,
            full_name=profile_in.full_name,
            phone_number=profile_in.phone_number,
            date_of_birth=profile_in.date_of_birth,
            gender=profile_in.gender,
            profile_image=profile_in.profile_image,
            is_active=True
        )

        db.add(new_profile)
        db.commit()
        db.refresh(new_profile)
        return new_profile

    @staticmethod
    def get_profile(db: Session, auth_user_id: int) -> UserProfile:
        """
        Retrieve profile for authenticated user.
        Raises 404 if profile does not exist.
        """
        profile = db.query(UserProfile).filter(UserProfile.auth_user_id == auth_user_id).first()
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found. Please create a profile first."
            )
        return profile

    @staticmethod
    def update_profile(
        db: Session,
        auth_user_id: int,
        update_data: UserProfileUpdate,
        is_patch: bool = False
    ) -> UserProfile:
        """
        Update profile details for the authenticated user.
        """
        profile = UserService.get_profile(db, auth_user_id)

        update_dict = update_data.model_dump(exclude_unset=is_patch)
        for key, value in update_dict.items():
            if value is not None or not is_patch:
                setattr(profile, key, value)

        db.add(profile)
        db.commit()
        db.refresh(profile)
        return profile

    @staticmethod
    def deactivate_or_delete_profile(db: Session, auth_user_id: int) -> None:
        """
        Deactivate user profile. Marks account as inactive while preserving history.
        """
        profile = UserService.get_profile(db, auth_user_id)
        profile.is_active = False
        db.add(profile)
        db.commit()


user_service = UserService()
