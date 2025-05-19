"""
User related schemas.
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, validator

class UserBase(BaseModel):
    """Base user schema."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False

class UserCreate(UserBase):
    """Schema for creating a new user."""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    
    @validator('password')
    def password_strength(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one number')
        # Add more password strength requirements as needed
        return v

class UserUpdate(UserBase):
    """Schema for updating a user."""
    password: Optional[str] = Field(None, min_length=8, max_length=100)

class UserInDBBase(UserBase):
    """Base schema for user in database."""
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class User(UserInDBBase):
    """Schema for user response (without sensitive data)."""
    pass

class UserInDB(UserInDBBase):
    """Schema for user in database (with hashed password)."""
    hashed_password: str

class UserWithRoles(User):
    """Schema for user with roles."""
    roles: List[str] = []
    
    @classmethod
    def from_orm(cls, user, roles=None):
        """Create UserWithRoles from ORM user and roles."""
        user_dict = user.__dict__
        if hasattr(user, 'roles') and user.roles:
            user_dict['roles'] = [role.name for role in user.roles]
        elif roles is not None:
            user_dict['roles'] = roles
        else:
            user_dict['roles'] = []
        return cls(**user_dict)
