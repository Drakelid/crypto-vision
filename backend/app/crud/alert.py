"""
CRUD operations for Alerts.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from sqlalchemy import and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.crud.base import CRUDBase
from app.models.alert import Alert
from app.schemas.alert import AlertCreate, AlertUpdate, AlertStatus

class CRUDAlert(CRUDBase[Alert, AlertCreate, AlertUpdate]):
    """CRUD operations for Alert model."""

    async def get_multi_by_user(
        self, 
        db: AsyncSession, 
        *, 
        user_id: UUID,
        skip: int = 0, 
        limit: int = 100,
        **filters: Any
    ) -> List[Alert]:
        """Get multiple alerts for a specific user with optional filtering."""
        query = select(self.model).where(self.model.user_id == user_id)
        
        # Apply additional filters
        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.where(getattr(self.model, key) == value)
                
        result = await db.execute(query.offset(skip).limit(limit))
        return result.scalars().all()
    
    async def get_active_alerts_for_user(
        self, 
        db: AsyncSession, 
        *, 
        user_id: UUID
    ) -> List[Alert]:
        """Get all active alerts for a specific user."""
        query = select(self.model).where(
            and_(
                self.model.user_id == user_id,
                self.model.status == AlertStatus.ACTIVE,
                or_(
                    self.model.expires_at.is_(None),
                    self.model.expires_at > datetime.utcnow()
                )
            )
        )
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_by_user_and_id(
        self, 
        db: AsyncSession, 
        *, 
        user_id: UUID, 
        alert_id: UUID
    ) -> Optional[Alert]:
        """Get a specific alert for a specific user."""
        query = select(self.model).where(
            and_(
                self.model.id == alert_id,
                self.model.user_id == user_id
            )
        )
        result = await db.execute(query)
        return result.scalars().first()
    
    async def update_status(
        self, 
        db: AsyncSession, 
        *, 
        db_obj: Alert, 
        status: AlertStatus,
        **kwargs: Any
    ) -> Alert:
        """Update the status of an alert."""
        update_data = {"status": status, **kwargs}
        return await self.update(db, db_obj=db_obj, obj_in=update_data)
    
    async def get_alerts_for_price_check(
        self, 
        db: AsyncSession, 
        *, 
        symbol: str,
        current_price: float
    ) -> List[Alert]:
        """Get all active alerts that should be triggered for the given symbol and price."""
        query = select(self.model).where(
            and_(
                self.model.symbol == symbol.upper(),
                self.model.status == AlertStatus.ACTIVE,
                or_(
                    self.model.expires_at.is_(None),
                    self.model.expires_at > datetime.utcnow()
                ),
                or_(
                    and_(self.model.condition == ">", current_price > self.model.target_price),
                    and_(self.model.condition == ">=", current_price >= self.model.target_price),
                    and_(self.model.condition == "<", current_price < self.model.target_price),
                    and_(self.model.condition == "<=", current_price <= self.model.target_price),
                    and_(self.model.condition == "==", current_price == self.model.target_price),
                    and_(self.model.condition == "!=", current_price != self.model.target_price)
                )
            )
        )
        result = await db.execute(query)
        return result.scalars().all()

# Create a singleton instance
alert = CRUDAlert(Alert)
