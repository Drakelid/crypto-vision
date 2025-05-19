"""
API v1 package initialization.
"""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    users,
    crypto,
    predictions,
    alerts,
    models,
)

router = APIRouter()

# Include all endpoint routers
router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
router.include_router(users.router, prefix="/users", tags=["Users"])
router.include_router(crypto.router, prefix="/crypto", tags=["Cryptocurrency"])
router.include_router(predictions.router, prefix="/predictions", tags=["Predictions"])
router.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])
router.include_router(models.router, prefix="/models", tags=["Models"])
