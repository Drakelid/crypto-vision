# CryptoVision

A web-based dashboard for predicting cryptocurrency prices using machine learning.

## Prerequisites

- Docker (Docker Desktop for Windows/Mac or Docker Engine for Linux)
- Docker Compose (usually comes with Docker Desktop)

## Getting Started

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/crypto-vision.git
   cd crypto-vision
   ```

2. **Build and start the services**
   ```bash
   docker-compose up --build
   ```

   This will:
   - Build the FastAPI application container
   - Start PostgreSQL with TimescaleDB extension
   - Start Redis for caching and rate limiting
   - Run database migrations
   - Start the FastAPI development server

3. **Access the application**
   - API Documentation (Swagger UI): http://localhost:8000/docs
   - ReDoc Documentation: http://localhost:8000/redoc
   - FastAPI Application: http://localhost:8000

## Services

- **Backend**: FastAPI application running on port 8000
- **Database**: PostgreSQL with TimescaleDB extension
- **Cache**: Redis for rate limiting and caching

## Development

### Running Tests

```bash
docker-compose run --rm backend pytest
```

### Database Migrations

To create a new database migration:

```bash
docker-compose run --rm backend alembic revision --autogenerate -m "Your migration message"
```

To apply migrations:

```bash
docker-compose run --rm backend alembic upgrade head
```

### Environment Variables

Copy the example environment file and update the values:

```bash
cp backend/.env.example backend/.env
```

Update the `.env` file with your configuration.

## Production Deployment

For production, you should:

1. Set `ENVIRONMENT=production` in the `.env` file
2. Set `DEBUG=False` in the `.env` file
3. Update the `SECRET_KEY` with a strong secret
4. Configure proper CORS settings in `BACKEND_CORS_ORIGINS`
5. Set up proper database credentials
6. Configure a reverse proxy (Nginx, Traefik, etc.) with HTTPS

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
