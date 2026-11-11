"""
Pydantic Schemas for User Profile Validation & Serialization.
"""

from typing import Optional
from datetime import date, datetime
import re
from pydantic import BaseModel, Field, field_validator, ConfigDict


def validate_phone(phone: Optional[str]) -> Optional[str]:
    """Validate phone number format if provided."""
    if phone is not None:
        cleaned = re.sub(r"[\s\-\(\)\+]", "", phone)
        if not (7 <= len(cleaned) <= 15 and cleaned.isdigit()):
            raise ValueError("Phone number must contain between 7 and 15 digits.")
        return phone.strip()
    return None


class UserProfileBase(BaseModel):
    """Base profile attributes."""
    full_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Full customer name",
        examples=["Pasupathi"]
    )
    phone_number: Optional[str] = Field(
        default=None,
        description="Contact phone number",
        examples=["+919876543210"]
    )
    date_of_birth: Optional[date] = Field(
        default=None,
        description="Date of birth (YYYY-MM-DD)",
        examples=["1998-05-15"]
    )
    gender: Optional[str] = Field(
        default=None,
        max_length=20,
        description="Gender (Male, Female, Other)",
        examples=["Male"]
    )
    profile_image: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Profile image URL or file path",
        examples=["https://cdn.shopease.com/avatars/pasu.png"]
    )

    @field_validator("phone_number")
    @classmethod
    def check_phone(cls, v: Optional[str]) -> Optional[str]:
        return validate_phone(v)

    @field_validator("full_name")
    @classmethod
    def check_name(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Full name cannot be blank or whitespace only.")
        return stripped


class UserProfileCreate(UserProfileBase):
    """Schema for creating a user profile."""
    pass


class UserProfileUpdate(BaseModel):
    """Schema for fully updating a user profile."""
    full_name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    phone_number: Optional[str] = Field(default=None)
    date_of_birth: Optional[date] = Field(default=None)
    gender: Optional[str] = Field(default=None, max_length=20)
    profile_image: Optional[str] = Field(default=None, max_length=255)

    @field_validator("phone_number")
    @classmethod
    def check_phone(cls, v: Optional[str]) -> Optional[str]:
        return validate_phone(v)


class UserProfilePatch(UserProfileUpdate):
    """Schema for partially updating a user profile."""
    pass


class UserProfileResponse(UserProfileBase):
    """Response schema returned for user profiles."""
    id: int
    auth_user_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MessageResponse(BaseModel):
    """Generic status response schema."""
    success: bool = True
    message: str
