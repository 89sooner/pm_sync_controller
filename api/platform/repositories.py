from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select
from . import models


async def create_platform(db: AsyncSession, platform):
    db_platform = models.Platform(**platform.model_dump())
    db.add(db_platform)
    await db.commit()
    await db.refresh(db_platform)
    return db_platform


async def get_platforms(db: AsyncSession, skip: int = 0, limit: int = 100):
    query = select(models.Platform).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


async def get_platform(db: AsyncSession, platform_id: int):
    query = select(models.Platform).where(models.Platform.id == platform_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def update_platform(db: AsyncSession, platform_id: int, platform):
    query = select(models.Platform).where(models.Platform.id == platform_id)
    result = await db.execute(query)
    db_platform = result.scalar_one_or_none()

    if db_platform:
        for key, value in platform.model_dump().items():
            setattr(db_platform, key, value)
        await db.commit()
        await db.refresh(db_platform)
    return db_platform


async def delete_platform(db: AsyncSession, platform_id: int):
    query = select(models.Platform).where(models.Platform.id == platform_id)
    result = await db.execute(query)
    db_platform = result.scalar_one_or_none()

    if db_platform:
        await db.delete(db_platform)
        await db.commit()
    return db_platform
