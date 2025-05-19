#!/usr/bin/env python3
import sys
import os
import psycopg2
import time
from urllib.parse import urlparse

# Get database URL from environment variable or use default
DATABASE_URL = os.environ.get('DATABASE_URL')

if not DATABASE_URL:
    # Construct from individual environment variables
    db_params = {
        'dbname': os.environ.get('POSTGRES_DB', 'cryptovision'),
        'user': os.environ.get('POSTGRES_USER', 'postgres'),
        'password': os.environ.get('POSTGRES_PASSWORD', 'postgres'),
        'host': os.environ.get('POSTGRES_SERVER', 'db'),
        'port': os.environ.get('POSTGRES_PORT', '5432')
    }
else:
    # Parse the DATABASE_URL
    url = urlparse(DATABASE_URL)
    db_params = {
        'dbname': url.path[1:],  # Remove leading '/'
        'user': url.username,
        'password': url.password,
        'host': url.hostname,
        'port': url.port or '5432'
    }

print('Waiting for PostgreSQL to be ready...')

for i in range(30):
    try:
        conn = psycopg2.connect(
            dbname=db_params['dbname'],
            user=db_params['user'],
            password=db_params['password'],
            host=db_params['host'],
            port=db_params['port']
        )
        conn.close()
        print('PostgreSQL is available')
        sys.exit(0)
    except Exception as e:
        print(f'PostgreSQL is unavailable - {e}')
        time.sleep(1)

print('Failed to connect to PostgreSQL after 30 seconds')
sys.exit(1)
