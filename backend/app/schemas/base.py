"""
Base schemas shared across the application.
"""
from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union
from uuid import UUID

from pydantic import BaseModel, Field
from pydantic.generics import GenericModel

# Create a generic type variable for paginated responses
T = TypeVar('T')

class BaseSchema(BaseModel):
    """Base schema that includes common fields for all schemas."""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }

class PaginatedResponse(GenericModel, Generic[T]):
    """Generic paginated response schema."""
    items: List[T] = Field(..., description="List of items in the current page")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    pages: int = Field(..., description="Total number of pages")
    size: int = Field(..., description="Number of items per page")

class Message(BaseModel):
    """Generic message response schema."""
    message: str = Field(..., description="Response message")
    
class ErrorResponse(BaseModel):
    """Error response schema."""
    detail: Union[str, Dict[str, Any]] = Field(..., description="Error details")
