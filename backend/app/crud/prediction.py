from typing import Any, Dict, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

import torch
import pandas as pd
import numpy as np
from app.crud.base import CRUDBase
from app.models.models import Prediction, ModelVersion, PriceHistory, Cryptocurrency
from app.schemas.prediction import PredictionCreate, PredictionUpdate


class CRUDPrediction(CRUDBase[Prediction, PredictionCreate, PredictionUpdate]):
    """CRUD for predictions."""

    async def get_production_model(self, db: AsyncSession) -> Optional[Dict[str, Any]]:
        """
        Load the production machine learning model.

        Returns a dictionary containing the model and its metadata.
        """
        result = await db.execute(
            select(ModelVersion).where(ModelVersion.is_production == True)
        )
        production_model_version = result.scalars().first()

        if not production_model_version:
            return None

        # Load the model artifacts
        # This assumes the model is a PyTorch model
        model = torch.load(production_model_version.path)
        model.eval()  # Set model to evaluation mode

        return {
            "model": model,
            "version": production_model_version
        }

    def _preprocess_data(self, data: pd.DataFrame, sequence_length: int = 60) -> Dict[str, Any]:
        """
        Preprocess the data for the model.
        - Normalize the 'close' price
        - Create sequences
        """
        close_prices = data['close'].values.astype(float)
        min_price = np.min(close_prices)
        max_price = np.max(close_prices)

        # Avoid division by zero if all prices are the same
        if max_price == min_price:
            scaled_prices = np.zeros(close_prices.shape)
        else:
            scaled_prices = (close_prices - min_price) / (max_price - min_price)

        # Create sequences
        X = []
        for i in range(len(scaled_prices) - sequence_length):
            X.append(scaled_prices[i:i + sequence_length])

        # We only need the most recent sequence for prediction
        last_sequence = np.array(X)[-1]

        return {
            "sequence": last_sequence,
            "min_price": min_price,
            "max_price": max_price
        }

    async def get_and_preprocess_data(
        self,
        db: AsyncSession,
        *,
        symbol: str,
        sequence_length: int = 60,
        limit: int = 200
    ) -> Optional[Dict[str, Any]]:
        """Fetch and preprocess data for a given symbol."""
        crypto_result = await db.execute(select(Cryptocurrency).where(Cryptocurrency.symbol == symbol))
        crypto = crypto_result.scalars().first()
        if not crypto:
            return None

        price_history_result = await db.execute(
            select(PriceHistory)
            .where(PriceHistory.cryptocurrency_id == crypto.id)
            .order_by(PriceHistory.timestamp.desc())
            .limit(limit)
        )
        price_history = price_history_result.scalars().all()

        if len(price_history) < sequence_length:
            return None

        df = pd.DataFrame([p.__dict__ for p in price_history])
        df = df.sort_values('timestamp').reset_index(drop=True)

        processed_data = self._preprocess_data(df, sequence_length)

        tensor = torch.from_numpy(processed_data["sequence"]).float().unsqueeze(0).unsqueeze(0)

        return {
            "tensor": tensor,
            "min_price": processed_data["min_price"],
            "max_price": processed_data["max_price"],
            "crypto": crypto
        }

    async def predict(self, db: AsyncSession, *, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Perform price prediction for a given symbol.
        """
        # 1. Load model
        model_data = await self.get_production_model(db)
        if not model_data:
            return None # No production model found

        # 2. Get and preprocess data
        processed_data = await self.get_and_preprocess_data(db, symbol=symbol)
        if not processed_data:
            return None # Not enough data or symbol not found

        # 3. Make prediction
        model = model_data["model"]
        input_tensor = processed_data["tensor"]

        with torch.no_grad():
            raw_prediction = model(input_tensor).item()

        # 4. Post-process (inverse transform) the prediction
        min_price = processed_data["min_price"]
        max_price = processed_data["max_price"]

        if max_price == min_price:
             predicted_price = min_price # or max_price, they are the same
        else:
            predicted_price = raw_prediction * (max_price - min_price) + min_price

        return {
            "predicted_price": predicted_price,
            "model_version": model_data["version"],
            "cryptocurrency": processed_data["crypto"]
        }


    async def get_by_symbol_and_model(
        self,
        db: AsyncSession,
        *,
        symbol: str,
        model_version_id: str
    ) -> Optional[Prediction]:
        """Get the last prediction for a symbol and model."""
        result = await db.execute(
            select(self.model)
            .join(ModelVersion)
            .where(
                self.model.cryptocurrency.has(symbol=symbol),
                self.model.model_version_id == model_version_id
            )
            .order_by(self.model.timestamp.desc())
        )
        return result.scalars().first()

prediction = CRUDPrediction(Prediction)
