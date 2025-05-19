"""
Pydantic schemas for request/response models.
"""
# Base schemas
from .base import BaseSchema, PaginatedResponse, Message, ErrorResponse

# Authentication schemas
from .token import Token, TokenPayload

# User schemas
from .user import User, UserCreate, UserInDB, UserUpdate, UserInDBBase

# Cryptocurrency schemas
from .cryptocurrency import Cryptocurrency, CryptocurrencyCreate, CryptocurrencyUpdate, CryptocurrencyWithMetrics

# Price history schemas
from .price_history import PriceHistory, PriceHistoryCreate, PriceHistoryUpdate, PriceHistoryWithCrypto

# Prediction schemas
from .prediction import Prediction, PredictionCreate, PredictionUpdate, PredictionWithCrypto, PredictionHorizon

# Model version schemas
from .model_version import ModelVersion, ModelVersionCreate, ModelVersionUpdate, ModelVersionWithPredictions

# Alert schemas
from .alert import Alert, AlertCreate, AlertUpdate, AlertInDB, AlertStatus, AlertCondition

# Re-export all schemas
__all__ = [
    # Base
    'BaseSchema', 'PaginatedResponse', 'Message', 'ErrorResponse',
    
    # Authentication
    'Token', 'TokenPayload',
    
    # User
    'User', 'UserCreate', 'UserInDB', 'UserUpdate', 'UserInDBBase',
    
    # Cryptocurrency
    'Cryptocurrency', 'CryptocurrencyCreate', 'CryptocurrencyUpdate', 'CryptocurrencyWithMetrics',
    
    # Price History
    'PriceHistory', 'PriceHistoryCreate', 'PriceHistoryUpdate', 'PriceHistoryWithCrypto',
    
    # Prediction
    'Prediction', 'PredictionCreate', 'PredictionUpdate', 'PredictionWithCrypto', 'PredictionHorizon',
    
    # Model Version
    'ModelVersion', 'ModelVersionCreate', 'ModelVersionUpdate', 'ModelVersionWithPredictions',
    
    # Alert
    'Alert', 'AlertCreate', 'AlertUpdate', 'AlertInDB', 'AlertStatus', 'AlertCondition',
]
