"""
CRUD operations for the application.
"""
from .base import CRUDBase
from .user import user, CRUDUser
from .alert import alert, CRUDAlert

__all__ = [
    'CRUDBase',
    'user',
    'CRUDUser',
    'alert',
    'CRUDAlert',
]
