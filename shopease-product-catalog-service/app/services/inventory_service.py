"""
Inventory Business Logic Service.
Handles stock-in, stock-out, transaction history logging, and low-stock queries.
Enforces that stock cannot become negative and operations are ACID transactional.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.product_model import Product
from app.models.inventory_model import InventoryTransaction
from app.core.config import settings


class InventoryService:
    """Service providing stock adjustments and audit history."""

    @staticmethod
    def _get_product(db: Session, product_id: int) -> Product:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {product_id} was not found."
            )
        return product

    @staticmethod
    def get_stock(db: Session, product_id: int, threshold: Optional[int] = None) -> dict:
        """Retrieve current stock status."""
        product = InventoryService._get_product(db, product_id)
        limit = threshold if threshold is not None else settings.DEFAULT_LOW_STOCK_THRESHOLD
        return {
            "product_id": product.id,
            "product_name": product.name,
            "sku": product.sku,
            "stock_quantity": product.stock_quantity,
            "is_low_stock": product.stock_quantity <= limit,
            "low_stock_threshold": limit
        }

    @staticmethod
    def stock_in(db: Session, product_id: int, quantity: int, remarks: Optional[str] = None) -> InventoryTransaction:
        """
        Increase stock level and create immutable audit transaction.
        """
        if quantity <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Stock-in quantity must be greater than zero."
            )

        product = InventoryService._get_product(db, product_id)

        try:
            previous_stock = product.stock_quantity
            updated_stock = previous_stock + quantity
            product.stock_quantity = updated_stock

            tx = InventoryTransaction(
                product_id=product.id,
                transaction_type="IN",
                quantity=quantity,
                previous_stock=previous_stock,
                updated_stock=updated_stock,
                remarks=remarks or "Stock In Supply Restock"
            )

            db.add(product)
            db.add(tx)
            db.commit()
            db.refresh(tx)
            return tx
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to record stock-in: {str(e)}"
            )

    @staticmethod
    def stock_out(db: Session, product_id: int, quantity: int, remarks: Optional[str] = None) -> InventoryTransaction:
        """
        Decrease stock level with guard against negative inventory.
        """
        if quantity <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Stock-out quantity must be greater than zero."
            )

        product = InventoryService._get_product(db, product_id)

        if quantity > product.stock_quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient inventory. Available stock: {product.stock_quantity}, requested deduction: {quantity}."
            )

        try:
            previous_stock = product.stock_quantity
            updated_stock = previous_stock - quantity
            product.stock_quantity = updated_stock

            tx = InventoryTransaction(
                product_id=product.id,
                transaction_type="OUT",
                quantity=quantity,
                previous_stock=previous_stock,
                updated_stock=updated_stock,
                remarks=remarks or "Stock Out Order Fulfillment / Discard"
            )

            db.add(product)
            db.add(tx)
            db.commit()
            db.refresh(tx)
            return tx
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to record stock-out: {str(e)}"
            )

    @staticmethod
    def get_history(db: Session, product_id: int) -> List[InventoryTransaction]:
        """Fetch chronological transaction history for a product."""
        # Ensure product exists
        InventoryService._get_product(db, product_id)
        return db.query(InventoryTransaction).filter(
            InventoryTransaction.product_id == product_id
        ).order_by(InventoryTransaction.created_at.desc(), InventoryTransaction.id.desc()).all()

    @staticmethod
    def get_low_stock_products(db: Session, threshold: Optional[int] = None) -> List[Product]:
        """List active products below the low-stock threshold."""
        limit = threshold if threshold is not None else settings.DEFAULT_LOW_STOCK_THRESHOLD
        return db.query(Product).filter(
            Product.is_active.is_(True),
            Product.stock_quantity <= limit
        ).order_by(Product.stock_quantity.asc()).all()


inventory_service = InventoryService()
