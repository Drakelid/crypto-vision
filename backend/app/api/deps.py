"""
Dependencies for API endpoints.
"""
from typing import Generator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import security
from app.core.config import settings
from app.crud import user as crud_user
from app.db.session import SessionLocal
from app.models import User
from app.schemas.token import TokenPayload

# OAuth2 scheme for token authentication
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login/access-token"
)

# Dependency to get DB session
async def get_db() -> Generator:
    """
    Dependency that provides a database session.
    
    Yields:
        AsyncSession: Database session
    """
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# Dependency to get current user from token
async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(reusable_oauth2),
) -> User:
    """
    Dependency to get the current authenticated user from the token.
    
    Args:
        db: Database session
        token: JWT token
        
    Returns:
        User: Authenticated user
        
    Raises:
        HTTPException: If the token is invalid or the user doesn't exist
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    
    user = await crud_user.user.get(db, id=token_data.sub)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return user

# Dependency to get current active user
async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency to check if the current user is active.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User: User if active
        
    Raises:
        HTTPException: If the user is not active
    """
    if not crud_user.is_active(current_user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

# Dependency to get current active superuser
def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency to check if the current user is a superuser.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User: Superuser if active and has superuser privileges
        
    Raises:
        HTTPException: If the user is not a superuser
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user doesn't have enough privileges"
        )
    return current_user

# Dependency to check if user has a specific role
class RoleChecker:
    """
    Dependency to check if the current user has a specific role.
    """
    def __init__(self, role_name: str):
        self.role_name = role_name
    
    async def __call__(
        self, 
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ) -> User:
        """
        Check if the current user has the required role.
        
        Args:
            current_user: Current authenticated user
            db: Database session
            
        Returns:
            User: Current user if they have the required role
            
        Raises:
            HTTPException: If the user doesn't have the required role
        """
        from app.crud import user as crud_user
        
        has_role = await crud_user.user.has_role(
            db, str(current_user.id), self.role_name
        )
        
        if not has_role and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User doesn't have the required role: {self.role_name}"
            )
        
        return current_user
