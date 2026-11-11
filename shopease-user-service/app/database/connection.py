"""
Database Connection & Session Management for User Service.
Supports MySQL 8 with automatic fallback to SQLite for local standalone development.
"""

import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

logger = logging.getLogger("uvicorn.error")

Base = declarative_base()

# Attempt MySQL connection; fallback to SQLite for local standalone testing
engine = None
try:
    if settings.DATABASE_URL.startswith("mysql"):
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
    engine = create_engine(
        "sqlite:///./shopease_user.db",
        connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """FastAPI dependency providing transactional database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all user & address database tables."""
    Base.metadata.create_all(bind=engine)
