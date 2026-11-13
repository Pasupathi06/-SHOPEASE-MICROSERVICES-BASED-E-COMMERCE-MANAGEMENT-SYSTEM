"""
Pydantic Schemas for Product Category Validation & Serialization.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict


class CategoryBase(BaseModel):
    """Base category attributes."""
    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Category name (unique)",
        examples=["Electronics"]
    )
    description: Optional[str] = Field(
        default=None,
        description="Category description",
        examples=["Smartphones, laptops, and consumer electronics."]
    )
    is_active: bool = Field(
        default=True,
        description="Category visibility status"
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Category name cannot be blank or only whitespace.")
        return stripped


class CategoryCreate(CategoryBase):
    """Schema for creating a category."""
    pass


class CategoryUpdate(BaseModel):
    """Schema for updating a category."""
    name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    description: Optional[str] = Field(default=None)
    is_active: Optional[bool] = Field(default=None)

    @field_validator("name")
    @classmethod
    def validate_name_if_present(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            stripped = v.strip()
            if not stripped:
                raise ValueError("Category name cannot be blank or only whitespace.")
            return stripped
        return v


class CategoryResponse(CategoryBase):
    """Response schema for category."""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MessageResponse(BaseModel):
    """Generic message response."""
    success: bool = True
    message: str
