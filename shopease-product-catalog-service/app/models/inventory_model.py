"""
Inventory Transaction SQLAlchemy ORM Model.
Defines `inventory_transactions` table recording stock audit trails.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.connection import Base


class InventoryTransaction(Base):
    """SQLAlchemy model tracking stock adjustments and inventory history."""
    __tablename__ = "inventory_transactions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    transaction_type = Column(String(20), nullable=False)  # "IN" or "OUT"
    quantity = Column(Integer, nullable=False)
    previous_stock = Column(Integer, nullable=False)
    updated_stock = Column(Integer, nullable=False)
    remarks = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationship back to Product
    product = relationship("Product", back_populates="inventory_transactions")

    def __repr__(self) -> str:
        return f"<InventoryTransaction(id={self.id}, product_id={self.product_id}, type='{self.transaction_type}', qty={self.quantity}, stock={self.updated_stock})>"
