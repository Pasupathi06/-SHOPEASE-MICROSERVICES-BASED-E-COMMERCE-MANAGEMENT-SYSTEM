"""Pydantic Schemas Package for Product Catalog Microservice."""

from app.schemas.category_schema import (
    CategoryBase,
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    MessageResponse
)
from app.schemas.product_schema import (
    ProductBase,
    ProductCreate,
    ProductUpdate,
    ProductPatch,
    ProductResponse,
    ProductPaginationResponse
)
from app.schemas.inventory_schema import (
    StockAdjustmentRequest,
    InventoryTransactionResponse,
    StockStatusResponse
)

__all__ = [
    "CategoryBase",
    "CategoryCreate",
    "CategoryUpdate",
    "CategoryResponse",
    "MessageResponse",
    "ProductBase",
    "ProductCreate",
    "ProductUpdate",
    "ProductPatch",
    "ProductResponse",
    "ProductPaginationResponse",
    "StockAdjustmentRequest",
    "InventoryTransactionResponse",
    "StockStatusResponse"
]
