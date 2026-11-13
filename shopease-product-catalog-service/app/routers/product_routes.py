"""
Product REST API Router.
Endpoints for Catalog Product Management with advanced filtering, search, pagination, and RBAC.
"""

from typing import Optional, Dict, Any
from decimal import Decimal
from fastapi import APIRouter, Depends, status, Path, Query
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.core.security import require_admin, get_current_user_optional
from app.schemas.product_schema import (
    ProductCreate,
    ProductUpdate,
    ProductPatch,
    ProductResponse,
    ProductPaginationResponse,
)
from app.schemas.category_schema import MessageResponse
from app.services.product_service import product_service

router = APIRouter(
    prefix="/products",
    tags=["Products"],
)


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create product (Admin Only)",
    description="Creates a new catalog product with initial stock tracking. Requires Admin role.",
)
def create_product(
    product_in: ProductCreate,
    current_admin: Dict[str, Any] = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create product endpoint."""
    return product_service.create_product(db, product_in)


@router.get(
    "",
    response_model=ProductPaginationResponse,
    status_code=status.HTTP_200_OK,
    summary="List products with search, filters, pagination, and sorting",
    description="Public endpoint supporting search by name/SKU, category filtering, price bounds, sorting, and pagination.",
)
def list_products(
    search: Optional[str] = Query(default=None, description="Search keyword matching product name or SKU"),
    category_id: Optional[int] = Query(default=None, description="Filter by category ID"),
    min_price: Optional[Decimal] = Query(default=None, ge=Decimal("0.0"), description="Minimum price filter"),
    max_price: Optional[Decimal] = Query(default=None, ge=Decimal("0.0"), description="Maximum price filter"),
    brand: Optional[str] = Query(default=None, description="Filter by manufacturer brand"),
    in_stock_only: Optional[bool] = Query(default=False, description="Filter items with stock > 0"),
    page: int = Query(default=1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(default=10, ge=1, le=100, description="Items per page"),
    sort_by: str = Query(default="created_at", regex="^(price|name|created_at|stock_quantity)$", description="Field to sort by"),
    sort_order: str = Query(default="desc", regex="^(asc|desc)$", description="Sorting direction"),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Search and filter products endpoint."""
    is_admin = current_user is not None and current_user.get("role") == "admin"
    items, total, total_pages = product_service.list_products(
        db=db,
        search=search,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        brand=brand,
        in_stock_only=in_stock_only,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
        is_admin=is_admin
    )
    return ProductPaginationResponse(
        items=[ProductResponse.model_validate(p) for p in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Get product details",
    description="Retrieves a single product by ID. Inactive products are only accessible by Admins.",
)
def get_product(
    product_id: int = Path(..., description="Unique product identifier"),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Get product by ID endpoint."""
    is_admin = current_user is not None and current_user.get("role") == "admin"
    product = product_service.get_product_by_id(db, product_id, is_admin=is_admin)
    return ProductResponse.model_validate(product)


@router.put(
    "/{product_id}",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Update product (Admin Only)",
    description="Updates existing product information. Requires Admin role.",
)
def update_product(
    product_id: int = Path(..., description="Unique product identifier"),
    product_update: ProductUpdate = ...,
    current_admin: Dict[str, Any] = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update product endpoint."""
    product = product_service.update_product(db, product_id, product_update, is_patch=False)
    return ProductResponse.model_validate(product)


@router.patch(
    "/{product_id}",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Partially update product (Admin Only)",
    description="Updates only supplied fields of an existing product. Requires Admin role.",
)
def patch_product(
    product_id: int = Path(..., description="Unique product identifier"),
    product_patch: ProductPatch = ...,
    current_admin: Dict[str, Any] = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Patch product endpoint."""
    product = product_service.update_product(db, product_id, product_patch, is_patch=True)
    return ProductResponse.model_validate(product)


@router.delete(
    "/{product_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete / Deactivate product (Admin Only)",
    description="Deactivates a product from public catalog listings. Requires Admin role.",
)
def delete_product(
    product_id: int = Path(..., description="Unique product identifier"),
    current_admin: Dict[str, Any] = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete product endpoint."""
    product_service.delete_product(db, product_id)
    return MessageResponse(
        success=True,
        message=f"Product with ID {product_id} deactivated successfully."
    )
