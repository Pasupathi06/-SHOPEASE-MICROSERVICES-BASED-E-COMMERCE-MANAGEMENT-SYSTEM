"""
Database Connection & Session Management.
Supports MySQL 8 with automatic fallback to SQLite for local standalone development.
"""

import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

logger = logging.getLogger("uvicorn.error")

Base = declarative_base()

# Attempt MySQL connection; if not available locally, use SQLite fallback
engine = None
try:
    if settings.DATABASE_URL.startswith("mysql"):
        # Test connecting to MySQL engine
        test_engine = create_engine(
            settings.DATABASE_URL,
            pool_pre_ping=True,
            pool_recycle=3600,
            connect_args={"connect_timeout": 3}
        )
        with test_engine.connect() as conn:
            pass
        engine = test_engine
        logger.info(f"Connected successfully to MySQL database: {settings.MYSQL_DATABASE}")
    else:
        engine = create_engine(settings.DATABASE_URL)
except Exception as e:
    logger.warning(
        f"MySQL database not immediately reachable at {settings.MYSQL_HOST}:{settings.MYSQL_PORT}. "
        f"Using local SQLite database for standalone execution. Error: {e}"
    )
    # Safe local fallback for testing without external MySQL
    engine = create_engine(
        "sqlite:///./shopease_auth.db",
        connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    FastAPI dependency yielding a database session and guaranteeing proper closure.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all database tables based on models."""
    Base.metadata.create_all(bind=engine)
