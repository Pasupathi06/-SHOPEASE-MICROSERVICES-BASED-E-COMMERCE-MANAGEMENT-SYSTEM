"""
Category REST API Router.
Endpoints for Category Management with Admin RBAC enforcement.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, status, Path, Query
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.core.security import require_admin, get_current_user_optional
from app.schemas.category_schema import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    MessageResponse,
)
from app.services.category_service import category_service

router = APIRouter(
    prefix="/categories",
    tags=["Product Categories"],
)


@router.post(
    "",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create category (Admin Only)",
    description="Creates a new product category. Requires Admin JWT Bearer token.",
)
def create_category(
    cat_in: CategoryCreate,
    current_admin: Dict[str, Any] = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create category endpoint."""
    return category_service.create_category(db, cat_in)


@router.get(
    "",
    response_model=List[CategoryResponse],
    status_code=status.HTTP_200_OK,
    summary="List all categories",
    description="Retrieves active categories for customers, or all categories if requested by an Admin.",
)
def list_categories(
    include_inactive: bool = Query(default=False, description="Include inactive categories (Admin only)"),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """List categories endpoint."""
    is_admin = current_user is not None and current_user.get("role") == "admin"
    show_inactive = include_inactive if is_admin else False
    return category_service.list_categories(db, include_inactive=show_inactive)


@router.get(
    "/{category_id}",
    response_model=CategoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get category details",
    description="Fetches category information by ID.",
)
def get_category(
    category_id: int = Path(..., description="Unique category identifier"),
    db: Session = Depends(get_db)
):
    """Get category by ID endpoint."""
    return category_service.get_category_by_id(db, category_id)


@router.put(
    "/{category_id}",
    response_model=CategoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Update category (Admin Only)",
    description="Updates existing category name, description, or active status.",
)
def update_category(
    category_id: int = Path(..., description="Unique category identifier"),
    cat_update: CategoryUpdate = ...,
    current_admin: Dict[str, Any] = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update category endpoint."""
    return category_service.update_category(db, category_id, cat_update)


@router.delete(
    "/{category_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete category (Admin Only)",
    description="Deletes category if no products are associated with it.",
)
def delete_category(
    category_id: int = Path(..., description="Unique category identifier"),
    current_admin: Dict[str, Any] = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete category endpoint."""
    category_service.delete_category(db, category_id)
    return MessageResponse(
        success=True,
        message=f"Category with ID {category_id} deleted successfully."
    )
