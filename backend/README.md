# CryptoVision Backend

## Project Overview
CryptoVision is a web-based dashboard for predicting cryptocurrency prices using machine learning. This is the backend service built with FastAPI, PostgreSQL, and TimescaleDB.

## Features

- **User Authentication & Authorization**
  - JWT-based authentication
  - Role-based access control (Admin, Analyst, Viewer)
  - User management

- **Cryptocurrency Data**
  - Real-time and historical price data
  - Multiple cryptocurrency support
  - OHLCV data storage

- **Predictions**
  - Machine learning model integration
  - Multiple model version support
  - Prediction history and metrics

- **Alerts**
  - Price threshold alerts
  - Email notifications
  - Custom alert conditions

## Prerequisites

- Python 3.9+
- PostgreSQL 13+
- TimescaleDB extension
- Redis (for rate limiting and caching, optional)
- Python virtual environment (recommended)

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/crypto-vision.git
   cd crypto-vision/backend
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Copy the example environment file and update the values:
   ```bash
   cp .env.example .env
   ```
   Update the `.env` file with your database credentials and other settings.

5. **Initialize the database**
   ```bash
   python -m scripts.init_db
   ```

## Running the Application

### Development Mode
```bash
uvicorn app.main:app --reload
```

### Production Mode
For production, you should use a production-ready ASGI server like Uvicorn with Gunicorn:

```bash
gunicorn -k uvicorn.workers.UvicornWorker -w 4 -b 0.0.0.0:8000 app.main:app
```

## API Documentation

Once the application is running, you can access the following documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## Project Structure

```
backend/
├── app/
│   ├── api/                    # API routes
│   │   ├── v1/                 # API version 1
│   │   │   ├── endpoints/      # API endpoints
│   │   │   └── __init__.py
│   │   └── __init__.py
│   │
│   ├── core/                  # Core functionality
│   │   ├── config.py           # Configuration settings
│   │   └── security.py         # Security utilities
│   │
│   ├── crud/                 # Database CRUD operations
│   │   ├── base.py             # Base CRUD class
│   │   ├── crypto.py           # Cryptocurrency CRUD operations
│   │   └── user.py             # User CRUD operations
│   │
│   ├── db/                   # Database configuration
│   │   ├── session.py          # Database session management
│   │   └── base.py             # Base database model
│   │
│   ├── models/               # SQLAlchemy models
│   │   └── models.py
│   │
│   ├── schemas/              # Pydantic models/schemas
│   │   ├── crypto.py
│   │   ├── user.py
│   │   └── prediction.py
│   │
│   ├── static/               # Static files (CSS, JS, etc.)
│   ├── main.py               # FastAPI application
│   └── __init__.py
│
├── scripts/                 # Utility scripts
│   └── init_db.py           # Database initialization script
│
├── tests/                   # Test files
│   ├── conftest.py
│   ├── test_api/
│   └── test_crud/
│
├── .env.example             # Example environment variables
├── .gitignore
├── alembic.ini              # Database migration configuration
├── requirements.txt         # Project dependencies
└── README.md
```

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
# Application
PROJECT_NAME="CryptoVision"
ENVIRONMENT="development"
DEBUG=True
SECRET_KEY="your-secret-key-here"  # Change this in production
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=yourpassword
POSTGRES_DB=cryptovision
DATABASE_URL=postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_SERVER}/${POSTGRES_DB}

# CORS
BACKEND_CORS_ORIGINS=["*"]  # In production, specify your frontend URL

# Email (for notifications)
SMTP_TLS=True
SMTP_PORT=587
SMTP_HOST=smtp.example.com
SMTP_USER=your-email@example.com
SMTP_PASSWORD=your-email-password
EMAILS_FROM_EMAIL=no-reply@cryptovision.app
EMAILS_FROM_NAME="CryptoVision"

# Redis (for rate limiting and caching)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# API Keys (for external services)
COINGECKO_API_KEY=your-coin-gecko-api-key
ALPHA_VANTAGE_API_KEY=your-alpha-vantage-api-key
```

## Testing

To run the test suite:

```bash
pytest
```

## Deployment

### Docker

1. Build the Docker image:
   ```bash
   docker build -t cryptovision-backend .
   ```

2. Run the container:
   ```bash
   docker run -d --name cryptovision-backend -p 8000:8000 --env-file .env cryptovision-backend
   ```

### Kubernetes

Example deployment files are provided in the `k8s/` directory.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [TimescaleDB](https://www.timescale.com/)
- [Uvicorn](https://www.uvicorn.org/)
