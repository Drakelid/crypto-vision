"""
Security utilities including password hashing and JWT token handling.
"""
from datetime import datetime, timedelta
from typing import Any, Optional, Union

from jose import jwt
from passlib.context import CryptContext
from pydantic import ValidationError

from app.core.config import settings
from app.schemas.token import TokenPayload

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(
    subject: Union[str, Any], 
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token.
    
    Args:
        subject: The subject (usually user ID) to include in the token
        expires_delta: Optional timedelta for token expiration
        
    Returns:
        str: Encoded JWT token
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {"exp": expire, "sub": str(subject), "type": "access"}
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt

def create_refresh_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT refresh token.
    
    Args:
        subject: The subject (usually user ID) to include in the token
        expires_delta: Optional timedelta for token expiration
        
    Returns:
        str: Encoded JWT refresh token
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
    
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.
    
    Args:
        plain_password: The password to verify
        hashed_password: The hash to verify against
        
    Returns:
        bool: True if the password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Hash a password.
    
    Args:
        password: The password to hash
        
    Returns:
        str: The hashed password
    """
    return pwd_context.hash(password)

def verify_token(token: str) -> Optional[TokenPayload]:
    """
    Verify a JWT token.
    
    Args:
        token: The JWT token to verify
        
    Returns:
        Optional[TokenPayload]: The token payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
        return token_data
    except (jwt.JWTError, ValidationError):
        return None

def verify_access_token(token: str) -> Optional[TokenPayload]:
    """
    Verify an access token.
    
    Args:
        token: The JWT access token to verify
        
    Returns:
        Optional[TokenPayload]: The token payload if valid, None otherwise
    """
    token_data = verify_token(token)
    if token_data and token_data.type == "access":
        return token_data
    return None

def verify_refresh_token(token: str) -> Optional[TokenPayload]:
    """
    Verify a refresh token.
    
    Args:
        token: The JWT refresh token to verify
        
    Returns:
        Optional[TokenPayload]: The token payload if valid, None otherwise
    """
    token_data = verify_token(token)
    if token_data and token_data.type == "refresh":
        return token_data
    return None
