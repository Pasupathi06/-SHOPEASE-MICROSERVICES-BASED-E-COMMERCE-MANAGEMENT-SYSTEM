"""
User Address SQLAlchemy ORM Model.
Defines `user_addresses` table for customer delivery addresses.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.connection import Base


class Address(Base):
    """SQLAlchemy model representing a delivery address for a user profile."""
    __tablename__ = "user_addresses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    address_type = Column(String(20), nullable=False, default="Home")
    full_name = Column(String(100), nullable=False)
    phone_number = Column(String(20), nullable=False)
    address_line_1 = Column(String(255), nullable=False)
    address_line_2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    country = Column(String(100), nullable=False, default="India")
    postal_code = Column(String(20), nullable=False)
    is_default = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Many-to-1 relationship back to UserProfile
    user = relationship("UserProfile", back_populates="addresses")

    def __repr__(self) -> str:
        return f"<Address(id={self.id}, user_id={self.user_id}, type='{self.address_type}', city='{self.city}', default={self.is_default})>"
