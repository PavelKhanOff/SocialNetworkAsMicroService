from app.config import SQLALCHEMY_DATABASE_URL
import logging
from typing import AsyncIterator

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


logger = logging.getLogger(__name__)

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    echo=True,
)
async_session = sessionmaker(
    bind=engine, autoflush=False, future=True, class_=AsyncSession
)
Base = declarative_base()


async def get_db() -> AsyncIterator[sessionmaker]:
    try:
        yield async_session
    except SQLAlchemyError as e:
        logger.exception(e)
