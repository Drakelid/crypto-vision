"""
Script to initialize the database and create tables.
"""
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the app directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.db.base_class import Base
from app.models import *  # Import all models to ensure they are registered with SQLAlchemy

def create_tables():
    """Create database tables directly."""
    print("Creating database tables...")
    
    # Create engine
    engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    print("Database tables created successfully.")

def main():
    """Main function to set up the database."""
    try:
        create_tables()
        print("Database setup complete.")
    except Exception as e:
        print(f"Error setting up database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
