"""
API router for version 1 of the API.
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, crypto, models, alerts

api_router = APIRouter()

# Include routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(crypto.router, prefix="/crypto", tags=["Cryptocurrency"])
api_router.include_router(models.router, prefix="/models", tags=["Models"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])
