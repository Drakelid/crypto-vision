#!/bin/bash

# Wait for PostgreSQL to be ready
until PGPASSWORD=postgres psql -h db -U postgres -d cryptovision -c "SELECT 1" > /dev/null 2>&1; do
  echo "Waiting for PostgreSQL to be ready..."
  sleep 2
done

# Initialize Alembic
echo "Initializing Alembic..."
alembic init alembic

# Update alembic.ini with the correct database URL
sed -i "s|sqlalchemy.url = .*|sqlalchemy.url = postgresql://postgres:postgres@db:5432/cryptovision|" /app/alembic.ini

# Update env.py to use our models
echo "from app.db.base_class import Base
from app.models import *  # Import all models to ensure they are registered with SQLAlchemy
target_metadata = Base.metadata" > /app/alembic/env.py

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Initialize the database
echo "Initializing database..."
python init_db.py

# Start the application
echo "Starting application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
