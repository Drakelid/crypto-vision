"""
Price history related Pydantic models.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator

from app.schemas.base import BaseSchema


class PriceHistoryBase(BaseModel):
    """Base price history schema with shared fields."""
    cryptocurrency_id: UUID = Field(..., description="ID of the cryptocurrency")
    timestamp: datetime = Field(..., description="Timestamp of the price data")
    open: float = Field(..., description="Opening price")
    high: float = Field(..., description="Highest price")
    low: float = Field(..., description="Lowest price")
    close: float = Field(..., description="Closing price")
    volume: float = Field(..., description="Trading volume")


class PriceHistoryCreate(PriceHistoryBase):
    """Schema for creating new price history data."""
    pass


class PriceHistoryUpdate(BaseModel):
    """Schema for updating existing price history data."""
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    volume: Optional[float] = None


class PriceHistoryInDBBase(PriceHistoryBase, BaseSchema):
    """Base schema for price history in database."""
    id: UUID

    class Config:
        orm_mode = True


class PriceHistory(PriceHistoryInDBBase):
    """Price history schema for API responses."""
    pass


class PriceHistoryWithCrypto(PriceHistory):
    """Price history schema with cryptocurrency details."""
    symbol: Optional[str] = None
    name: Optional[str] = None

    @validator('symbol', pre=True)
    def set_crypto_symbol(cls, v, values):
        if v is not None:
            return v
        if hasattr(values, 'cryptocurrency') and values.cryptocurrency:
            return values.cryptocurrency.symbol
        return None

    @validator('name', pre=True)
    def set_crypto_name(cls, v, values):
        if v is not None:
            return v
        if hasattr(values, 'cryptocurrency') and values.cryptocurrency:
            return values.cryptocurrency.name
        return None
