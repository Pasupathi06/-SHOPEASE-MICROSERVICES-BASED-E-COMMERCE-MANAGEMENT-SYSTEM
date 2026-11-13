"""
Category Business Logic Service.
Handles category CRUD and ensures integrity against deleting populated categories.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.category_model import Category
from app.models.product_model import Product
from app.schemas.category_schema import CategoryCreate, CategoryUpdate


class CategoryService:
    """Service providing category operations and constraint checks."""

    @staticmethod
    def get_category_by_id(db: Session, category_id: int) -> Category:
        """Fetch category by ID or raise 404."""
        cat = db.query(Category).filter(Category.id == category_id).first()
        if not cat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with ID {category_id} was not found."
            )
        return cat

    @staticmethod
    def create_category(db: Session, cat_in: CategoryCreate) -> Category:
        """Create a new category. Rejects duplicate names."""
        normalized_name = cat_in.name.strip()
        existing = db.query(Category).filter(Category.name.ilike(normalized_name)).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category with name '{normalized_name}' already exists."
            )

        category = Category(
            name=normalized_name,
            description=cat_in.description,
            is_active=cat_in.is_active
        )
        db.add(category)
        db.commit()
        db.refresh(category)
        return category

    @staticmethod
    def list_categories(db: Session, include_inactive: bool = False) -> List[Category]:
        """List categories. Customers only see active categories."""
        query = db.query(Category)
        if not include_inactive:
            query = query.filter(Category.is_active.is_(True))
        return query.order_by(Category.name.asc()).all()

    @staticmethod
    def update_category(db: Session, category_id: int, cat_update: CategoryUpdate) -> Category:
        """Update category attributes."""
        category = CategoryService.get_category_by_id(db, category_id)

        update_dict = cat_update.model_dump(exclude_unset=True)
        if "name" in update_dict and update_dict["name"]:
            new_name = update_dict["name"].strip()
            if new_name.lower() != category.name.lower():
                dup = db.query(Category).filter(Category.name.ilike(new_name)).first()
                if dup:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Category with name '{new_name}' already exists."
                    )
            update_dict["name"] = new_name

        for key, value in update_dict.items():
            setattr(category, key, value)

        db.add(category)
        db.commit()
        db.refresh(category)
        return category

    @staticmethod
    def delete_category(db: Session, category_id: int) -> None:
        """
        Delete a category.
        Rejects deletion if products are currently assigned to this category.
        """
        category = CategoryService.get_category_by_id(db, category_id)

        # Check for associated products
        product_count = db.query(Product).filter(Product.category_id == category_id).count()
        if product_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete category '{category.name}'. It contains {product_count} product(s). Please reassign or delete products first."
            )

        db.delete(category)
        db.commit()


category_service = CategoryService()
