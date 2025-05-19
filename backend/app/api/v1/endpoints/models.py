"""
Model related API endpoints.
"""
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models
from app.api import deps
from app.schemas.crypto import ModelVersion, ModelVersionCreate, ModelVersionUpdate
from app.schemas.prediction import Prediction, PredictionCreate, PredictionUpdate

router = APIRouter()

# Model Version Endpoints
@router.get("/versions/", response_model=List[ModelVersion])
async def read_model_versions(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    Retrieve all model versions.
    """
    model_versions = await crud.model_version.get_multi(db, skip=skip, limit=limit)
    return model_versions

@router.get("/versions/{model_version_id}", response_model=ModelVersion)
async def read_model_version(
    model_version_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    Get a specific model version by ID.
    """
    model_version = await crud.model_version.get(db, id=model_version_id)
    if not model_version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model version not found",
        )
    return model_version

@router.post("/versions/", response_model=ModelVersion, status_code=status.HTTP_201_CREATED)
async def create_model_version(
    model_version_in: ModelVersionCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    Create a new model version (admin only).
    """
    # Check if model version with this name and version already exists
    existing = await crud.model_version.get_by_name_version(
        db, 
        name=model_version_in.name, 
        version=model_version_in.version
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A model version with this name and version already exists",
        )
    
    # If this is set as production, unset any existing production version
    if model_version_in.is_production:
        await crud.model_version.set_production_version(db, model_version_id="")
    
    model_version = await crud.model_version.create(db, obj_in=model_version_in)
    return model_version

@router.put("/versions/{model_version_id}", response_model=ModelVersion)
async def update_model_version(
    model_version_id: str,
    model_version_in: ModelVersionUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    Update a model version (admin only).
    """
    model_version = await crud.model_version.get(db, id=model_version_id)
    if not model_version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model version not found",
        )
    
    # If updating to production, unset any existing production version
    if model_version_in.is_production:
        await crud.model_version.set_production_version(db, model_version_id=model_version_id)
    
    model_version = await crud.model_version.update(
        db, 
        db_obj=model_version, 
        obj_in=model_version_in
    )
    return model_version

@router.post("/versions/{model_version_id}/set-production", response_model=ModelVersion)
async def set_production_model(
    model_version_id: str,
    current_user: models.User = Depends(deps.get_current_active_superuser),
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    Set a model version as the production version (admin only).
    """
    model_version = await crud.model_version.set_production_version(
        db, 
        model_version_id=model_version_id
    )
    if not model_version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model version not found",
        )
    return model_version

# Prediction Endpoints
@router.get("/predictions/", response_model=List[Prediction])
async def read_predictions(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    Retrieve all predictions.
    """
    predictions = await crud.prediction.get_multi(db, skip=skip, limit=limit)
    return predictions

@router.get("/predictions/{prediction_id}", response_model=Prediction)
async def read_prediction(
    prediction_id: str,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    Get a specific prediction by ID.
    """
    prediction = await crud.prediction.get(db, id=prediction_id)
    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prediction not found",
        )
    return prediction

@router.post("/predictions/", response_model=Prediction, status_code=status.HTTP_201_CREATED)
async def create_prediction(
    prediction_in: PredictionCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    Create a new prediction.
    
    Requires 'analyst' or 'admin' role.
    """
    # Check if the user has the required role
    has_analyst_role = await crud.user.has_role(db, str(current_user.id), "analyst")
    if not has_analyst_role and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Analyst or admin role required.",
        )
    
    # Verify the cryptocurrency exists
    cryptocurrency = await crud.cryptocurrency.get(db, id=prediction_in.cryptocurrency_id)
    if not cryptocurrency:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cryptocurrency not found",
        )
    
    # Verify the model version exists
    model_version = await crud.model_version.get(db, id=prediction_in.model_version_id)
    if not model_version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model version not found",
        )
    
    prediction = await crud.prediction.create(db, obj_in=prediction_in)
    return prediction

@router.put("/predictions/{prediction_id}", response_model=Prediction)
async def update_prediction(
    prediction_id: str,
    prediction_in: PredictionUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    Update a prediction.
    
    Requires 'analyst' or 'admin' role.
    """
    # Check if the user has the required role
    has_analyst_role = await crud.user.has_role(db, str(current_user.id), "analyst")
    if not has_analyst_role and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Analyst or admin role required.",
        )
    
    prediction = await crud.prediction.get(db, id=prediction_id)
    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prediction not found",
        )
    
    # Verify the cryptocurrency exists if being updated
    if prediction_in.cryptocurrency_id is not None:
        cryptocurrency = await crud.cryptocurrency.get(db, id=prediction_in.cryptocurrency_id)
        if not cryptocurrency:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cryptocurrency not found",
            )
    
    # Verify the model version exists if being updated
    if prediction_in.model_version_id is not None:
        model_version = await crud.model_version.get(db, id=prediction_in.model_version_id)
        if not model_version:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Model version not found",
            )
    
    prediction = await crud.prediction.update(
        db, 
        db_obj=prediction, 
        obj_in=prediction_in
    )
    return prediction

@router.delete("/predictions/{prediction_id}", response_model=Prediction)
async def delete_prediction(
    prediction_id: str,
    current_user: models.User = Depends(deps.get_current_active_superuser),
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    Delete a prediction (admin only).
    """
    prediction = await crud.prediction.get(db, id=prediction_id)
    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prediction not found",
        )
    
    prediction = await crud.prediction.remove(db, id=prediction_id)
    return prediction
