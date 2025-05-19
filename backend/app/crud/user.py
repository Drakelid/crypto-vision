"""
CRUD operations for Users.
"""
from typing import Any, Dict, Optional, Union

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models import User, UserRole, Role
from app.schemas.user import UserCreate, UserUpdate

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """CRUD operations for User model."""
    
    @staticmethod
    def is_active(user: User) -> bool:
        """Check if a user is active.
        
        Args:
            user: User object to check
            
        Returns:
            bool: True if user is active, False otherwise
        """
        return user.is_active
    
    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[User]:
        """Get a user by email."""
        result = await db.execute(
            select(User).where(User.email == email)
        )
        return result.scalars().first()
    
    async def create(self, db: AsyncSession, *, obj_in: UserCreate) -> User:
        """Create a new user with hashed password."""
        db_obj = User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
            is_active=obj_in.is_active if hasattr(obj_in, 'is_active') else True,
            is_superuser=obj_in.is_superuser if hasattr(obj_in, 'is_superuser') else False,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def update(
        self, 
        db: AsyncSession, 
        *, 
        db_obj: User, 
        obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        """Update a user, including password hashing if password is provided."""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
            
        if "password" in update_data and update_data["password"]:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
            
        return await super().update(db, db_obj=db_obj, obj_in=update_data)
    
    async def authenticate(
        self, 
        db: AsyncSession, 
        *, 
        email: str, 
        password: str
    ) -> Optional[User]:
        """Authenticate a user with email and password."""
        user = await self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
    
    def is_active(self, user: User) -> bool:
        """Check if user is active."""
        return user.is_active
    
    def is_superuser(self, user: User) -> bool:
        """Check if user is a superuser."""
        return user.is_superuser
    
    async def add_role(self, db: AsyncSession, user_id: str, role_name: str) -> bool:
        """Add a role to a user."""
        # Check if role exists
        result = await db.execute(
            select(Role).where(Role.name == role_name)
        )
        role = result.scalars().first()
        
        if not role:
            return False
            
        # Check if user already has this role
        result = await db.execute(
            select(UserRole).where(
                UserRole.user_id == user_id,
                UserRole.role_id == role.id
            )
        )
        existing = result.scalars().first()
        
        if existing:
            return True
            
        # Add role
        user_role = UserRole(user_id=user_id, role_id=role.id)
        db.add(user_role)
        await db.commit()
        return True
    
    async def remove_role(self, db: AsyncSession, user_id: str, role_name: str) -> bool:
        """Remove a role from a user."""
        # Find the role
        result = await db.execute(
            select(Role).where(Role.name == role_name)
        )
        role = result.scalars().first()
        
        if not role:
            return False
            
        # Find and delete the user role
        result = await db.execute(
            delete(UserRole).where(
                UserRole.user_id == user_id,
                UserRole.role_id == role.id
            )
        )
        await db.commit()
        return True
    
    async def has_role(self, db: AsyncSession, user_id: str, role_name: str) -> bool:
        """Check if a user has a specific role."""
        result = await db.execute(
            select(UserRole).join(Role).where(
                UserRole.user_id == user_id,
                Role.name == role_name
            )
        )
        return result.scalars().first() is not None

# Create a singleton instance
user = CRUDUser(User)
