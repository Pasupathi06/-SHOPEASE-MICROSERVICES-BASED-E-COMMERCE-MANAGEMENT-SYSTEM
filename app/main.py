"""
ShopEase - Authentication Microservice Main Application.
Initializes FastAPI, registers routers, handles lifecycle events, and seeds default credentials.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.database.connection import init_db, SessionLocal
from app.models.user_model import User
from app.core.security import hash_password
from app.routers.auth_routes import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle handler."""
    # 1. Initialize database tables
    init_db()

    # 2. Seed default user (pasu / pasupathi@123) if not already present
    db = SessionLocal()
    try:
        default_email = "pasu@shopease.com"
        existing = db.query(User).filter(User.email == default_email).first()
        if not existing:
            default_user = User(
                full_name="pasu",
                email=default_email,
                password_hash=hash_password("pasupathi@123"),
                role="admin",
                is_active=True
            )
            db.add(default_user)
            db.commit()
            print(f"[Startup] Default user created: {default_email} (Role: admin)")
    finally:
        db.close()

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

# Register Authentication Router
app.include_router(auth_router, prefix="/api/auth")


# System Endpoints
@app.get("/", tags=["System"])
def root():
    """Root endpoint welcoming clients to ShopEase Auth Service."""
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
