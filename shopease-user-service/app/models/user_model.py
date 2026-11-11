"""
User Profile SQLAlchemy ORM Model.
Defines `user_profiles` table mapping customer profile data linked via `auth_user_id`.
"""

from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.connection import Base


class UserProfile(Base):
    """SQLAlchemy model representing a customer profile."""
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    auth_user_id = Column(Integer, unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    phone_number = Column(String(20), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(String(20), nullable=True)
    profile_image = Column(String(255), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # 1-to-Many relationship with addresses
    addresses = relationship("Address", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<UserProfile(id={self.id}, auth_user_id={self.auth_user_id}, name='{self.full_name}')>"
