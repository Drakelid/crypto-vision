"""
Prediction related Pydantic models.
"""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator

from app.schemas.base import BaseSchema


class PredictionHorizon(str, Enum):
    """Possible prediction horizons."""
    HOUR = "1h"
    DAY = "1d"
    WEEK = "1w"
    MONTH = "1m"


class PredictionBase(BaseModel):
    """Base prediction schema with shared fields."""
    cryptocurrency_id: UUID = Field(..., description="ID of the cryptocurrency")
    model_version_id: UUID = Field(..., description="ID of the model version used for prediction")
    timestamp: datetime = Field(..., description="When the prediction was made")
    prediction_time: datetime = Field(..., description="The time the prediction is for")
    horizon: PredictionHorizon = Field(..., description="Prediction horizon")
    predicted_price: float = Field(..., description="Predicted price")
    confidence_upper: Optional[float] = Field(None, description="Upper bound of the confidence interval")
    confidence_lower: Optional[float] = Field(None, description="Lower bound of the confidence interval")
    metrics: Optional[Dict[str, Any]] = Field(None, description="Additional prediction metrics")


class PredictionCreate(PredictionBase):
    """Schema for creating a new prediction."""
    pass


class PredictionUpdate(BaseModel):
    """Schema for updating an existing prediction."""
    predicted_price: Optional[float] = None
    confidence_upper: Optional[float] = None
    confidence_lower: Optional[float] = None
    metrics: Optional[Dict[str, Any]] = None


class PredictionInDBBase(PredictionBase, BaseSchema):
    """Base schema for prediction in database."""
    id: UUID

    class Config:
        orm_mode = True


class Prediction(PredictionInDBBase):
    """Prediction schema for API responses."""
    pass


class PredictionWithCrypto(Prediction):
    """Prediction schema with cryptocurrency details."""
    cryptocurrency_symbol: Optional[str] = None
    cryptocurrency_name: Optional[str] = None

    @validator('cryptocurrency_symbol', pre=True)
    def set_crypto_symbol(cls, v, values):
        if v is not None:
            return v
        if hasattr(values, 'cryptocurrency') and values.cryptocurrency:
            return values.cryptocurrency.symbol
        return None

    @validator('cryptocurrency_name', pre=True)
    def set_crypto_name(cls, v, values):
        if v is not None:
            return v
        if hasattr(values, 'cryptocurrency') and values.cryptocurrency:
            return values.cryptocurrency.name
        return None
