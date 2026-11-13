"""
ShopEase Product Catalog Microservice - Main Application Entrypoint.
Initializes FastAPI, registers routers, configures CORS, and manages database lifecycle.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.config import settings
from app.database.connection import init_db, get_db
from app.routers.product_routes import router as product_router
from app.routers.category_routes import router as category_router
from app.routers.inventory_routes import router as inventory_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager: sets up DB tables on startup."""
    init_db()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description=settings.DESCRIPTION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS Middleware Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Microservice Routers with /api prefix
app.include_router(category_router, prefix="/api")
app.include_router(product_router, prefix="/api")
app.include_router(inventory_router, prefix="/api")


@app.get(
    "/",
    tags=["Service Information"],
    summary="Microservice Info & Documentation Links"
)
def root():
    """Returns basic service details and interactive API documentation links."""
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.PROJECT_VERSION,
        "status": "online",
        "port": settings.PORT,
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi_json": "/openapi.json"
        },
        "endpoints": {
            "categories": "/api/categories",
            "products": "/api/products",
            "inventory": "/api/inventory",
            "health": "/health"
        }
    }


@app.get(
    "/health",
    tags=["System Health"],
    summary="Microservice Health Check",
    status_code=status.HTTP_200_OK
)
def health_check(db: Session = Depends(get_db)):
    """
    Verifies that the API service is alive and the database connection is operational.
    """
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"unreachable ({str(e)})"

    return {
        "service": settings.PROJECT_NAME,
        "status": "healthy" if db_status == "connected" else "degraded",
        "database": db_status,
        "version": settings.PROJECT_VERSION
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
