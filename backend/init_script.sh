#!/bin/bash

# Wait for PostgreSQL to be ready
until PGPASSWORD=postgres psql -h db -U postgres -d cryptovision -c "SELECT 1" > /dev/null 2>&1; do
  echo "Waiting for PostgreSQL to be ready..."
  sleep 2
done

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Initialize the database
echo "Initializing database..."
python init_db.py

# Start the application
echo "Starting application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
