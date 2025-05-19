"""
CRUD operations for cryptocurrency data.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union

import pandas as pd
from sqlalchemy import and_, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import (
    Cryptocurrency, 
    PriceHistory, 
    Prediction, 
    ModelVersion,
    Alert
)
from app.schemas.crypto import (
    CryptocurrencyCreate, 
    CryptocurrencyUpdate,
    PriceHistoryCreate,
    PriceHistoryUpdate,
    PredictionCreate,
    PredictionUpdate,
    ModelVersionCreate,
    ModelVersionUpdate,
    AlertCreate,
    AlertUpdate
)

class CRUDCryptocurrency(CRUDBase[Cryptocurrency, CryptocurrencyCreate, CryptocurrencyUpdate]):
    """CRUD operations for Cryptocurrency model."""
    
    async def get_by_symbol(self, db: AsyncSession, *, symbol: str) -> Optional[Cryptocurrency]:
        """Get a cryptocurrency by its symbol."""
        result = await db.execute(
            select(Cryptocurrency).where(Cryptocurrency.symbol == symbol)
        )
        return result.scalars().first()
    
    async def get_multi_active(
        self, 
        db: AsyncSession, 
        *, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Cryptocurrency]:
        """Get all active cryptocurrencies."""
        result = await db.execute(
            select(Cryptocurrency)
            .where(Cryptocurrency.is_active == True)
            .offset(skip)
            .limit(limit)
            .order_by(Cryptocurrency.symbol)
        )
        return result.scalars().all()

class CRUDPriceHistory(CRUDBase[PriceHistory, PriceHistoryCreate, PriceHistoryUpdate]):
    """CRUD operations for PriceHistory model."""
    
    async def get_latest(
        self, 
        db: AsyncSession, 
        *, 
        cryptocurrency_id: str,
        limit: int = 1
    ) -> Optional[PriceHistory]:
        """Get the latest price history for a cryptocurrency."""
        result = await db.execute(
            select(PriceHistory)
            .where(PriceHistory.cryptocurrency_id == cryptocurrency_id)
            .order_by(PriceHistory.timestamp.desc())
            .limit(limit)
        )
        return result.scalars().first()
    
    async def get_historical_data(
        self,
        db: AsyncSession,
        *,
        cryptocurrency_id: str,
        start_date: datetime,
        end_date: Optional[datetime] = None,
        interval: str = "1h"
    ) -> List[PriceHistory]:
        """
        Get historical price data for a cryptocurrency within a date range.
        
        Args:
            db: Database session
            cryptocurrency_id: ID of the cryptocurrency
            start_date: Start date for the historical data
            end_date: End date for the historical data (defaults to now)
            interval: Time interval for the data (e.g., "1h", "1d", "1w")
            
        Returns:
            List of PriceHistory objects
        """
        if end_date is None:
            end_date = datetime.utcnow()
        
        # Convert interval to a time delta for the query
        interval_mapping = {
            "1m": "1 minute",
            "5m": "5 minutes",
            "15m": "15 minutes",
            "1h": "1 hour",
            "4h": "4 hours",
            "1d": "1 day",
            "1w": "1 week",
        }
        
        interval_sql = interval_mapping.get(interval, "1 hour")
        
        # Use time_bucket_gapfill for continuous time series with gaps
        query = text("""
            SELECT 
                time_bucket_gapfill(
                    :interval_sql, 
                    timestamp, 
                    start => :start_date, 
                    finish => :end_date
                ) AS bucket,
                first(open, timestamp) AS open,
                max(high) AS high,
                min(low) AS low,
                last(close, timestamp) AS close,
                sum(volume) AS volume
            FROM price_history
            WHERE 
                cryptocurrency_id = :cryptocurrency_id
                AND timestamp >= :start_date
                AND timestamp <= :end_date
            GROUP BY bucket
            ORDER BY bucket
        """)
        
        result = await db.execute(
            query,
            {
                "cryptocurrency_id": cryptocurrency_id,
                "start_date": start_date,
                "end_date": end_date,
                "interval_sql": interval_sql
            }
        )
        
        # Convert to PriceHistory objects
        price_history = []
        for row in result.mappings():
            price_history.append(PriceHistory(
                cryptocurrency_id=cryptocurrency_id,
                timestamp=row["bucket"],
                open=row["open"],
                high=row["high"],
                low=row["low"],
                close=row["close"],
                volume=row["volume"] or 0.0,
            ))
            
        return price_history
    
    async def get_ohlcv_dataframe(
        self,
        db: AsyncSession,
        *,
        cryptocurrency_id: str,
        start_date: datetime,
        end_date: Optional[datetime] = None,
        interval: str = "1h"
    ) -> pd.DataFrame:
        """
        Get OHLCV data as a pandas DataFrame.
        
        Args:
            db: Database session
            cryptocurrency_id: ID of the cryptocurrency
            start_date: Start date for the historical data
            end_date: End date for the historical data (defaults to now)
            interval: Time interval for the data (e.g., "1h", "1d", "1w")
            
        Returns:
            pandas.DataFrame with OHLCV data
        """
        data = await self.get_historical_data(
            db,
            cryptocurrency_id=cryptocurrency_id,
            start_date=start_date,
            end_date=end_date,
            interval=interval
        )
        
        # Convert to DataFrame
        df = pd.DataFrame([{
            'timestamp': item.timestamp,
            'open': item.open,
            'high': item.high,
            'low': item.low,
            'close': item.close,
            'volume': item.volume,
        } for item in data])
        
        if not df.empty:
            df.set_index('timestamp', inplace=True)
        
        return df

class CRUDPrediction(CRUDBase[Prediction, PredictionCreate, PredictionUpdate]):
    """CRUD operations for Prediction model."""
    
    async def get_latest(
        self, 
        db: AsyncSession, 
        *, 
        cryptocurrency_id: str,
        horizon: str,
        limit: int = 1
    ) -> Optional[Prediction]:
        """Get the latest prediction for a cryptocurrency and horizon."""
        result = await db.execute(
            select(Prediction)
            .where(
                and_(
                    Prediction.cryptocurrency_id == cryptocurrency_id,
                    Prediction.horizon == horizon
                )
            )
            .order_by(Prediction.prediction_time.desc())
            .limit(limit)
        )
        return result.scalars().first()
    
    async def get_predictions_for_period(
        self,
        db: AsyncSession,
        *,
        cryptocurrency_id: str,
        start_date: datetime,
        end_date: Optional[datetime] = None,
        horizon: Optional[str] = None,
        model_version_id: Optional[str] = None
    ) -> List[Prediction]:
        """
        Get predictions for a cryptocurrency within a date range.
        
        Args:
            db: Database session
            cryptocurrency_id: ID of the cryptocurrency
            start_date: Start date for predictions
            end_date: End date for predictions (defaults to now)
            horizon: Optional prediction horizon to filter by
            model_version_id: Optional model version ID to filter by
            
        Returns:
            List of Prediction objects
        """
        if end_date is None:
            end_date = datetime.utcnow()
        
        query = select(Prediction).where(
            and_(
                Prediction.cryptocurrency_id == cryptocurrency_id,
                Prediction.timestamp >= start_date,
                Prediction.timestamp <= end_date
            )
        )
        
        if horizon is not None:
            query = query.where(Prediction.horizon == horizon)
            
        if model_version_id is not None:
            query = query.where(Prediction.model_version_id == model_version_id)
            
        query = query.order_by(Prediction.timestamp.desc())
        
        result = await db.execute(query)
        return result.scalars().all()

class CRUDModelVersion(CRUDBase[ModelVersion, ModelVersionCreate, ModelVersionUpdate]):
    """CRUD operations for ModelVersion model."""
    
    async def get_by_name_version(
        self, 
        db: AsyncSession, 
        *, 
        name: str, 
        version: str
    ) -> Optional[ModelVersion]:
        """Get a model version by name and version."""
        result = await db.execute(
            select(ModelVersion)
            .where(
                and_(
                    ModelVersion.name == name,
                    ModelVersion.version == version
                )
            )
        )
        return result.scalars().first()
    
    async def get_production_version(
        self, 
        db: AsyncSession, 
        *, 
        name: str
    ) -> Optional[ModelVersion]:
        """Get the production version of a model by name."""
        result = await db.execute(
            select(ModelVersion)
            .where(
                and_(
                    ModelVersion.name == name,
                    ModelVersion.is_production == True
                )
            )
        )
        return result.scalars().first()
    
    async def set_production_version(
        self, 
        db: AsyncSession, 
        *, 
        model_version_id: str
    ) -> Optional[ModelVersion]:
        """Set a model version as the production version."""
        # Get the model version to be set as production
        model_version = await self.get(db, id=model_version_id)
        if not model_version:
            return None
        
        # First, unset any existing production version for this model
        await db.execute(
            update(ModelVersion)
            .where(
                and_(
                    ModelVersion.name == model_version.name,
                    ModelVersion.is_production == True
                )
            )
            .values(is_production=False)
        )
        
        # Set the new production version
        model_version.is_production = True
        db.add(model_version)
        await db.commit()
        await db.refresh(model_version)
        
        return model_version

class CRUDAlert(CRUDBase[Alert, AlertCreate, AlertUpdate]):
    """CRUD operations for Alert model."""
    
    async def get_active_alerts_for_user(
        self, 
        db: AsyncSession, 
        *, 
        user_id: str
    ) -> List[Alert]:
        """Get all active alerts for a user."""
        result = await db.execute(
            select(Alert)
            .where(
                and_(
                    Alert.user_id == user_id,
                    Alert.is_active == True
                )
            )
            .order_by(Alert.created_at.desc())
        )
        return result.scalars().all()
    
    async def get_active_alerts_for_asset(
        self, 
        db: AsyncSession, 
        *, 
        cryptocurrency_id: str
    ) -> List[Alert]:
        """Get all active alerts for a specific cryptocurrency."""
        result = await db.execute(
            select(Alert)
            .where(
                and_(
                    Alert.cryptocurrency_id == cryptocurrency_id,
                    Alert.is_active == True
                )
            )
        )
        return result.scalars().all()
    
    async def check_alert_conditions(
        self,
        db: AsyncSession,
        *,
        cryptocurrency_id: str,
        current_price: float
    ) -> List[Alert]:
        """
        Check if any alert conditions are met for a given cryptocurrency and price.
        
        Returns a list of alerts that were triggered.
        """
        alerts = await self.get_active_alerts_for_asset(db, cryptocurrency_id=cryptocurrency_id)
        triggered_alerts = []
        
        for alert in alerts:
            condition_met = False
            
            if alert.condition_type == "price_above" and current_price > alert.condition_value:
                condition_met = True
            elif alert.condition_type == "price_below" and current_price < alert.condition_value:
                condition_met = True
            # Add more condition types as needed
            
            if condition_met:
                alert.last_triggered = datetime.utcnow()
                triggered_alerts.append(alert)
        
        if triggered_alerts:
            db.add_all(triggered_alerts)
            await db.commit()
            
        return triggered_alerts

# Create singleton instances
cryptocurrency = CRUDCryptocurrency(Cryptocurrency)
price_history = CRUDPriceHistory(PriceHistory)
prediction = CRUDPrediction(Prediction)
model_version = CRUDModelVersion(ModelVersion)
alert = CRUDAlert(Alert)
