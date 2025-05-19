"""
Main FastAPI application module.
"""
import logging
from contextlib import asynccontextmanager
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import SQLAlchemyError

from app.api import api_router
from app.core.config import settings
from app.db.session import engine, Base
from app.db.init_database import init_db
from app.startup import create_start_app_handler, create_stop_app_handler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for the FastAPI application.
    
    Handles startup and shutdown events.
    """
    logger.info("Starting up...")
    
    # Initialize database
    try:
        # Try to run migrations first
        from app.db.init_database import run_migrations
        run_migrations()
    except Exception as e:
        logger.warning(f"Failed to run migrations: {e}")
        logger.info("Falling back to direct table creation...")
        try:
            # Fall back to direct table creation
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created")
        except Exception as e:
            logger.error(f"Error creating database tables: {e}")
            raise
    
    # Initialize application data
    await create_start_app_handler(app)()
    
    yield
    
    # Clean up resources
    logger.info("Shutting down...")
    await create_stop_app_handler(app)()
    await engine.dispose()
    logger.info("Database connection closed")

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="CryptoVision Dashboard API - Real-time cryptocurrency price predictions and analytics",
    version="1.0.0",
    docs_url=None,  # Disable default docs to use custom Swagger UI
    redoc_url=None,  # Disable default ReDoc
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# Set up CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include API routers
app.include_router(api_router, prefix=settings.API_V1_STR)

# Health check endpoint
@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint.
    
    Returns:
        Dict[str, str]: Status message
    """
    return {"status": "ok"}

# Custom exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """
    Handle HTTP exceptions.
    """
    return {
        "detail": exc.detail,
        "status_code": exc.status_code,
    }

@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request, exc):
    """
    Handle SQLAlchemy exceptions.
    """
    logger.error(f"Database error: {exc}")
    return {
        "detail": "Database error occurred",
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
    }

# Custom Swagger UI
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """
    Custom Swagger UI HTML.
    """
    return get_swagger_ui_html(
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        title=f"{settings.PROJECT_NAME} - Swagger UI",
        oauth2_redirect_url=None,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )

# Custom OpenAPI schema
def custom_openapi():
    """
    Generate custom OpenAPI schema.
    """
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=settings.PROJECT_NAME,
        version="1.0.0",
        description="CryptoVision Dashboard API - Real-time cryptocurrency price predictions and analytics",
        routes=app.routes,
    )
    
    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "Enter: 'Bearer &lt;JWT_TOKEN&gt;'\n\nExample: 'Bearer abcde12345'"
        }
    }
    
    # Add security to all endpoints by default
    for path in openapi_schema["paths"].values():
        for method in path.values():
            # Skip public endpoints
            if path not in ["/health", "/api/v1/auth/login/access-token", "/api/v1/auth/refresh-token"]:
                method["security"] = [{"OAuth2PasswordBearer": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

# Set the custom OpenAPI schema
app.openapi = custom_openapi

# Mount static files for Swagger UI
app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info" if settings.DEBUG else "warning",
    )
