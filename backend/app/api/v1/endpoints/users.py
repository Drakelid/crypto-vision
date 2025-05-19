"""
User related API endpoints.
"""
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models
from app.api import deps
from app.schemas.user import User, UserCreate, UserUpdate, UserWithRoles

router = APIRouter()

@router.get("/me", response_model=UserWithRoles)
async def read_user_me(
    current_user: models.User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    Get current user information.
    """
    # Get user roles
    user_roles = await crud.user.get_roles(db, user_id=str(current_user.id))
    
    # Convert to UserWithRoles schema
    user_data = current_user.__dict__
    user_data["roles"] = [role.name for role in user_roles]
    
    return UserWithRoles(**user_data)

@router.put("/me", response_model=User)
async def update_user_me(
    user_in: UserUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    Update current user information.
    """
    user = await crud.user.update(db, db_obj=current_user, obj_in=user_in)
    return user

@router.get("/", response_model=List[User])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_superuser),
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    Retrieve all users (admin only).
    """
    users = await crud.user.get_multi(db, skip=skip, limit=limit)
    return users

@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    Create a new user.
    
    This endpoint is open to everyone (no authentication required).
    """
    # Check if user with this email already exists
    user = await crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists",
        )
    
    # Create the user
    user = await crud.user.create(db, obj_in=user_in)
    
    # Add default 'viewer' role
    await crud.user.add_role(db, user_id=str(user.id), role_name="viewer")
    
    return user

@router.get("/{user_id}", response_model=User)
async def read_user(
    user_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    Get a specific user by ID.
    
    Users can only see their own information, unless they're an admin.
    """
    if str(current_user.id) != user_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    user = await crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    return user

@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: str,
    user_in: UserUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    Update a user.
    
    Users can only update their own information, unless they're an admin.
    """
    if str(current_user.id) != user_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    user = await crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Only admins can change superuser status
    if not current_user.is_superuser and hasattr(user_in, 'is_superuser'):
        delattr(user_in, 'is_superuser')
    
    user = await crud.user.update(db, db_obj=user, obj_in=user_in)
    return user

@router.delete("/{user_id}", response_model=User)
async def delete_user(
    user_id: str,
    current_user: models.User = Depends(deps.get_current_active_superuser),
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    Delete a user (admin only).
    """
    user = await crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Prevent deleting yourself
    if str(user.id) == str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete yourself",
        )
    
    user = await crud.user.remove(db, id=user_id)
    return user

@router.post("/{user_id}/roles/{role_name}", response_model=UserWithRoles)
async def add_user_role(
    user_id: str,
    role_name: str,
    current_user: models.User = Depends(deps.get_current_active_superuser),
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    Add a role to a user (admin only).
    """
    user = await crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    success = await crud.user.add_role(db, user_id=user_id, role_name=role_name)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to add role '{role_name}' to user",
        )
    
    # Get updated user with roles
    user = await crud.user.get(db, id=user_id)
    user_roles = await crud.user.get_roles(db, user_id=user_id)
    
    user_data = user.__dict__
    user_data["roles"] = [role.name for role in user_roles]
    
    return UserWithRoles(**user_data)

@router.delete("/{user_id}/roles/{role_name}", response_model=UserWithRoles)
async def remove_user_role(
    user_id: str,
    role_name: str,
    current_user: models.User = Depends(deps.get_current_active_superuser),
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    Remove a role from a user (admin only).
    """
    user = await crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    success = await crud.user.remove_role(db, user_id=user_id, role_name=role_name)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to remove role '{role_name}' from user",
        )
    
    # Get updated user with roles
    user = await crud.user.get(db, id=user_id)
    user_roles = await crud.user.get_roles(db, user_id=user_id)
    
    user_data = user.__dict__
    user_data["roles"] = [role.name for role in user_roles]
    
    return UserWithRoles(**user_data)
