"""
Authentication Business Logic Service.
Handles user registration, credential verification, token generation, and password updates.
"""

from typing import Tuple, Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user_model import User
from app.schemas.auth_schema import UserRegister, UserLogin, ChangePasswordRequest
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)


class AuthService:
    """Service providing core authentication and user management workflows."""

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Fetch user record by normalized lowercase email."""
        return db.query(User).filter(User.email == email.strip().lower()).first()

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Fetch user record by primary key ID."""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def register_user(db: Session, user_data: UserRegister) -> User:
        """
        Register a new user in the database.
        Validates duplicate emails and hashes password before saving.
        """
        normalized_email = user_data.email.strip().lower()

        # Check for existing email registration
        existing = db.query(User).filter(User.email == normalized_email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"An account with email '{normalized_email}' is already registered."
            )

        # Hash password securely with bcrypt
        hashed_pwd = hash_password(user_data.password)

        new_user = User(
            full_name=user_data.full_name,
            email=normalized_email,
            password_hash=hashed_pwd,
            role="customer",
            is_active=True
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

    @staticmethod
    def authenticate_user(db: Session, login_data: UserLogin) -> Tuple[User, str]:
        """
        Authenticate user credentials and issue signed JWT access token.
        Raises 401 on incorrect credentials or 403 on deactivated account.
        """
        normalized_email = login_data.email.strip().lower()
        user = db.query(User).filter(User.email == normalized_email).first()

        # Constant-time comparison check
        if not user or not verify_password(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive or disabled. Contact administrator.",
            )

        # Generate JWT token
        token_claims = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role,
        }
        access_token = create_access_token(token_claims)
        return user, access_token

    @staticmethod
    def change_password(db: Session, user: User, change_req: ChangePasswordRequest) -> None:
        """
        Change authenticated user password after verifying current credentials.
        """
        if not verify_password(change_req.current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password verification failed. Please try again."
            )

        # Hash and persist new password
        user.password_hash = hash_password(change_req.new_password)
        db.add(user)
        db.commit()
        db.refresh(user)

    @staticmethod
    def verify_token(token: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Verify token integrity and signature."""
        try:
            payload = decode_access_token(token)
            return True, "Token is active and valid.", payload
        except HTTPException as e:
            return False, e.detail, None
        except Exception as e:
            return False, str(e), None


auth_service = AuthService()
