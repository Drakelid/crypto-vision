"""
Cryptocurrency related Pydantic models.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator

from app.schemas.base import BaseSchema


class CryptocurrencyBase(BaseModel):
    """Base cryptocurrency schema with shared fields."""
    symbol: str = Field(..., description="Cryptocurrency symbol (e.g., BTC, ETH)")
    name: str = Field(..., description="Full name of the cryptocurrency")
    is_active: bool = Field(True, description="Whether the cryptocurrency is active")


class CryptocurrencyCreate(CryptocurrencyBase):
    """Schema for creating a new cryptocurrency."""
    pass


class CryptocurrencyUpdate(BaseModel):
    """Schema for updating an existing cryptocurrency."""
    name: Optional[str] = None
    is_active: Optional[bool] = None


class CryptocurrencyInDBBase(CryptocurrencyBase, BaseSchema):
    """Base schema for cryptocurrency in database."""
    id: UUID
    created_at: datetime

    class Config:
        orm_mode = True


class Cryptocurrency(CryptocurrencyInDBBase):
    """Cryptocurrency schema for API responses."""
    pass


class CryptocurrencyWithMetrics(CryptocurrencyInDBBase):
    """Cryptocurrency schema with additional metrics."""
    current_price: Optional[float] = None
    price_change_24h: Optional[float] = None
    price_change_percentage_24h: Optional[float] = None
    market_cap: Optional[float] = None
    volume_24h: Optional[float] = None
    last_updated: Optional[datetime] = None

    @validator('current_price', pre=True)
    def set_current_price(cls, v, values):
        if v is not None:
            return v
        if hasattr(values, 'price_history') and values.price_history:
            return values.price_history[-1].close if values.price_history else None
        return None
