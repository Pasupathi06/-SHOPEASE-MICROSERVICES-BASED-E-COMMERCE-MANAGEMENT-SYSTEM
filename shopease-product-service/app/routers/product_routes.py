"""
Product API Endpoints Router.
Defines REST endpoints for Product CRUD operations.
"""

from typing import List, Optional
from fastapi import APIRouter, status, Query, Path
from app.schemas.product_schema import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductDeleteResponse,
)
from app.services.product_service import product_service

router = APIRouter(
    prefix="",
    tags=["Products"],
)


@router.post(
    "/",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new product",
    description="Accepts product payload, generates unique product ID, stores in memory, and returns created product.",
)
def create_product(product: ProductCreate):
    """Create a new product."""
    new_product = product_service.create_product(product)
    return new_product


@router.get(
    "/",
    response_model=List[ProductResponse],
    status_code=status.HTTP_200_OK,
    summary="Retrieve all products",
    description="Retrieves products with optional category filtering and pagination (skip/limit). Returns empty list if no products match.",
)
def get_all_products(
    category: Optional[str] = Query(
        default=None,
        description="Filter products by category name (case-insensitive)"
    ),
    skip: int = Query(
        default=0,
        ge=0,
        description="Number of products to skip for pagination"
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Maximum number of products to return"
    ),
):
    """Retrieve all products with filtering and pagination."""
    return product_service.get_all_products(category=category, skip=skip, limit=limit)


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve product by ID",
    description="Fetches a specific product by its unique product identifier. Returns 404 if not found.",
)
def get_product_by_id(
    product_id: str = Path(..., description="Unique product ID (e.g. PROD-1001)")
):
    """Retrieve product by its unique identifier."""
    return product_service.get_product_by_id(product_id)


@router.put(
    "/{product_id}",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Update product",
    description="Updates existing product fields. Returns updated product or 404 if not found.",
)
def update_product(
    product_id: str = Path(..., description="Unique product ID to update"),
    product_update: ProductUpdate = ...,
):
    """Update an existing product."""
    return product_service.update_product(product_id, product_update)


@router.delete(
    "/{product_id}",
    response_model=ProductDeleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete product",
    description="Deletes a product by ID. Returns success confirmation or 404 if not found.",
)
def delete_product(
    product_id: str = Path(..., description="Unique product ID to delete")
):
    """Delete an existing product."""
    product_service.delete_product(product_id)
    return ProductDeleteResponse(
        message="Product deleted successfully.",
        product_id=product_id
    )
