"""
Cryptocurrency related schemas.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator

class CryptocurrencyBase(BaseModel):
    """Base schema for cryptocurrency."""
    symbol: str
    name: str
    is_active: bool = True

class CryptocurrencyCreate(CryptocurrencyBase):
    """Schema for creating a new cryptocurrency."""
    pass

class CryptocurrencyUpdate(CryptocurrencyBase):
    """Schema for updating a cryptocurrency."""
    symbol: Optional[str] = None
    name: Optional[str] = None
    is_active: Optional[bool] = None

class Cryptocurrency(CryptocurrencyBase):
    """Schema for cryptocurrency response."""
    id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class PriceHistoryBase(BaseModel):
    """Base schema for price history."""
    cryptocurrency_id: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float

class PriceHistoryCreate(PriceHistoryBase):
    """Schema for creating new price history."""
    pass

class PriceHistoryUpdate(PriceHistoryBase):
    """Schema for updating price history."""
    cryptocurrency_id: Optional[str] = None
    timestamp: Optional[datetime] = None
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    volume: Optional[float] = None

class PriceHistory(PriceHistoryBase):
    """Schema for price history response."""
    id: str
    
    class Config:
        from_attributes = True

class ModelVersionBase(BaseModel):
    """Base schema for model version."""
    name: str
    version: str
    path: str
    metrics: Optional[Dict[str, Any]] = None
    is_production: bool = False

class ModelVersionCreate(ModelVersionBase):
    """Schema for creating a new model version."""
    pass

class ModelVersionUpdate(ModelVersionBase):
    """Schema for updating a model version."""
    name: Optional[str] = None
    version: Optional[str] = None
    path: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None
    is_production: Optional[bool] = None

class ModelVersion(ModelVersionBase):
    """Schema for model version response."""
    id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class PredictionBase(BaseModel):
    """Base schema for prediction."""
    cryptocurrency_id: str
    model_version_id: str
    timestamp: datetime
    prediction_time: datetime
    horizon: str
    predicted_price: float
    confidence_upper: Optional[float] = None
    confidence_lower: Optional[float] = None
    metrics: Optional[Dict[str, Any]] = None

class PredictionCreate(PredictionBase):
    """Schema for creating a new prediction."""
    pass

class PredictionUpdate(PredictionBase):
    """Schema for updating a prediction."""
    cryptocurrency_id: Optional[str] = None
    model_version_id: Optional[str] = None
    timestamp: Optional[datetime] = None
    prediction_time: Optional[datetime] = None
    horizon: Optional[str] = None
    predicted_price: Optional[float] = None
    confidence_upper: Optional[float] = None
    confidence_lower: Optional[float] = None
    metrics: Optional[Dict[str, Any]] = None

class Prediction(PredictionBase):
    """Schema for prediction response."""
    id: str
    
    class Config:
        from_attributes = True

class AlertBase(BaseModel):
    """Base schema for alert."""
    user_id: str
    cryptocurrency_id: str
    condition_type: str
    condition_value: float
    is_active: bool = True

class AlertCreate(AlertBase):
    """Schema for creating a new alert."""
    pass

class AlertUpdate(AlertBase):
    """Schema for updating an alert."""
    user_id: Optional[str] = None
    cryptocurrency_id: Optional[str] = None
    condition_type: Optional[str] = None
    condition_value: Optional[float] = None
    is_active: Optional[bool] = None

class Alert(AlertBase):
    """Schema for alert response."""
    id: str
    last_triggered: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class AlertInDB(Alert):
    """Schema for alert in database."""
    cryptocurrency: Optional[Cryptocurrency] = None
    
    class Config:
        from_attributes = True
