# api/scheduler_config/repositories.py
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from . import models


async def get_scheduler_config(db: AsyncSession, task_type: str):
    query = select(models.SchedulerConfig).where(
        models.SchedulerConfig.task_type == task_type
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_scheduler_configs(db: AsyncSession):
    query = select(models.SchedulerConfig)
    result = await db.execute(query)
    return result.scalars().all()


async def create_scheduler_config(db: AsyncSession, config):
    db_config = models.SchedulerConfig(**config.dict())
    db.add(db_config)
    await db.commit()
    await db.refresh(db_config)
    return db_config


async def update_scheduler_config(db: AsyncSession, task_type: str, is_active: bool):
    config = await get_scheduler_config(db, task_type)
    if config:
        config.is_active = is_active
        await db.commit()
        await db.refresh(config)
    return config


async def update_last_run(db: AsyncSession, task_type: str):
    config = await get_scheduler_config(db, task_type)
    if config:
        config.last_run = func.now()
        await db.commit()
        await db.refresh(config)
    return config
