# /config/db.py
# 데이터베이스 설정

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.orm import declarative_base
from .settings import settings
from typing import AsyncGenerator

engine = create_async_engine(
    settings.DB_URL,
    echo=True,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    autocommit=False,
    expire_on_commit=False,
    class_=AsyncSession,
)

naming_convention = {
    "ix": "%(column_0_label)s_idx",
    "uq": "%(table_name)s_%(column_0_name)s_key",
    "ck": "%(table_name)s_%(constraint_name)s_check",
    "fk": "%(table_name)s_%(column_0_name)s_fkey",
    "pk": "%(table_name)s_pkey",
}

Base = declarative_base(metadata=MetaData(naming_convention=naming_convention))


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """비동기 데이터베이스 세션을 제공하는 의존성 함수"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
