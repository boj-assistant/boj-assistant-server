from app.core.config import settings
from typing import Optional
import asyncpg
import logging

logger = logging.getLogger(__name__)

db_pool: Optional[asyncpg.Pool] = None

async def init_db_pool() :
    global db_pool
    if db_pool is None:
        try:
            db_pool = await asyncpg.create_pool(
                host=settings.DB_HOST,
                port=settings.DB_PORT,
                database=settings.DB_NAME,
                user=settings.DB_USER,
                password=settings.DB_PASSWORD,
                min_size=5,
                max_size=30
            )
            if db_pool : 
                logger.info(f"Database pool initialized")
        except Exception as e:
            logger.error(f"Database pool initialization failed: {e}")
            raise

async def get_db_pool() -> asyncpg.Pool:
    global db_pool
    if db_pool is None:
        await init_db_pool()
    return db_pool

async def close_db_pool():
    global db_pool
    if db_pool:
        try:
            await db_pool.close()
            logger.info(f"Database pool closed")
        except Exception as e:
            logger.error(f"Error closing database pool: {e}")
        finally:
            db_pool = None
    else:
        logger.info("Database pool already closed")