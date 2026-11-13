"""
Product Business Logic Service.
Handles product creation, validation, search, filtering, pagination, and sorting.
"""

from typing import Optional, List, Tuple
from decimal import Decimal
import math
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, desc, asc
from fastapi import HTTPException, status
from app.models.product_model import Product
from app.models.category_model import Category
from app.models.inventory_model import InventoryTransaction
from app.schemas.product_schema import ProductCreate, ProductUpdate


class ProductService:
    """Service providing catalog product CRUD, advanced search, and filtering."""

    @staticmethod
    def get_product_by_id(db: Session, product_id: int, is_admin: bool = False) -> Product:
        """Fetch product by ID. If non-admin and product is inactive, returns 404."""
        product = db.query(Product).options(joinedload(Product.category)).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {product_id} was not found."
            )
        if not product.is_active and not is_admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {product_id} is currently unavailable."
            )
        return product

    @staticmethod
    def create_product(db: Session, product_in: ProductCreate) -> Product:
        """
        Create a new product.
        Validates SKU uniqueness, category existence, and logs initial inventory if stock > 0.
        """
        # 1. Validate Category
        category = db.query(Category).filter(Category.id == product_in.category_id).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with ID {product_in.category_id} was not found."
            )

        # 2. Validate SKU Uniqueness
        normalized_sku = product_in.sku.strip().upper()
        existing_sku = db.query(Product).filter(Product.sku == normalized_sku).first()
        if existing_sku:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product with SKU '{normalized_sku}' already exists."
            )

        # 3. Create Product
        product = Product(
            category_id=product_in.category_id,
            name=product_in.name.strip(),
            description=product_in.description,
            sku=normalized_sku,
            price=product_in.price,
            discount_price=product_in.discount_price,
            stock_quantity=product_in.stock_quantity,
            image_url=product_in.image_url,
            brand=product_in.brand,
            is_active=product_in.is_active
        )
        db.add(product)
        db.flush()

        # 4. If initial stock > 0, log audit transaction
        if product.stock_quantity > 0:
            tx = InventoryTransaction(
                product_id=product.id,
                transaction_type="IN",
                quantity=product.stock_quantity,
                previous_stock=0,
                updated_stock=product.stock_quantity,
                remarks="Initial Stock on Product Creation"
            )
            db.add(tx)

        db.commit()
        db.refresh(product)
        return product

    @staticmethod
    def list_products(
        db: Session,
        search: Optional[str] = None,
        category_id: Optional[int] = None,
        min_price: Optional[Decimal] = None,
        max_price: Optional[Decimal] = None,
        brand: Optional[str] = None,
        in_stock_only: Optional[bool] = None,
        page: int = 1,
        page_size: int = 10,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        is_admin: bool = False
    ) -> Tuple[List[Product], int, int]:
        """
        Search, filter, paginate, and sort products.
        Non-admins only see active products.
        """
        query = db.query(Product).options(joinedload(Product.category))

        # Filter by Active status for customers
        if not is_admin:
            query = query.filter(Product.is_active.is_(True))

        # Search by name or SKU
        if search:
            search_term = f"%{search.strip()}%"
            query = query.filter(or_(
                Product.name.ilike(search_term),
                Product.sku.ilike(search_term)
            ))

        # Category filter
        if category_id:
            query = query.filter(Product.category_id == category_id)

        # Price range filters
        if min_price is not None:
            query = query.filter(Product.price >= min_price)
        if max_price is not None:
            query = query.filter(Product.price <= max_price)

        # Brand filter
        if brand:
            query = query.filter(Product.brand.ilike(f"%{brand.strip()}%"))

        # In-stock filter
        if in_stock_only:
            query = query.filter(Product.stock_quantity > 0)

        # Total matching records count
        total = query.count()

        # Sorting logic
        sort_column_map = {
            "price": Product.price,
            "name": Product.name,
            "stock_quantity": Product.stock_quantity,
            "created_at": Product.created_at,
        }
        sort_col = sort_column_map.get(sort_by.lower(), Product.created_at)
        if sort_order.lower() == "asc":
            query = query.order_by(asc(sort_col))
        else:
            query = query.order_by(desc(sort_col))

        # Pagination
        offset = (page - 1) * page_size
        items = query.offset(offset).limit(page_size).all()
        total_pages = math.ceil(total / page_size) if total > 0 else 1

        return items, total, total_pages

    @staticmethod
    def update_product(
        db: Session,
        product_id: int,
        product_update: ProductUpdate,
        is_patch: bool = False
    ) -> Product:
        """Update product details and validate constraints."""
        product = ProductService.get_product_by_id(db, product_id, is_admin=True)

        update_dict = product_update.model_dump(exclude_unset=is_patch)

        # Validate category if changing
        if "category_id" in update_dict and update_dict["category_id"]:
            cat = db.query(Category).filter(Category.id == update_dict["category_id"]).first()
            if not cat:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Category with ID {update_dict['category_id']} does not exist."
                )

        # Validate SKU if changing
        if "sku" in update_dict and update_dict["sku"]:
            new_sku = update_dict["sku"].strip().upper()
            if new_sku != product.sku:
                dup = db.query(Product).filter(Product.sku == new_sku).first()
                if dup:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Product with SKU '{new_sku}' already exists."
                    )
            update_dict["sku"] = new_sku

        # Validate discount price logic
        price = update_dict.get("price", product.price)
        discount = update_dict.get("discount_price", product.discount_price)
        if discount is not None and discount >= price:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Discount price must be strictly less than the regular price."
            )

        for key, value in update_dict.items():
            if value is not None or not is_patch:
                setattr(product, key, value)

        db.add(product)
        db.commit()
        db.refresh(product)
        return product

    @staticmethod
    def delete_product(db: Session, product_id: int) -> None:
        """Deactivate or delete a product."""
        product = ProductService.get_product_by_id(db, product_id, is_admin=True)
        # Soft delete / deactivate
        product.is_active = False
        db.add(product)
        db.commit()

    @staticmethod
    def update_product_partial(db: Session, product_id: int, product_patch) -> Product:
        """Partial update helper method."""
        return ProductService.update_product(db, product_id, product_patch, is_patch=True)

    # Alias for flexibility
    get_products = list_products


product_service = ProductService()
