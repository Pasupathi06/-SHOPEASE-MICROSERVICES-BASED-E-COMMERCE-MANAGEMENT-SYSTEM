"""
Pydantic Schemas for Product Validation, Search, and Serialization.
"""

from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from app.schemas.category_schema import CategoryResponse


class ProductBase(BaseModel):
    """Base product attributes."""
    name: str = Field(
        ...,
        min_length=2,
        max_length=150,
        description="Product name",
        examples=["Apple iPhone 15 Pro"]
    )
    description: Optional[str] = Field(
        default=None,
        description="Detailed product specifications",
        examples=["128GB, Natural Titanium, A17 Pro chip."]
    )
    sku: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Stock Keeping Unit (unique product code)",
        examples=["IPHONE15P-128-NAT"]
    )
    price: Decimal = Field(
        ...,
        gt=Decimal("0.0"),
        decimal_places=2,
        description="Regular retail price (greater than zero)",
        examples=[Decimal("999.99")]
    )
    discount_price: Optional[Decimal] = Field(
        default=None,
        gt=Decimal("0.0"),
        decimal_places=2,
        description="Discounted promotional price (must be less than regular price if set)",
        examples=[Decimal("949.99")]
    )
    stock_quantity: int = Field(
        default=0,
        ge=0,
        description="Initial stock quantity (non-negative integer)",
        examples=[50]
    )
    image_url: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Product image link",
        examples=["https://cdn.shopease.com/products/iphone15pro.jpg"]
    )
    brand: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Product brand or manufacturer",
        examples=["Apple"]
    )
    is_active: bool = Field(
        default=True,
        description="Product availability status"
    )
    category_id: int = Field(
        ...,
        gt=0,
        description="Valid ID of the product category",
        examples=[1]
    )

    @field_validator("name", "sku")
    @classmethod
    def validate_non_blank(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Field cannot be blank or only whitespace.")
        return stripped

    @model_validator(mode="after")
    def validate_discount(self) -> "ProductBase":
        if self.discount_price is not None and self.discount_price >= self.price:
            raise ValueError("Discount price must be less than the regular price.")
        return self


class ProductCreate(ProductBase):
    """Schema for creating a new product."""
    pass


class ProductUpdate(BaseModel):
    """Schema for fully or partially updating a product."""
    name: Optional[str] = Field(default=None, min_length=2, max_length=150)
    description: Optional[str] = Field(default=None)
    sku: Optional[str] = Field(default=None, min_length=3, max_length=50)
    price: Optional[Decimal] = Field(default=None, gt=Decimal("0.0"), decimal_places=2)
    discount_price: Optional[Decimal] = Field(default=None, gt=Decimal("0.0"), decimal_places=2)
    stock_quantity: Optional[int] = Field(default=None, ge=0)
    image_url: Optional[str] = Field(default=None, max_length=255)
    brand: Optional[str] = Field(default=None, max_length=100)
    is_active: Optional[bool] = Field(default=None)
    category_id: Optional[int] = Field(default=None, gt=0)


class ProductPatch(ProductUpdate):
    """Schema for partial update."""
    pass


class ProductResponse(ProductBase):
    """Response schema for a single product."""
    id: int
    created_at: datetime
    updated_at: datetime
    category: Optional[CategoryResponse] = None

    model_config = ConfigDict(from_attributes=True)


class ProductPaginationResponse(BaseModel):
    """Paginated product list response."""
    items: List[ProductResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
