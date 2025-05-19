"""
Alert related Pydantic models.
"""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator

from app.schemas.base import BaseSchema


class AlertStatus(str, Enum):
    """Possible status values for an alert."""
    ACTIVE = "active"
    TRIGGERED = "triggered"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class AlertCondition(str, Enum):
    """Possible conditions for an alert."""
    GREATER_THAN = ">"
    GREATER_THAN_OR_EQUAL = ">="
    LESS_THAN = "<"
    LESS_THAN_OR_EQUAL = "<="
    EQUAL = "=="
    NOT_EQUAL = "!="


class AlertBase(BaseModel):
    """Base alert schema with shared fields."""
    name: str = Field(..., description="Name of the alert")
    description: Optional[str] = Field(None, description="Description of the alert")
    symbol: str = Field(..., description="Cryptocurrency symbol (e.g., BTC, ETH)")
    condition: AlertCondition = Field(..., description="Condition for the alert")
    target_price: float = Field(..., description="Target price for the alert")
    is_active: bool = Field(True, description="Whether the alert is active")
    expires_at: Optional[datetime] = Field(None, description="When the alert expires")


class AlertCreate(AlertBase):
    """Schema for creating a new alert."""
    pass


class AlertUpdate(BaseModel):
    """Schema for updating an existing alert."""
    name: Optional[str] = Field(None, description="Name of the alert")
    description: Optional[str] = Field(None, description="Description of the alert")
    is_active: Optional[bool] = Field(None, description="Whether the alert is active")
    expires_at: Optional[datetime] = Field(None, description="When the alert expires")


class AlertInDBBase(AlertBase, BaseSchema):
    """Base schema for alert in database."""
    id: UUID
    user_id: UUID
    status: AlertStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class Alert(AlertInDBBase):
    """Alert schema for API responses."""
    pass


class AlertInDB(AlertInDBBase):
    """Schema for alert in database."""
    pass
