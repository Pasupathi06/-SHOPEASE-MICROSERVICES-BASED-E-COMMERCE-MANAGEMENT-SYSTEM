"""
Pydantic Schemas for Delivery Address Validation & Serialization.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict
from app.schemas.user_schema import validate_phone


class AddressBase(BaseModel):
    """Base delivery address attributes."""
    address_type: str = Field(
        default="Home",
        max_length=20,
        description="Address categorization (Home, Office, Other)",
        examples=["Home"]
    )
    full_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Recipient contact name",
        examples=["Pasupathi"]
    )
    phone_number: str = Field(
        ...,
        description="Contact phone number for delivery updates",
        examples=["+919876543210"]
    )
    address_line_1: str = Field(
        ...,
        min_length=3,
        max_length=255,
        description="Street address, building, apartment",
        examples=["123 Tech Park Avenue, Apt 4B"]
    )
    address_line_2: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Landmark, suite, or additional information",
        examples=["Near Cyber Gateway"]
    )
    city: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="City or town",
        examples=["Chennai"]
    )
    state: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="State or province",
        examples=["Tamil Nadu"]
    )
    country: str = Field(
        default="India",
        max_length=100,
        description="Country",
        examples=["India"]
    )
    postal_code: str = Field(
        ...,
        min_length=3,
        max_length=20,
        description="Postal / PIN code",
        examples=["600001"]
    )
    is_default: bool = Field(
        default=False,
        description="Whether this is the default shipping address",
        examples=[True]
    )

    @field_validator("phone_number")
    @classmethod
    def check_phone(cls, v: str) -> str:
        validated = validate_phone(v)
        if not validated:
            raise ValueError("Valid phone number is required.")
        return validated


class AddressCreate(AddressBase):
    """Schema for adding a new delivery address."""
    pass


class AddressUpdate(BaseModel):
    """Schema for updating an existing delivery address."""
    address_type: Optional[str] = Field(default=None, max_length=20)
    full_name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    phone_number: Optional[str] = Field(default=None)
    address_line_1: Optional[str] = Field(default=None, min_length=3, max_length=255)
    address_line_2: Optional[str] = Field(default=None, max_length=255)
    city: Optional[str] = Field(default=None, min_length=2, max_length=100)
    state: Optional[str] = Field(default=None, min_length=2, max_length=100)
    country: Optional[str] = Field(default=None, max_length=100)
    postal_code: Optional[str] = Field(default=None, min_length=3, max_length=20)
    is_default: Optional[bool] = Field(default=None)

    @field_validator("phone_number")
    @classmethod
    def check_phone(cls, v: Optional[str]) -> Optional[str]:
        return validate_phone(v)


class AddressResponse(AddressBase):
    """Response schema for delivery address."""
    id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
