"""
Script to manually initialize the database and create tables.
"""
import os
import sys
import time
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

# Add the app directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.db.base_class import Base
from app.models import *  # Import all models to ensure they are registered with SQLAlchemy

def wait_for_db(engine, max_retries=30, delay=2):
    """Wait for the database to be available."""
    retry_count = 0
    while retry_count < max_retries:
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                print("Database is available.")
                return True
        except OperationalError as e:
            print(f"Database not available, retrying in {delay} seconds... (Attempt {retry_count + 1}/{max_retries})")
            retry_count += 1
            time.sleep(delay)
    print("Failed to connect to the database after multiple retries.")
    return False

def create_tables():
    """Create database tables directly."""
    print("Initializing database...")
    print(f"Database URL: {settings.SQLALCHEMY_DATABASE_URI}")
    
    # Create engine with explicit connect_args
    engine = create_engine(
        settings.SQLALCHEMY_DATABASE_URI,
        pool_pre_ping=True,
        pool_recycle=300,
        connect_args={"options": "-c timezone=utc"}
    )
    
    # Wait for the database to be available
    if not wait_for_db(engine):
        print("Error: Could not connect to the database.")
        sys.exit(1)
    
    print("Creating database tables...")
    
    # Create all tables in a transaction
    with engine.begin() as connection:
        try:
            # Drop all tables first to start fresh
            print("Dropping existing tables...")
            Base.metadata.drop_all(bind=connection)
            
            # Create all tables
            print("Creating tables...")
            Base.metadata.create_all(bind=connection)
            
            print("Database tables created successfully.")
            
        except Exception as e:
            print(f"Error creating tables: {e}")
            import traceback
            traceback.print_exc()
            raise

def main():
    """Main function to set up the database."""
    print("Starting database initialization...")
    print(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    
    try:
        create_tables()
        print("Database setup complete.")
    except Exception as e:
        print(f"Error setting up database: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
