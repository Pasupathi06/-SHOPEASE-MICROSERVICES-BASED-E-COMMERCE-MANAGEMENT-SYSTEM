"""
User Address Business Logic Service.
Enforces strict user ownership and maintains a single default delivery address constraint.
"""

from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.address_model import Address
from app.models.user_model import UserProfile
from app.schemas.address_schema import AddressCreate, AddressUpdate


class AddressService:
    """Service providing delivery address management with strict ownership authorization."""

    @staticmethod
    def _get_profile(db: Session, auth_user_id: int) -> UserProfile:
        profile = db.query(UserProfile).filter(UserProfile.auth_user_id == auth_user_id).first()
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found. Please create a profile before managing addresses."
            )
        return profile

    @staticmethod
    def create_address(db: Session, auth_user_id: int, addr_in: AddressCreate) -> Address:
        """
        Add a delivery address.
        If marked default, unsets default status from any existing addresses.
        If this is user's first address, automatically sets default.
        """
        profile = AddressService._get_profile(db, auth_user_id)

        existing_addresses = db.query(Address).filter(Address.user_id == profile.id).all()
        should_be_default = addr_in.is_default or len(existing_addresses) == 0

        if should_be_default:
            # Unset default on previous addresses
            db.query(Address).filter(Address.user_id == profile.id).update({"is_default": False})

        new_address = Address(
            user_id=profile.id,
            address_type=addr_in.address_type,
            full_name=addr_in.full_name,
            phone_number=addr_in.phone_number,
            address_line_1=addr_in.address_line_1,
            address_line_2=addr_in.address_line_2,
            city=addr_in.city,
            state=addr_in.state,
            country=addr_in.country,
            postal_code=addr_in.postal_code,
            is_default=should_be_default,
        )

        db.add(new_address)
        db.commit()
        db.refresh(new_address)
        return new_address

    @staticmethod
    def get_user_addresses(db: Session, auth_user_id: int) -> List[Address]:
        """List all addresses belonging to the authenticated user."""
        profile = AddressService._get_profile(db, auth_user_id)
        return db.query(Address).filter(Address.user_id == profile.id).order_by(Address.is_default.desc()).all()

    @staticmethod
    def get_address_by_id(db: Session, auth_user_id: int, address_id: int) -> Address:
        """
        Retrieve single address by ID while enforcing ownership check.
        Returns 404 if not found, 403 if address belongs to another user.
        """
        profile = AddressService._get_profile(db, auth_user_id)
        address = db.query(Address).filter(Address.id == address_id).first()

        if not address:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Address with ID {address_id} was not found."
            )

        if address.user_id != profile.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. You do not have permission to access another user's address."
            )

        return address

    @staticmethod
    def update_address(
        db: Session,
        auth_user_id: int,
        address_id: int,
        addr_update: AddressUpdate
    ) -> Address:
        """Update existing address fields."""
        address = AddressService.get_address_by_id(db, auth_user_id, address_id)

        update_dict = addr_update.model_dump(exclude_unset=True)

        if update_dict.get("is_default") is True:
            # Unset other defaults
            db.query(Address).filter(Address.user_id == address.user_id).update({"is_default": False})

        for key, value in update_dict.items():
            setattr(address, key, value)

        db.add(address)
        db.commit()
        db.refresh(address)
        return address

    @staticmethod
    def delete_address(db: Session, auth_user_id: int, address_id: int) -> None:
        """Delete an address owned by authenticated user."""
        address = AddressService.get_address_by_id(db, auth_user_id, address_id)
        db.delete(address)
        db.commit()

    @staticmethod
    def set_default_address(db: Session, auth_user_id: int, address_id: int) -> Address:
        """Set designated address as default and demote all other addresses."""
        address = AddressService.get_address_by_id(db, auth_user_id, address_id)

        # Unset all
        db.query(Address).filter(Address.user_id == address.user_id).update({"is_default": False})

        address.is_default = True
        db.add(address)
        db.commit()
        db.refresh(address)
        return address


address_service = AddressService()
