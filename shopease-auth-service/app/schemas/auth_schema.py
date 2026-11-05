"""
Pydantic Schemas for Authentication Request & Response Validation.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator, ConfigDict


class UserRegister(BaseModel):
    """User Registration Request Schema."""
    full_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="User full name (2 to 100 characters)",
        examples=["Pasupathi"]
    )
    email: EmailStr = Field(
        ...,
        description="Valid unique email address",
        examples=["pasu@shopease.com"]
    )
    password: str = Field(
        ...,
        min_length=6,
        max_length=100,
        description="Password (minimum 6 characters)",
        examples=["pasupathi@123"]
    )
    confirm_password: str = Field(
        ...,
        min_length=6,
        max_length=100,
        description="Confirm password must match password",
        examples=["pasupathi@123"]
    )

    @field_validator("full_name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Full name cannot be blank or only whitespace.")
        return stripped

    @model_validator(mode="after")
    def passwords_match(self) -> "UserRegister":
        if self.password != self.confirm_password:
            raise ValueError("Password and confirm_password do not match.")
        return self


class UserLogin(BaseModel):
    """User Login Request Schema."""
    email: EmailStr = Field(
        ...,
        description="Registered user email",
        examples=["pasu@shopease.com"]
    )
    password: str = Field(
        ...,
        description="Account password",
        examples=["pasupathi@123"]
    )


class UserResponse(BaseModel):
    """User Public Profile Response Schema (never exposes password/hash)."""
    id: int = Field(description="Unique user identifier", examples=[1])
    full_name: str = Field(description="User full name", examples=["Pasupathi"])
    email: str = Field(description="User email address", examples=["pasu@shopease.com"])
    role: str = Field(description="User authorization role", examples=["customer"])
    is_active: bool = Field(description="Account active status", examples=[True])
    created_at: datetime = Field(description="Registration timestamp")

    model_config = ConfigDict(from_attributes=True)


class RegisterResponse(BaseModel):
    """Registration Success Response Schema."""
    message: str = Field(description="Success notification message", examples=["User registered successfully."])
    user: UserResponse


class TokenResponse(BaseModel):
    """Login / JWT Token Response Schema."""
    message: str = Field(description="Authentication status message", examples=["Login successful."])
    access_token: str = Field(description="Signed JWT access token")
    token_type: str = Field(default="bearer", description="Token authentication scheme")
    user: UserResponse


class TokenVerifyRequest(BaseModel):
    """Request schema for validating an existing JWT token."""
    token: str = Field(..., description="JWT token string to verify")


class TokenVerifyResponse(BaseModel):
    """Verification Response Schema."""
    valid: bool = Field(description="Whether the token is cryptographically valid and unexpired")
    message: str = Field(description="Token status description")
    payload: Optional[Dict[str, Any]] = Field(default=None, description="Decoded token payload claims")


class ChangePasswordRequest(BaseModel):
    """Password Change Request Schema."""
    current_password: str = Field(
        ...,
        description="Existing account password",
        examples=["pasupathi@123"]
    )
    new_password: str = Field(
        ...,
        min_length=6,
        max_length=100,
        description="New password (minimum 6 characters)",
        examples=["new_pasupathi@456"]
    )
    confirm_new_password: str = Field(
        ...,
        min_length=6,
        max_length=100,
        description="Confirm new password",
        examples=["new_pasupathi@456"]
    )

    @model_validator(mode="after")
    def validate_password_change(self) -> "ChangePasswordRequest":
        if self.new_password != self.confirm_new_password:
            raise ValueError("new_password and confirm_new_password do not match.")
        if self.new_password == self.current_password:
            raise ValueError("New password cannot be identical to current password.")
        return self


class MessageResponse(BaseModel):
    """Generic status response schema."""
    success: bool = True
    message: str = Field(description="Status message")
