"""
Core Application Configuration.
Loads environment variables and provides centralized application settings.
"""

import os
from urllib.parse import quote_plus
from pydantic import BaseModel
from dotenv import load_dotenv

# Load .env file
load_dotenv()


class Settings(BaseModel):
    """Authentication Microservice Settings."""
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "ShopEase Auth Service")
    PROJECT_VERSION: str = os.getenv("PROJECT_VERSION", "1.0.0")
    DESCRIPTION: str = os.getenv(
        "DESCRIPTION",
        "Independent JWT-based Authentication Microservice for ShopEase E-Commerce platform."
    )
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8001"))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")

    # API Prefix
    API_PREFIX: str = os.getenv("API_PREFIX", "/api/auth")

    # JWT Configuration
    JWT_SECRET_KEY: str = os.getenv(
        "JWT_SECRET_KEY",
        "shopease_jwt_super_secret_key_pasupathi_2026_secure_hash_key_123"
    )
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

    # Database Configuration
    MYSQL_HOST: str = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT: int = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER: str = os.getenv("MYSQL_USER", "pasu")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "pasupathi@123")
    MYSQL_DATABASE: str = os.getenv("MYSQL_DATABASE", "shopease_auth_db")

    @property
    def DATABASE_URL(self) -> str:
        custom_url = os.getenv("DATABASE_URL")
        if custom_url:
            return custom_url
        encoded_password = quote_plus(self.MYSQL_PASSWORD)
        return f"mysql+pymysql://{self.MYSQL_USER}:{encoded_password}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"


settings = Settings()
