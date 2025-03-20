from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator
from models.user_role import UserRole


class UserBase(BaseModel):
    """Base user schema with common attributes."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=80)
    nickname: Optional[str] = Field(None, max_length=80)


class UserCreate(UserBase):
    """Schema for user creation with password."""
    password: str = Field(..., min_length=6)


class UserUpdate(BaseModel):
    """Schema for user updates with all fields optional."""
    email: Optional[EmailStr] = None
    nickname: Optional[str] = Field(None, max_length=80)

class UserChangePassword(BaseModel):
    """Schema for user change password."""
    email: Optional[EmailStr] = None
    old_password: str = Field(..., min_length=6)
    new_password: str = Field(..., min_length=6)

class UserRoleUpdate(BaseModel):
    """Schema for updating a user's role."""
    role: str
    
    @validator('role')
    def validate_role(cls, value):
        try:
            UserRole(value)
            return value
        except ValueError:
            raise ValueError(f"Invalid role: {value}. Must be one of {[r.value for r in UserRole]}")

class UserInDB(UserBase):
    """Schema for user in database with additional fields."""
    id: str  # Changed from int to str to match UUID string in database
    role: str = Field(default=UserRole.FREE.value)
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""
        from_attributes = True  # Allows model to be created from ORM objects


class UserResponse(UserBase):
    """Schema for user response without sensitive data."""
    id: str  # Changed from int to str to match UUID string in database
    role: str = Field(default=UserRole.FREE.value)
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""
        from_attributes = True

class UserLogin(BaseModel):
    """Schema for user login."""
    email: str
    password: str

    class Config:
        """Pydantic config."""
        from_attributes = True
