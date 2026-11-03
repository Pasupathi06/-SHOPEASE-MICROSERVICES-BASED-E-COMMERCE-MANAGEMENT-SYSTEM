"""
Product Data Model.
Represents the in-memory data structure for products in ShopEase.
"""

from typing import Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class ProductModel(BaseModel):
    """
    In-memory Product Data Model.
    Represents product entity stored in memory dictionary.
    """
    product_id: str = Field(description="Unique identifier for the product")
    product_name: str = Field(description="Name of the product")
    product_description: Optional[str] = Field(default=None, description="Detailed product description")
    product_price: float = Field(description="Unit price of the product (greater than zero)")
    stock_quantity: int = Field(description="Available stock quantity (non-negative integer)")
    product_category: str = Field(description="Category to which the product belongs")
    product_status: str = Field(description="Status of the product: 'Active' or 'Inactive'")
    created_date: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 timestamp when product was created"
    )

    def to_dict(self) -> dict:
        """Serialize model to dictionary."""
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: dict) -> "ProductModel":
        """Create model instance from dictionary."""
        return cls(**data)
