"""
Application Configuration Settings.
Loads configuration from environment variables with sensible defaults.
"""

import os
from pydantic import BaseModel
from dotenv import load_dotenv

# Load .env file if present
load_dotenv()


class Settings(BaseModel):
    """Application settings class."""
    APP_NAME: str = os.getenv("APP_NAME", "ShopEase Product Service")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    APP_DESCRIPTION: str = os.getenv(
        "APP_DESCRIPTION",
        "Microservices-based Product Management Service for ShopEase E-Commerce platform."
    )
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8003"))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")
    API_PREFIX: str = os.getenv("API_PREFIX", "/api/products")


settings = Settings()
