"""
Initialize the database with sample data.
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.crud import user as crud_user, cryptocurrency as crud_crypto
from app.db.session import SessionLocal, engine, Base
from app.models import Role, User, Cryptocurrency, PriceHistory, ModelVersion
from app.schemas.user import UserCreate
from app.schemas.crypto import CryptocurrencyCreate, ModelVersionCreate

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sample data
SAMPLE_CRYPTOCURRENCIES = [
    {"symbol": "BTC/USDT", "name": "Bitcoin"},
    {"symbol": "ETH/USDT", "name": "Ethereum"},
    {"symbol": "BNB/USDT", "name": "Binance Coin"},
    {"symbol": "SOL/USDT", "name": "Solana"},
    {"symbol": "XRP/USDT", "name": "Ripple"},
    {"symbol": "ADA/USDT", "name": "Cardano"},
    {"symbol": "DOT/USDT", "name": "Polkadot"},
]

SAMPLE_ROLES = [
    {"name": "admin", "description": "Administrator with full access"},
    {"name": "analyst", "description": "Can create and update predictions"},
    {"name": "viewer", "description": "Can view data but not modify"},
]

SAMPLE_USERS = [
    {
        "email": "admin@cryptovision.app",
        "password": "Admin@123",
        "full_name": "Admin User",
        "is_superuser": True,
        "roles": ["admin"],
    },
    {
        "email": "analyst@cryptovision.app",
        "password": "Analyst@123",
        "full_name": "Analyst User",
        "is_superuser": False,
        "roles": ["analyst", "viewer"],
    },
    {
        "email": "user@cryptovision.app",
        "password": "User@123",
        "full_name": "Regular User",
        "is_superuser": False,
        "roles": ["viewer"],
    },
]

SAMPLE_MODEL_VERSIONS = [
    {
        "name": "transformer",
        "version": "1.0.0",
        "path": "/models/transformer/v1.0.0",
        "metrics": {"mae": 0.02, "rmse": 0.03, "r2": 0.95},
        "is_production": True,
    },
    {
        "name": "lstm",
        "version": "1.0.0",
        "path": "/models/lstm/v1.0.0",
        "metrics": {"mae": 0.025, "rmse": 0.035, "r2": 0.93},
        "is_production": False,
    },
]

async def init_roles(db: AsyncSession) -> None:
    """Initialize roles in the database."""
    logger.info("Creating roles...")
    for role_data in SAMPLE_ROLES:
        role = await db.execute(
            select(Role).where(Role.name == role_data["name"])
        )
        role = role.scalars().first()
        
        if not role:
            role = Role(**role_data)
            db.add(role)
            logger.info(f"Created role: {role.name}")
    
    await db.commit()

async def init_users(db: AsyncSession) -> None:
    """Initialize users in the database."""
    logger.info("Creating users...")
    
    for user_data in SAMPLE_USERS:
        # Create user
        user = await crud_user.user.get_by_email(db, email=user_data["email"])
        
        if not user:
            user_in = UserCreate(
                email=user_data["email"],
                password=user_data["password"],
                full_name=user_data["full_name"],
                is_superuser=user_data["is_superuser"],
            )
            user = await crud_user.user.create(db, obj_in=user_in)
            logger.info(f"Created user: {user.email}")
        
        # Assign roles
        for role_name in user_data["roles"]:
            role = await db.execute(
                select(Role).where(Role.name == role_name)
            )
            role = role.scalars().first()
            
            if role:
                # Check if user already has this role
                has_role = await crud_user.user.has_role(
                    db, str(user.id), role_name
                )
                
                if not has_role:
                    await crud_user.user.add_role(
                        db, user_id=str(user.id), role_name=role_name
                    )
                    logger.info(f"Assigned role '{role_name}' to user '{user.email}'")
    
    await db.commit()

async def init_cryptocurrencies(db: AsyncSession) -> None:
    """Initialize cryptocurrencies in the database."""
    logger.info("Creating cryptocurrencies...")
    
    for crypto_data in SAMPLE_CRYPTOCURRENCIES:
        crypto = await crud_crypto.cryptocurrency.get_by_symbol(
            db, symbol=crypto_data["symbol"]
        )
        
        if not crypto:
            crypto_in = CryptocurrencyCreate(**crypto_data)
            crypto = await crud_crypto.cryptocurrency.create(db, obj_in=crypto_in)
            logger.info(f"Created cryptocurrency: {crypto.symbol}")
    
    await db.commit()

async def init_model_versions(db: AsyncSession) -> None:
    """Initialize model versions in the database."""
    logger.info("Creating model versions...")
    
    for model_data in SAMPLE_MODEL_VERSIONS:
        model = await db.execute(
            select(ModelVersion)
            .where(
                (ModelVersion.name == model_data["name"]) &
                (ModelVersion.version == model_data["version"])
            )
        )
        model = model.scalars().first()
        
        if not model:
            model_in = ModelVersionCreate(**model_data)
            model = ModelVersion(**model_in.dict())
            db.add(model)
            logger.info(f"Created model version: {model.name} v{model.version}")
    
    await db.commit()

async def init_price_history(db: AsyncSession, days: int = 30) -> None:
    """
    Generate sample price history data for testing.
    
    Args:
        db: Database session
        days: Number of days of historical data to generate
    """
    logger.info(f"Generating {days} days of price history...")
    
    # Get all cryptocurrencies
    result = await db.execute(select(Cryptocurrency))
    cryptocurrencies = result.scalars().all()
    
    if not cryptocurrencies:
        logger.warning("No cryptocurrencies found. Skipping price history generation.")
        return
    
    # Generate price data for each cryptocurrency
    for crypto in cryptocurrencies:
        # Check if we already have price history for this cryptocurrency
        result = await db.execute(
            select(PriceHistory)
            .where(PriceHistory.cryptocurrency_id == crypto.id)
            .limit(1)
        )
        existing = result.scalars().first()
        
        if existing:
            logger.info(f"Price history already exists for {crypto.symbol}. Skipping...")
            continue
        
        logger.info(f"Generating price history for {crypto.symbol}...")
        
        # Generate OHLCV data
        base_price = 100.0  # Base price for simulation
        price_history = []
        
        for i in range(days * 24):  # One data point per hour
            timestamp = datetime.utcnow() - timedelta(hours=i)
            
            # Simple price simulation with some randomness
            open_price = base_price * (1 + 0.1 * (i % 24) / 24)  * (1 + 0.1 * (i % 7) / 7)
            close_price = open_price * (0.99 + 0.02 * (i % 5) / 5)  # Random close price
            high = max(open_price, close_price) * (1 + 0.01 * (i % 3) / 3)
            low = min(open_price, close_price) * (0.99 - 0.01 * (i % 4) / 4)
            volume = 1000 * (1 + 0.5 * (i % 10) / 10)  # Random volume
            
            price_history.append({
                "cryptocurrency_id": crypto.id,
                "timestamp": timestamp,
                "open": open_price,
                "high": high,
                "low": low,
                "close": close_price,
                "volume": volume,
            })
        
        # Bulk insert
        if price_history:
            db.add_all([PriceHistory(**data) for data in price_history])
            await db.commit()
            logger.info(f"Added {len(price_history)} price records for {crypto.symbol}")

async def init() -> None:
    """Initialize the database."""
    logger.info("Initializing database...")
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with SessionLocal() as db:
        try:
            await init_roles(db)
            await init_users(db)
            await init_cryptocurrencies(db)
            await init_model_versions(db)
            await init_price_history(db)
            logger.info("Database initialization completed successfully")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            await db.rollback()
            raise

if __name__ == "__main__":
    asyncio.run(init())
