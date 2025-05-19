import sys
import os
from sqlalchemy import create_engine, text
from app.core.config import settings

def check_database_connection():
    print("Checking database connection...")
    print(f"SQLALCHEMY_DATABASE_URI: {settings.SQLALCHEMY_DATABASE_URI}")
    
    try:
        # Create a synchronous engine
        engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
        
        # Test connection
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("✅ Database connection successful!")
            
            # List all tables
            result = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            
            tables = [row[0] for row in result]
            print("\nTables in the database:")
            for table in tables:
                print(f"- {table}")
            
            if not tables:
                print("\n⚠️  No tables found in the database.")
            
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    check_database_connection()
