"""
Pydantic Schemas for Request and Response Validation.
Enforces validation rules on Product CRUD operations.
"""

from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, ConfigDict


class ProductStatus(str, Enum):
    """Predefined valid product status values."""
    ACTIVE = "Active"
    INACTIVE = "Inactive"


class ProductBase(BaseModel):
    """Base schema containing common product attributes."""
    product_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Name of the product (must not be empty, max 100 characters)",
        examples=["Wireless Noise-Canceling Headphones"]
    )
    product_description: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Optional detailed product description (max 500 characters)",
        examples=["Premium over-ear Bluetooth headphones with active noise cancellation."]
    )
    product_price: float = Field(
        ...,
        gt=0.0,
        description="Price of the product (must be greater than 0)",
        examples=[99.99]
    )
    stock_quantity: int = Field(
        ...,
        ge=0,
        description="Current stock quantity (non-negative integer)",
        examples=[50]
    )
    product_category: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Product category (2 to 50 characters)",
        examples=["Electronics"]
    )
    product_status: ProductStatus = Field(
        default=ProductStatus.ACTIVE,
        description="Product status (Active or Inactive)",
        examples=[ProductStatus.ACTIVE]
    )

    @field_validator("product_name")
    @classmethod
    def validate_name_not_blank(cls, value: str) -> str:
        """Ensure product name is not only whitespace."""
        stripped = value.strip()
        if not stripped:
            raise ValueError("Product name cannot be empty or whitespace only.")
        return stripped

    @field_validator("product_category")
    @classmethod
    def validate_category_not_blank(cls, value: str) -> str:
        """Ensure product category is not blank."""
        stripped = value.strip()
        if not stripped:
            raise ValueError("Product category cannot be empty or whitespace only.")
        return stripped

    @field_validator("product_description")
    @classmethod
    def validate_description(cls, value: Optional[str]) -> Optional[str]:
        """Strip description if provided."""
        if value is not None:
            stripped = value.strip()
            return stripped if stripped else None
        return None


class ProductCreate(ProductBase):
    """Schema for creating a new product."""
    pass


class ProductUpdate(BaseModel):
    """Schema for updating an existing product (all fields optional)."""
    product_name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="Updated product name (must not be empty, max 100 characters)"
    )
    product_description: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Updated product description (max 500 characters)"
    )
    product_price: Optional[float] = Field(
        default=None,
        gt=0.0,
        description="Updated product price (must be greater than 0)"
    )
    stock_quantity: Optional[int] = Field(
        default=None,
        ge=0,
        description="Updated stock quantity (non-negative integer)"
    )
    product_category: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=50,
        description="Updated product category (2 to 50 characters)"
    )
    product_status: Optional[ProductStatus] = Field(
        default=None,
        description="Updated product status (Active or Inactive)"
    )

    @field_validator("product_name")
    @classmethod
    def validate_name_if_present(cls, value: Optional[str]) -> Optional[str]:
        if value is not None:
            stripped = value.strip()
            if not stripped:
                raise ValueError("Product name cannot be empty or whitespace only.")
            return stripped
        return value

    @field_validator("product_category")
    @classmethod
    def validate_category_if_present(cls, value: Optional[str]) -> Optional[str]:
        if value is not None:
            stripped = value.strip()
            if not stripped:
                raise ValueError("Product category cannot be empty or whitespace only.")
            return stripped
        return value


class ProductResponse(ProductBase):
    """Schema for product responses returned to clients."""
    product_id: str = Field(description="Unique product identifier", examples=["PROD-1001"])
    created_date: str = Field(
        description="ISO 8601 creation timestamp",
        examples=["2026-11-03T09:30:00+00:00"]
    )

    model_config = ConfigDict(from_attributes=True)


class ProductDeleteResponse(BaseModel):
    """Response schema returned upon product deletion."""
    message: str = Field(description="Success message", examples=["Product deleted successfully."])
    product_id: str = Field(description="ID of the deleted product", examples=["PROD-1001"])


class ErrorResponse(BaseModel):
    """Consistent error response schema."""
    success: bool = False
    error: str = Field(description="Error message")
    detail: Optional[str] = Field(default=None, description="Detailed error description")
