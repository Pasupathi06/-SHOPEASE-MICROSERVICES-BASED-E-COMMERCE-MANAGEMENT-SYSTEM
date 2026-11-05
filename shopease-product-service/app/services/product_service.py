"""
Product Service.
Handles business logic and in-memory storage for Product entities.
"""

from typing import Dict, List, Optional
import threading
from app.models.product_model import ProductModel
from app.schemas.product_schema import ProductCreate, ProductUpdate, ProductStatus


class ProductNotFoundException(Exception):
    """Raised when a requested product does not exist."""
    def __init__(self, product_id: str):
        self.product_id = product_id
        super().__init__(f"Product with ID '{product_id}' was not found.")


class DuplicateProductException(Exception):
    """Raised when attempting to create a product with duplicate identifier."""
    def __init__(self, message: str):
        super().__init__(message)


class InvalidProductDataException(Exception):
    """Raised when product data violates business rules."""
    def __init__(self, message: str):
        super().__init__(message)


class ProductService:
    """
    In-memory Product Service.
    Maintains a dictionary of products with thread-safe ID generation and operations.
    """

    def __init__(self) -> None:
        self._products: Dict[str, ProductModel] = {}
        self._id_counter: int = 1000
        self._lock = threading.Lock()

    def _generate_id(self) -> str:
        """Generate unique sequential product ID e.g. PROD-1001."""
        with self._lock:
            self._id_counter += 1
            return f"PROD-{self._id_counter}"

    def create_product(self, product_in: ProductCreate) -> ProductModel:
        """
        Create a new product and store it in-memory.
        """
        product_id = self._generate_id()
        product = ProductModel(
            product_id=product_id,
            product_name=product_in.product_name,
            product_description=product_in.product_description,
            product_price=product_in.product_price,
            stock_quantity=product_in.stock_quantity,
            product_category=product_in.product_category,
            product_status=product_in.product_status.value,
        )
        with self._lock:
            self._products[product_id] = product
        return product

    def get_all_products(
        self,
        category: Optional[str] = None,
        skip: int = 0,
        limit: int = 10,
    ) -> List[ProductModel]:
        """
        Retrieve all products with optional category filtering and pagination.
        """
        with self._lock:
            products_list = list(self._products.values())

        if category:
            normalized_cat = category.strip().lower()
            products_list = [
                p for p in products_list
                if p.product_category.strip().lower() == normalized_cat
            ]

        # Apply pagination
        return products_list[skip : skip + limit]

    def get_product_by_id(self, product_id: str) -> ProductModel:
        """
        Retrieve a single product by its unique product_id.
        Raises ProductNotFoundException if not found.
        """
        with self._lock:
            product = self._products.get(product_id)
        if not product:
            raise ProductNotFoundException(product_id)
        return product

    def update_product(self, product_id: str, product_update: ProductUpdate) -> ProductModel:
        """
        Update an existing product with provided fields.
        Raises ProductNotFoundException if not found.
        """
        with self._lock:
            product = self._products.get(product_id)
            if not product:
                raise ProductNotFoundException(product_id)

            update_dict = product_update.model_dump(exclude_unset=True)
            if not update_dict:
                return product

            # Update fields
            current_data = product.to_dict()
            for key, value in update_dict.items():
                if value is not None:
                    if isinstance(value, ProductStatus):
                        current_data[key] = value.value
                    else:
                        current_data[key] = value

            updated_product = ProductModel(**current_data)
            self._products[product_id] = updated_product
            return updated_product

    def delete_product(self, product_id: str) -> bool:
        """
        Delete a product by ID.
        Raises ProductNotFoundException if not found.
        """
        with self._lock:
            if product_id not in self._products:
                raise ProductNotFoundException(product_id)
            del self._products[product_id]
            return True

    def count_products(self, category: Optional[str] = None) -> int:
        """Return total count of products, optionally filtered by category."""
        with self._lock:
            if not category:
                return len(self._products)
            normalized_cat = category.strip().lower()
            return sum(
                1 for p in self._products.values()
                if p.product_category.strip().lower() == normalized_cat
            )

    def clear(self) -> None:
        """Reset in-memory storage (useful for testing)."""
        with self._lock:
            self._products.clear()
            self._id_counter = 1000


# Singleton service instance
product_service = ProductService()
