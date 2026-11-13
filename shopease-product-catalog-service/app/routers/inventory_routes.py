"""
Inventory Routing & Controller Layer.
Exposes endpoints for stock-in, stock-out, audit transactions, and low-stock alerts.
Guarded by JWT Role-Based Access Control (Admin-only for stock modifications and auditing).
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.core.security import require_admin
from app.schemas.inventory_schema import (
    StockAdjustmentRequest,
    InventoryTransactionResponse,
    StockStatusResponse
)
from app.schemas.product_schema import ProductResponse
from app.services.inventory_service import inventory_service

router = APIRouter(prefix="/inventory", tags=["Inventory Operations"])


@router.get(
    "/low-stock",
    response_model=List[ProductResponse],
    summary="Get low stock products (Admin only)",
    description="Lists all active products whose stock count is less than or equal to the threshold."
)
def get_low_stock_products(
    threshold: Optional[int] = Query(
        default=None,
        ge=0,
        description="Custom threshold limit (defaults to system setting, e.g., 10)"
    ),
    db: Session = Depends(get_db),
    current_admin: dict = Depends(require_admin)
):
    """Admin-only endpoint to view products needing restocking."""
    return inventory_service.get_low_stock_products(db, threshold=threshold)


@router.get(
    "/{product_id}",
    response_model=StockStatusResponse,
    summary="Check product stock status",
    description="Inspects real-time inventory level and low-stock warning flag for a product."
)
def get_product_stock_status(
    product_id: int,
    threshold: Optional[int] = Query(default=None, ge=0),
    db: Session = Depends(get_db)
):
    """Public or customer accessible stock status overview."""
    return inventory_service.get_stock(db, product_id, threshold=threshold)


@router.post(
    "/{product_id}/stock-in",
    response_model=InventoryTransactionResponse,
    status_code=status.HTTP_200_OK,
    summary="Increase product stock (Admin only)",
    description="Restocks inventory by adding quantity, logs transaction type 'IN', and records previous/updated stock."
)
def stock_in(
    product_id: int,
    payload: StockAdjustmentRequest,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(require_admin)
):
    """Admin-only endpoint to record inbound inventory arrival."""
    return inventory_service.stock_in(
        db=db,
        product_id=product_id,
        quantity=payload.quantity,
        remarks=payload.remarks
    )


@router.post(
    "/{product_id}/stock-out",
    response_model=InventoryTransactionResponse,
    status_code=status.HTTP_200_OK,
    summary="Decrease product stock (Admin only)",
    description="Deducts stock units, verifies stock does not become negative, and records immutable 'OUT' audit record."
)
def stock_out(
    product_id: int,
    payload: StockAdjustmentRequest,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(require_admin)
):
    """Admin-only endpoint to record stock deductions or fulfillment dispatches."""
    return inventory_service.stock_out(
        db=db,
        product_id=product_id,
        quantity=payload.quantity,
        remarks=payload.remarks
    )


@router.get(
    "/{product_id}/history",
    response_model=List[InventoryTransactionResponse],
    summary="Get stock audit history (Admin only)",
    description="Returns chronological audit log of all IN and OUT inventory transactions for a product."
)
def get_inventory_history(
    product_id: int,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(require_admin)
):
    """Admin-only endpoint for full compliance and auditing of inventory movements."""
    return inventory_service.get_history(db=db, product_id=product_id)
