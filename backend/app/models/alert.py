"""
Alert model for price alerts.
"""
from datetime import datetime
from enum import Enum as EnumType
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.user import User  # noqa: F401


class AlertStatus(str, EnumType):
    """Possible status values for an alert."""
    ACTIVE = "active"
    TRIGGERED = "triggered"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class AlertCondition(str, EnumType):
    """Possible conditions for an alert."""
    GREATER_THAN = ">"
    GREATER_THAN_OR_EQUAL = ">="
    LESS_THAN = "<"
    LESS_THAN_OR_EQUAL = "<="
    EQUAL = "=="
    NOT_EQUAL = "!="


class Alert(Base):
    """Alert model for price alerts."""
    __tablename__ = "alerts"
    __table_args__ = {'extend_existing': True}  # Allow table redefinition
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    symbol = Column(String(10), nullable=False, index=True)  # e.g., BTC, ETH
    condition = Column(Enum(AlertCondition), nullable=False)
    target_price = Column(Float, nullable=False)
    status = Column(Enum(AlertStatus), default=AlertStatus.ACTIVE, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    triggered_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="alerts")
    
    def __repr__(self) -> str:
        return f"<Alert {self.name} ({self.symbol} {self.condition} {self.target_price})>"
    
    @property
    def is_expired(self) -> bool:
        """Check if the alert has expired."""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
