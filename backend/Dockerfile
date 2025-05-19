# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN echo "Contents of requirements.txt:" && cat requirements.txt && echo ""
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the application code and scripts
COPY . .

# Make the wait_for_postgres.py script executable
RUN chmod +x wait_for_postgres.py

# Create necessary directories
RUN mkdir -p /app/models

# Add the app directory to the Python path
ENV PYTHONPATH="/app"

# Set the working directory
WORKDIR /app

# Expose the port the app runs on
EXPOSE 8000

# Copy the initialization scripts
COPY init_db.py .
COPY init_script.sh .

# Make the init script executable
RUN chmod +x /app/init_script.sh

# Command to run the application
CMD ["/app/init_script.sh"]
