"""
Token related schemas.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    refresh_token: str
    token_type: str

class TokenPayload(BaseModel):
    """Schema for JWT token payload."""
    sub: Optional[str] = None  # Subject (user ID)
    exp: Optional[datetime] = None  # Expiration time
    type: Optional[str] = None  # Token type (access/refresh)
    
    class Config:
        from_attributes = True
