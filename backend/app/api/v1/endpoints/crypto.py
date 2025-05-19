"""
Cryptocurrency related API endpoints.
"""
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models
from app.api import deps
from app.schemas.crypto import (
    Cryptocurrency,
    CryptocurrencyCreate,
    CryptocurrencyUpdate,
    PriceHistory,
    PriceHistoryCreate,
    Prediction,
    PredictionCreate,
    ModelVersion,
    ModelVersionCreate,
)
from app.schemas.user import User

router = APIRouter()

# Cryptocurrency endpoints
@router.get("/cryptocurrencies/", response_model=List[Cryptocurrency])
async def read_cryptocurrencies(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve all cryptocurrencies.
    """
    cryptocurrencies = await crud.cryptocurrency.get_multi(db, skip=skip, limit=limit)
    return cryptocurrencies

@router.get("/cryptocurrencies/active/", response_model=List[Cryptocurrency])
async def read_active_cryptocurrencies(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve all active cryptocurrencies.
    """
    cryptocurrencies = await crud.cryptocurrency.get_multi_active(
        db, skip=skip, limit=limit
    )
    return cryptocurrencies

@router.get("/cryptocurrencies/{cryptocurrency_id}", response_model=Cryptocurrency)
async def read_cryptocurrency(
    cryptocurrency_id: str,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get a specific cryptocurrency by ID.
    """
    cryptocurrency = await crud.cryptocurrency.get(db, id=cryptocurrency_id)
    if not cryptocurrency:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cryptocurrency not found",
        )
    return cryptocurrency

@router.post("/cryptocurrencies/", response_model=Cryptocurrency, status_code=status.HTTP_201_CREATED)
async def create_cryptocurrency(
    cryptocurrency_in: CryptocurrencyCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create a new cryptocurrency (admin only).
    """
    # Check if cryptocurrency with this symbol already exists
    existing = await crud.cryptocurrency.get_by_symbol(
        db, symbol=cryptocurrency_in.symbol
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A cryptocurrency with this symbol already exists",
        )
    
    cryptocurrency = await crud.cryptocurrency.create(db, obj_in=cryptocurrency_in)
    return cryptocurrency

# Price history endpoints
@router.get("/price-history/", response_model=List[PriceHistory])
async def read_price_history(
    cryptocurrency_id: str,
    start_date: datetime,
    end_date: Optional[datetime] = None,
    interval: str = "1h",
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get historical price data for a cryptocurrency.
    
    - **cryptocurrency_id**: ID of the cryptocurrency
    - **start_date**: Start date for the historical data
    - **end_date**: End date for the historical data (defaults to now)
    - **interval**: Time interval (1m, 5m, 15m, 1h, 4h, 1d, 1w)
    """
    # Validate interval
    valid_intervals = ["1m", "5m", "15m", "1h", "4h", "1d", "1w"]
    if interval not in valid_intervals:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid interval. Must be one of: {', '.join(valid_intervals)}",
        )
    
    # Limit the date range to prevent excessive data retrieval
    max_days = 365  # Maximum 1 year of data
    if (end_date or datetime.utcnow()) - start_date > timedelta(days=max_days):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Date range cannot exceed {max_days} days",
        )
    
    history = await crud.price_history.get_historical_data(
        db,
        cryptocurrency_id=cryptocurrency_id,
        start_date=start_date,
        end_date=end_date,
        interval=interval,
    )
    
    return history

# Prediction endpoints
@router.get("/predictions/latest/", response_model=Optional[Prediction])
async def read_latest_prediction(
    cryptocurrency_id: str,
    horizon: str = "24h",
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get the latest prediction for a cryptocurrency and time horizon.
    
    - **cryptocurrency_id**: ID of the cryptocurrency
    - **horizon**: Prediction horizon (e.g., 1h, 24h, 7d)
    """
    prediction = await crud.prediction.get_latest(
        db, 
        cryptocurrency_id=cryptocurrency_id,
        horizon=horizon,
    )
    return prediction

@router.get("/predictions/", response_model=List[Prediction])
async def read_predictions(
    cryptocurrency_id: str,
    start_date: datetime,
    end_date: Optional[datetime] = None,
    horizon: Optional[str] = None,
    model_version_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get predictions for a cryptocurrency within a date range.
    
    - **cryptocurrency_id**: ID of the cryptocurrency
    - **start_date**: Start date for predictions
    - **end_date**: End date for predictions (defaults to now)
    - **horizon**: Optional prediction horizon to filter by
    - **model_version_id**: Optional model version ID to filter by
    """
    predictions = await crud.prediction.get_predictions_for_period(
        db,
        cryptocurrency_id=cryptocurrency_id,
        start_date=start_date,
        end_date=end_date,
        horizon=horizon,
        model_version_id=model_version_id,
    )
    
    return predictions[skip:skip + limit] if limit > 0 else predictions

# Model version endpoints
@router.get("/models/", response_model=List[ModelVersion])
async def read_model_versions(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get all model versions.
    """
    models = await crud.model_version.get_multi(db, skip=skip, limit=limit)
    return models

@router.get("/models/{model_name}/production", response_model=Optional[ModelVersion])
async def get_production_model(
    model_name: str,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get the production version of a model by name.
    """
    model = await crud.model_version.get_production_version(db, name=model_name)
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No production version found for model: {model_name}",
        )
    return model

@router.post("/models/", response_model=ModelVersion, status_code=status.HTTP_201_CREATED)
async def create_model_version(
    model_in: ModelVersionCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create a new model version (admin only).
    """
    # Check if model version with this name and version already exists
    existing = await crud.model_version.get_by_name_version(
        db, name=model_in.name, version=model_in.version
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A model version with this name and version already exists",
        )
    
    # If this is set as production, unset any existing production version
    if model_in.is_production:
        await crud.model_version.set_production_version(
            db, model_version_id=existing.id if existing else ""
        )
    
    model = await crud.model_version.create(db, obj_in=model_in)
    return model

@router.put("/models/{model_version_id}/set-production", response_model=ModelVersion)
async def set_production_model(
    model_version_id: str,
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Set a model version as the production version (admin only).
    """
    model = await crud.model_version.set_production_version(
        db, model_version_id=model_version_id
    )
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model version not found",
        )
    return model
