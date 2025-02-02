# api/scheduler_config/services.py
from sqlalchemy.ext.asyncio import AsyncSession
from . import repositories, schemas
from fastapi import HTTPException


async def get_config(db: AsyncSession, task_type: str):
    config = await repositories.get_scheduler_config(db, task_type)
    if not config:
        raise HTTPException(status_code=404, detail=f"Config for {task_type} not found")
    return config


async def get_configs(db: AsyncSession):
    return await repositories.get_scheduler_configs(db)


async def create_config(db: AsyncSession, config: schemas.SchedulerConfigCreate):
    return await repositories.create_scheduler_config(db, config)


async def update_config(
    db: AsyncSession, task_type: str, config: schemas.SchedulerConfigUpdate
):
    db_config = await repositories.update_scheduler_config(
        db, task_type, config.is_active
    )
    if not db_config:
        raise HTTPException(status_code=404, detail=f"Config for {task_type} not found")
    return db_config


async def is_task_enabled(db: AsyncSession, task_type: str) -> bool:
    config = await repositories.get_scheduler_config(db, task_type)
    return bool(config and config.is_active)
