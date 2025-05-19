#!/bin/bash

# Set Python path
export PYTHONPATH="/app"

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
until PGPASSWORD=postgres psql -h db -U postgres -d cryptovision -c "SELECT 1" > /dev/null 2>&1; do
  echo "PostgreSQL is not ready yet. Retrying in 2 seconds..."
  sleep 2
done

echo "PostgreSQL is ready!"

# Initialize the database
echo "Initializing database..."
python /app/init_db.py

# Start the application
echo "Starting application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
