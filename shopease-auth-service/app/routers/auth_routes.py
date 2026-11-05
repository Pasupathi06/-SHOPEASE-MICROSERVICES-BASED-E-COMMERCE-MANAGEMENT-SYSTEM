"""
Authentication API Endpoints Router.
Implements Register, Login, Me, Verify-Token, and Change-Password routes.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.user_model import User
from app.schemas.auth_schema import (
    UserRegister,
    UserLogin,
    UserResponse,
    RegisterResponse,
    TokenResponse,
    TokenVerifyRequest,
    TokenVerifyResponse,
    ChangePasswordRequest,
    MessageResponse,
)
from app.services.auth_service import auth_service
from app.core.security import get_current_user

router = APIRouter(
    prefix="",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Registers new user account with hashed password and default customer role.",
)
def register(
    user_in: UserRegister,
    db: Session = Depends(get_db)
):
    """User Registration Endpoint."""
    user = auth_service.register_user(db, user_in)
    return RegisterResponse(
        message="User registered successfully.",
        user=UserResponse.model_validate(user)
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate user and obtain JWT token",
    description="Authenticates email & password, verifies account status, and issues a JWT access token.",
)
def login(
    login_in: UserLogin,
    db: Session = Depends(get_db)
):
    """User Login Endpoint."""
    user, access_token = auth_service.authenticate_user(db, login_in)
    return TokenResponse(
        message="Authentication successful.",
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current authenticated user profile",
    description="Extracts user identity from JWT Bearer token and returns profile data.",
)
def get_me(
    current_user: User = Depends(get_current_user)
):
    """Protected Current User Profile Endpoint."""
    return UserResponse.model_validate(current_user)


@router.post(
    "/verify-token",
    response_model=TokenVerifyResponse,
    status_code=status.HTTP_200_OK,
    summary="Validate JWT access token",
    description="Inspects token signature, integrity, and expiration status.",
)
def verify_token(
    verify_in: TokenVerifyRequest
):
    """Token Validation Endpoint."""
    is_valid, msg, payload = auth_service.verify_token(verify_in.token)
    return TokenVerifyResponse(
        valid=is_valid,
        message=msg,
        payload=payload
    )


@router.post(
    "/change-password",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Change user password",
    description="Updates account password after verifying current credentials. Requires JWT Bearer token.",
)
def change_password(
    change_in: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Protected Password Change Endpoint."""
    auth_service.change_password(db, current_user, change_in)
    return MessageResponse(
        success=True,
        message="Password updated successfully."
    )
