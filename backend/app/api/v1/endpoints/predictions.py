from fastapi import APIRouter, Depends, HTTPException
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from pydantic import BaseModel

from app import crud
from app.api import deps
from app.schemas.prediction import PredictionCreate

router = APIRouter()

class PredictionResponse(BaseModel):
    symbol: str
    predicted_price: float
    prediction_time: datetime
    model_version: str

@router.post("/", response_model=PredictionResponse)
async def make_prediction(
    *,
    db: AsyncSession = Depends(deps.get_db),
    symbol: str,
) -> Any:
    """
    Make a new price prediction for a cryptocurrency.
    """
    horizon_hours = 24  # Using a fixed 24-hour horizon for now
    prediction_result = await crud.prediction.predict(db=db, symbol=symbol)

    if not prediction_result:
        raise HTTPException(
            status_code=404,
            detail=f"Could not make prediction for symbol '{symbol}'. "
                   f"Check if the symbol is correct and if there is a production model available."
        )

    predicted_price = prediction_result["predicted_price"]
    model_version = prediction_result["model_version"]
    cryptocurrency = prediction_result["cryptocurrency"]

    # Create the prediction record in the database
    prediction_in = PredictionCreate(
        cryptocurrency_id=cryptocurrency.id,
        model_version_id=model_version.id,
        timestamp=datetime.utcnow(),
        prediction_time=datetime.utcnow() + timedelta(hours=horizon_hours),
        horizon="1d",  # Corresponds to 24h
        predicted_price=predicted_price,
        confidence_upper=None,
        confidence_lower=None,
    )

    await crud.prediction.create(db=db, obj_in=prediction_in)

    return PredictionResponse(
        symbol=cryptocurrency.symbol,
        predicted_price=predicted_price,
        prediction_time=prediction_in.prediction_time,
        model_version=f"{model_version.name} v{model_version.version}"
    )