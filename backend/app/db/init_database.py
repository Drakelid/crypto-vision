"""
Initialize the database and apply migrations.
"""
import logging
import os
import sys
from typing import Optional

# Try to import Alembic, but don't fail if it's not available
try:
    from alembic import command
    from alembic.config import Config
    ALEMBIC_AVAILABLE = True
except ImportError:
    ALEMBIC_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Alembic is not available. Falling back to direct table creation.")

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.db.base_class import Base
from app.models.alert import Alert
from app.models.user import User

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migrations() -> None:
    """Run database migrations using Alembic."""
    if not ALEMBIC_AVAILABLE:
        logger.warning("Alembic is not available. Skipping migrations.")
        return
        
    try:
        logger.info("Running database migrations...")
        
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Configure Alembic
        alembic_cfg = Config(os.path.join(script_dir, "../../alembic.ini"))
        alembic_cfg.set_main_option("script_location", os.path.join(script_dir, "../alembic"))
        alembic_cfg.set_main_option("sqlalchemy.url", settings.SQLALCHEMY_DATABASE_URI)
        
        # Run migrations
        command.upgrade(alembic_cfg, "head")
        logger.info("Database migrations completed successfully")
    except Exception as e:
        logger.error(f"Error running migrations: {e}")
        raise

def create_tables() -> None:
    """Create database tables directly using SQLAlchemy."""
    logger.info("Creating database tables...")
    
    # Create engine and session
    engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise
    finally:
        engine.dispose()

def init_db() -> None:
    """Initialize the database."""
    logger.info("Initializing database...")
    
    try:
        # Try to run migrations first
        run_migrations()
    except Exception as e:
        logger.warning(f"Failed to run migrations: {e}")
        logger.info("Falling back to direct table creation...")
        create_tables()
    
    logger.info("Database initialization complete")

if __name__ == "__main__":
    init_db()
