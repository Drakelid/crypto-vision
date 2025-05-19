"""
Models package for the application.

This module imports all SQLAlchemy models and makes them available at the package level.
It handles circular imports by using string references in relationships.
"""
# Import models in an order that avoids circular imports

# 1. Import base models that don't have relationships first
from app.models.models import (
    Role,
    Cryptocurrency,
    ModelVersion,
)

# 2. Import models with relationships
from app.models.models import (
    UserRole,
    PriceHistory,
    Prediction,
)

# 3. Import models that were moved to separate files
from app.models.user import User
from app.models.alert import Alert

# Make models available at the package level
__all__ = [
    # User-related models
    'User',
    'Role',
    'UserRole',
    
    # Cryptocurrency and market data
    'Cryptocurrency',
    'PriceHistory',
    
    # ML models and predictions
    'ModelVersion',
    'Prediction',
    
    # Alerts
    'Alert',
]
