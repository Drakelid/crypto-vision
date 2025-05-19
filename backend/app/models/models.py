"""
Database models for the application.

Note: Some models have been moved to separate files to avoid circular imports.
- User model is in app/models/user.py
- Alert model is in app/models/alert.py
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, JSON, event, DDL, Text, PrimaryKeyConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.db.session import Base
from app.core.config import settings

def make_timescale_hypertable(table_name: str, time_column: str, 
                            partitioning_columns: Optional[List[str]] = None,
                            chunk_time_interval: str = '7 days',
                            if_not_exists: bool = True) -> DDL:
    """
    Create a TimescaleDB hypertable.
    
    Args:
        table_name: Name of the table to convert to a hypertable
        time_column: Name of the time column
        partitioning_columns: List of column names to partition by
        chunk_time_interval: Time interval for chunking
        if_not_exists: Whether to add IF NOT EXISTS to the command
    """
    # For now, let's simplify and not use partitioning columns
    # This is a temporary fix to get things working
    sql = f"""
    SELECT create_hypertable(
        '{table_name}',
        '{time_column}',
        if_not_exists => {str(if_not_exists).lower()},
        chunk_time_interval => INTERVAL '{chunk_time_interval}'
    );
    """
    
    return DDL(sql)

def add_compression_policy(table_name: str, segment_by: str, order_by: str, 
                          chunk_time_interval: str = '7 days') -> Optional[DDL]:
    """
    Add compression policy to a TimescaleDB hypertable.
    
    Args:
        table_name: Name of the table to compress
        segment_by: Column(s) to segment by for compression
        order_by: Column(s) to order by for compression
        chunk_time_interval: Time interval for compression chunks
        
    Returns:
        DDL object with the SQL commands or None if compression is not enabled
    """
    if not settings.ENABLE_TIMESCALEDB or not getattr(settings, 'ENABLE_TIMESCALEDB_COMPRESSION', False):
        return None
        
    try:
        # First, enable compression on the table
        enable_compression_sql = f"""
        ALTER TABLE {table_name} SET (
            timescaledb.compress,
            timescaledb.compress_segmentby = '{segment_by}',
            timescaledb.compress_orderby = '{order_by}',
            timescaledb.compress_chunk_time_interval = '{chunk_time_interval}'
        );
        """
        
        # Then add the compression policy
        add_policy_sql = f"""
        SELECT add_compression_policy(
            '{table_name}',
            compress_after => INTERVAL '{chunk_time_interval}'
        );
        """
        
        # Return a DDL that combines both commands
        return DDL(enable_compression_sql + "\n" + add_policy_sql)
    except Exception as e:
        import logging
        logging.error(f"Error creating compression policy for {table_name}: {e}")
        return None

# User model has been moved to app/models/user.py

class Role(Base):
    __tablename__ = "roles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    
    # Relationships - Using string references to avoid circular imports
    users = relationship("UserRole", back_populates="role", lazy="joined")

class UserRole(Base):
    __tablename__ = "user_roles"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"), primary_key=True)
    
    # Relationships - Using string references to avoid circular imports
    user = relationship("User", back_populates="roles", lazy="joined")
    role = relationship("Role", back_populates="users", lazy="joined")

class Cryptocurrency(Base):
    __tablename__ = "cryptocurrencies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    symbol = Column(String, unique=True, index=True, nullable=False)  # e.g., "BTC/USDT"
    name = Column(String, nullable=False)  # e.g., "Bitcoin"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    price_history = relationship("PriceHistory", back_populates="cryptocurrency")
    predictions = relationship("Prediction", back_populates="cryptocurrency")

class PriceHistory(Base):
    __tablename__ = "price_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    cryptocurrency_id = Column(UUID(as_uuid=True), ForeignKey("cryptocurrencies.id"), primary_key=True)
    timestamp = Column(DateTime, nullable=False, primary_key=True)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    
    # Relationships
    cryptocurrency = relationship("Cryptocurrency", back_populates="price_history")
    
    # Table arguments
    __table_args__ = (
        # Create a composite primary key with cryptocurrency_id and timestamp
        # This is required for TimescaleDB hypertables
        PrimaryKeyConstraint('id', 'cryptocurrency_id', 'timestamp'),
        {}
    )

# Event listener for after table creation
@event.listens_for(PriceHistory.__table__, 'after_create')
def create_price_history_hypertable(target, connection, **kw):
    """Create a hypertable for price history after table creation."""
    if settings.ENABLE_TIMESCALEDB:
        try:
            # Create the hypertable
            ddl = make_timescale_hypertable(
                table_name='price_history',
                time_column='timestamp',
                partitioning_columns=['cryptocurrency_id'],
                chunk_time_interval='7 days',
                if_not_exists=True
            )
            connection.execute(ddl)
            
            # Add compression policy if compression is enabled
            if settings.ENABLE_TIMESCALEDB_COMPRESSION:
                compression_ddl = add_compression_policy(
                    table_name='price_history',
                    segment_by='cryptocurrency_id',
                    order_by='timestamp DESC',
                    chunk_time_interval='7 days'
                )
                if compression_ddl is not None:
                    connection.execute(compression_ddl)
        except Exception as e:
            import logging
            logging.error(f"Error creating TimescaleDB hypertable: {e}")
            # Continue with the application startup even if TimescaleDB setup fails

class ModelVersion(Base):
    __tablename__ = "model_versions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, nullable=False)
    version = Column(String, nullable=False)  # Semantic versioning: MAJOR.MINOR.PATCH
    path = Column(String, nullable=False)  # Path to model artifacts
    metrics = Column(JSON, nullable=True)  # Store model metrics like MAE, RMSE, etc.
    is_production = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    predictions = relationship("Prediction", back_populates="model_version")

class Prediction(Base):
    __tablename__ = "predictions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    cryptocurrency_id = Column(UUID(as_uuid=True), ForeignKey("cryptocurrencies.id"), primary_key=True)
    model_version_id = Column(UUID(as_uuid=True), ForeignKey("model_versions.id"), nullable=False)
    timestamp = Column(DateTime, nullable=False, primary_key=True)
    prediction_time = Column(DateTime, nullable=False)  # When the prediction was made
    horizon = Column(String, nullable=False)  # e.g., "1h", "24h", "7d"
    predicted_price = Column(Float, nullable=False)
    confidence_upper = Column(Float, nullable=True)
    confidence_lower = Column(Float, nullable=True)
    metrics = Column(JSON, nullable=True)  # Store prediction metrics
    
    # Relationships
    cryptocurrency = relationship("Cryptocurrency", back_populates="predictions")
    model_version = relationship("ModelVersion", back_populates="predictions")
    
    # Table arguments for TimescaleDB
    __table_args__ = (
        # Create a composite primary key with id, cryptocurrency_id, and timestamp
        PrimaryKeyConstraint('id', 'cryptocurrency_id', 'timestamp'),
        {}
    )

# Event listener for after table creation
@event.listens_for(Prediction.__table__, 'after_create')
def create_prediction_hypertable(target, connection, **kw):
    """Create a hypertable for predictions after table creation."""
    if settings.ENABLE_TIMESCALEDB:
        try:
            # Create the hypertable
            ddl = make_timescale_hypertable(
                table_name='predictions',
                time_column='timestamp',
                partitioning_columns=['cryptocurrency_id', 'horizon'],
                chunk_time_interval='7 days',
                if_not_exists=True
            )
            connection.execute(ddl)
            
            # Add compression policy if compression is enabled
            if settings.ENABLE_TIMESCALEDB_COMPRESSION:
                compression_ddl = add_compression_policy(
                    table_name='predictions',
                    segment_by='cryptocurrency_id, horizon',
                    order_by='timestamp DESC',
                    chunk_time_interval='7 days'
                )
                if compression_ddl is not None:
                    connection.execute(compression_ddl)
        except Exception as e:
            import logging
            logging.error(f"Error creating TimescaleDB hypertable for predictions: {e}")
            # Continue with the application startup even if TimescaleDB setup fails

# Alert model has been moved to app/models/alert.py
