"""
API package initialization.
"""
from fastapi import APIRouter

from app.api.v1 import router as api_v1_router

api_router = APIRouter()

# Include API version 1 routes
api_router.include_router(api_v1_router, prefix="/v1")
