"""API Routers Package for Product Catalog Microservice."""

from app.routers.category_routes import router as category_router
from app.routers.product_routes import router as product_router
from app.routers.inventory_routes import router as inventory_router

__all__ = ["category_router", "product_router", "inventory_router"]
