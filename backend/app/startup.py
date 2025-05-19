"""
Application startup tasks.
"""
import logging
from typing import Callable

from fastapi import FastAPI
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.init_db import init_db
from app.db.session import SessionLocal

logger = logging.getLogger(__name__)

def create_start_app_handler(app: FastAPI) -> Callable:
    """
    Actions to run on application startup.
    """
    async def start_app() -> None:
        logger.info("Running application startup tasks...")
        
        # Initialize database
        if settings.ENVIRONMENT != "testing":
            logger.info("Initializing database...")
            db = SessionLocal()
            try:
                init_db()
            except Exception as e:
                logger.error(f"Error initializing database: {e}")
                raise
            finally:
                db.close()
        
        logger.info("Application startup tasks completed")
    
    return start_app

def create_stop_app_handler(app: FastAPI) -> Callable:
    """
    Actions to run on application shutdown.
    """
    async def stop_app() -> None:
        logger.info("Running application shutdown tasks...")
        # Add any cleanup tasks here
        logger.info("Application shutdown tasks completed")
    
    return stop_app
