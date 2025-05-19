"""
User model for authentication and authorization.
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import Boolean, Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class User(Base):
    """User model for authentication and authorization."""
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}  # Allow table redefinition
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    is_active = Column(Boolean(), default=True, nullable=False)
    is_superuser = Column(Boolean(), default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    alerts = relationship("Alert", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<User {self.email}>"
    
    @property
    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        return True
    
    @property
    def is_anonymous(self) -> bool:
        """Check if user is anonymous."""
        return False
    
    def get_id(self) -> str:
        """Get user ID as string."""
        return str(self.id)
