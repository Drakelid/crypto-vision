"""
Alert related API endpoints.
"""
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models
from app.api import deps
from app.schemas.alert import Alert, AlertCreate, AlertUpdate
from app.schemas.user import User

router = APIRouter()

@router.get("/", response_model=List[Alert])
async def read_alerts(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve all alerts for the current user.
    """
    alerts = await crud.alert.get_multi(
        db, 
        skip=skip, 
        limit=limit,
        filter_dict={"user_id": str(current_user.id)}
    )
    return alerts

@router.get("/active/", response_model=List[Alert])
async def read_active_alerts(
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve all active alerts for the current user.
    """
    alerts = await crud.alert.get_active_alerts_for_user(
        db, 
        user_id=str(current_user.id)
    )
    return alerts

@router.get("/{alert_id}", response_model=Alert)
async def read_alert(
    alert_id: str,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get a specific alert by ID.
    """
    alert = await crud.alert.get(db, id=alert_id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found",
        )
    
    # Ensure the user owns this alert
    if str(alert.user_id) != str(current_user.id) and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    return alert

@router.post("/", response_model=Alert, status_code=status.HTTP_201_CREATED)
async def create_alert(
    alert_in: AlertCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create a new alert.
    """
    # Verify the cryptocurrency exists
    cryptocurrency = await crud.cryptocurrency.get(db, id=alert_in.cryptocurrency_id)
    if not cryptocurrency:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cryptocurrency not found",
        )
    
    # Create the alert
    alert = await crud.alert.create_with_owner(
        db, 
        obj_in=alert_in, 
        owner_id=current_user.id
    )
    return alert

@router.put("/{alert_id}", response_model=Alert)
async def update_alert(
    alert_id: str,
    alert_in: AlertUpdate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an alert.
    """
    alert = await crud.alert.get(db, id=alert_id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found",
        )
    
    # Ensure the user owns this alert
    if str(alert.user_id) != str(current_user.id) and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    # If updating cryptocurrency_id, verify it exists
    if alert_in.cryptocurrency_id is not None:
        cryptocurrency = await crud.cryptocurrency.get(db, id=alert_in.cryptocurrency_id)
        if not cryptocurrency:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cryptocurrency not found",
            )
    
    alert = await crud.alert.update(db, db_obj=alert, obj_in=alert_in)
    return alert

@router.delete("/{alert_id}", response_model=Alert)
async def delete_alert(
    alert_id: str,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete an alert.
    """
    alert = await crud.alert.get(db, id=alert_id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found",
        )
    
    # Ensure the user owns this alert
    if str(alert.user_id) != str(current_user.id) and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    
    alert = await crud.alert.remove(db, id=alert_id)
    return alert
