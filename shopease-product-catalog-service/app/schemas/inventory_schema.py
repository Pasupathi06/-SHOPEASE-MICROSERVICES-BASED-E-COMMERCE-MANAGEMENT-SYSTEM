"""
Pydantic Schemas for Inventory Operations & Stock Auditing.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class StockAdjustmentRequest(BaseModel):
    """Schema for stock-in or stock-out operations."""
    quantity: int = Field(
        ...,
        gt=0,
        description="Quantity of units to add or remove (must be greater than zero)",
        examples=[25]
    )
    remarks: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Reason or reference for stock adjustment",
        examples=["PO-9821 Shipment Arrival"]
    )


class InventoryTransactionResponse(BaseModel):
    """Schema representing an immutable inventory audit record."""
    id: int
    product_id: int
    transaction_type: str
    quantity: int
    previous_stock: int
    updated_stock: int
    remarks: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StockStatusResponse(BaseModel):
    """Summary of product stock status."""
    product_id: int
    product_name: str
    sku: str
    stock_quantity: int
    is_low_stock: bool
    low_stock_threshold: int
