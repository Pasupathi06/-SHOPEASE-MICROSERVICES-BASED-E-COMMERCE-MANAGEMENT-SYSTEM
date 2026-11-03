"""
ShopEase - Product Service Main Application.
Initializes FastAPI, registers routers, handles exceptions, and sets up middleware.
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import settings
from app.routers.product_routes import router as product_router
from app.services.product_service import (
    ProductNotFoundException,
    DuplicateProductException,
    InvalidProductDataException,
)

# Initialize FastAPI Application with rich metadata
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception Handlers
@app.exception_handler(ProductNotFoundException)
async def product_not_found_handler(request: Request, exc: ProductNotFoundException):
    """Handle missing product exceptions with consistent 404 response."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)},
    )


@app.exception_handler(DuplicateProductException)
async def duplicate_product_handler(request: Request, exc: DuplicateProductException):
    """Handle duplicate product exceptions with 400 response."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)},
    )


@app.exception_handler(InvalidProductDataException)
async def invalid_product_handler(request: Request, exc: InvalidProductDataException):
    """Handle invalid product data exceptions with 400 response."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)},
    )


# Register Routers
app.include_router(product_router, prefix="/api/products")


# System Endpoints
@app.get("/", tags=["System"])
def root():
    """Root endpoint welcoming clients to ShopEase Product Service."""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "online",
        "docs_url": "/docs",
    }


@app.get("/health", tags=["System"])
def health_check():
    """Health check endpoint for Docker / orchestration probes."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
