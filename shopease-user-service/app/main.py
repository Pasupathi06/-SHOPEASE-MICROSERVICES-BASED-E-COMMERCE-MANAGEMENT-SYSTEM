"""
ShopEase - User Management Microservice Main Application.
Initializes FastAPI, registers Profile and Address routers, sets up CORS & database lifecycle.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.database.connection import init_db
from app.routers.user_routes import router as user_router
from app.routers.address_routes import router as address_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup & shutdown lifecycle handler."""
    init_db()
    yield


# Initialize FastAPI Application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description=settings.DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers under /api/users
app.include_router(user_router, prefix="/api/users")
app.include_router(address_router, prefix="/api/users")


# System Endpoints
@app.get("/", tags=["System"])
def root():
    """Root welcome endpoint for ShopEase User Service."""
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.PROJECT_VERSION,
        "status": "online",
        "docs_url": "/docs",
    }


@app.get("/health", tags=["System"])
def health_check():
    """Health check endpoint for Docker / orchestration probes."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
