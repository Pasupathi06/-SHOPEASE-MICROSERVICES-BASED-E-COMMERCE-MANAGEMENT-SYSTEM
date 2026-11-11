"""
Delivery Address REST API Router.
Endpoints for customer delivery address management with ownership protection.
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, status, Path
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.core.security import get_current_auth_user
from app.schemas.address_schema import (
    AddressCreate,
    AddressUpdate,
    AddressResponse,
)
from app.schemas.user_schema import MessageResponse
from app.services.address_service import address_service

router = APIRouter(
    prefix="/addresses",
    tags=["Delivery Addresses"],
)


@router.post(
    "",
    response_model=AddressResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a new delivery address",
    description="Adds a shipping address for the authenticated customer.",
)
def add_address(
    addr_in: AddressCreate,
    auth_user: Dict[str, Any] = Depends(get_current_auth_user),
    db: Session = Depends(get_db)
):
    """Add address endpoint."""
    return address_service.create_address(db, auth_user["auth_user_id"], addr_in)


@router.get(
    "",
    response_model=List[AddressResponse],
    status_code=status.HTTP_200_OK,
    summary="List current user addresses",
    description="Retrieves all delivery addresses for the authenticated user, default first.",
)
def list_addresses(
    auth_user: Dict[str, Any] = Depends(get_current_auth_user),
    db: Session = Depends(get_db)
):
    """List addresses endpoint."""
    return address_service.get_user_addresses(db, auth_user["auth_user_id"])


@router.get(
    "/{address_id}",
    response_model=AddressResponse,
    status_code=status.HTTP_200_OK,
    summary="Get specific delivery address",
    description="Fetches an address by ID. Enforces ownership check.",
)
def get_address(
    address_id: int = Path(..., description="Unique address identifier"),
    auth_user: Dict[str, Any] = Depends(get_current_auth_user),
    db: Session = Depends(get_db)
):
    """Get single address endpoint."""
    return address_service.get_address_by_id(db, auth_user["auth_user_id"], address_id)


@router.put(
    "/{address_id}",
    response_model=AddressResponse,
    status_code=status.HTTP_200_OK,
    summary="Update delivery address",
    description="Updates an address by ID. Enforces ownership check.",
)
def update_address(
    address_id: int = Path(..., description="Unique address identifier"),
    addr_in: AddressUpdate = ...,
    auth_user: Dict[str, Any] = Depends(get_current_auth_user),
    db: Session = Depends(get_db)
):
    """Update address endpoint."""
    return address_service.update_address(db, auth_user["auth_user_id"], address_id, addr_in)


@router.delete(
    "/{address_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete delivery address",
    description="Deletes an address by ID. Enforces ownership check.",
)
def delete_address(
    address_id: int = Path(..., description="Unique address identifier"),
    auth_user: Dict[str, Any] = Depends(get_current_auth_user),
    db: Session = Depends(get_db)
):
    """Delete address endpoint."""
    address_service.delete_address(db, auth_user["auth_user_id"], address_id)
    return MessageResponse(
        success=True,
        message=f"Address {address_id} deleted successfully."
    )


@router.patch(
    "/{address_id}/default",
    response_model=AddressResponse,
    status_code=status.HTTP_200_OK,
    summary="Set default delivery address",
    description="Designates the specified address as default and unsets all other addresses.",
)
def set_default_address(
    address_id: int = Path(..., description="Unique address identifier to set as default"),
    auth_user: Dict[str, Any] = Depends(get_current_auth_user),
    db: Session = Depends(get_db)
):
    """Set default address endpoint."""
    return address_service.set_default_address(db, auth_user["auth_user_id"], address_id)
