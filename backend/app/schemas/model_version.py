"""
Model version related Pydantic models.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator

from app.schemas.base import BaseSchema


class ModelVersionBase(BaseModel):
    """Base model version schema with shared fields."""
    name: str = Field(..., description="Name of the model")
    version: str = Field(..., description="Version identifier")
    path: str = Field(..., description="Path to the model file")
    metrics: Optional[Dict[str, Any]] = Field(None, description="Model performance metrics")
    is_production: bool = Field(False, description="Whether this is the production model")


class ModelVersionCreate(ModelVersionBase):
    """Schema for creating a new model version."""
    pass


class ModelVersionUpdate(BaseModel):
    """Schema for updating an existing model version."""
    is_production: Optional[bool] = None
    metrics: Optional[Dict[str, Any]] = None


class ModelVersionInDBBase(ModelVersionBase, BaseSchema):
    """Base schema for model version in database."""
    id: UUID
    created_at: datetime

    class Config:
        orm_mode = True


class ModelVersion(ModelVersionInDBBase):
    """Model version schema for API responses."""
    pass


class ModelVersionWithPredictions(ModelVersionInDBBase):
    """Model version schema with prediction count."""
    prediction_count: int = 0

    @validator('prediction_count', pre=True)
    def set_prediction_count(cls, v, values):
        if v is not None:
            return v
        if hasattr(values, 'predictions'):
            return len(values.predictions)
        return 0
