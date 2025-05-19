"""
API package initialization.
"""
from fastapi import APIRouter

from app.api.v1 import api as api_v1

api_router = APIRouter()

# Include API version 1 routes
api_router.include_router(api_v1.router, prefix="/v1")
