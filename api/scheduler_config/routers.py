# api/scheduler_config/routers.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from config.db import get_db
from scheduler import tasks
from . import schemas, services
from typing import List

router = APIRouter(prefix="/scheduler", tags=["scheduler"])


@router.post("/pause")
async def pause_scheduler():
    """스케줄러를 일시 중지합니다."""
    await tasks.pause_scheduler()
    return {"message": "Scheduler paused successfully"}


@router.post("/resume")
async def resume_scheduler():
    """스케줄러를 재개합니다."""
    await tasks.resume_scheduler()
    return {"message": "Scheduler resumed successfully"}


@router.post("/stop")
async def stop_scheduler():
    """스케줄러를 완전히 중지합니다."""
    await tasks.stop_scheduler()
    return {"message": "Scheduler stopped successfully"}


@router.get("/config", response_model=List[schemas.SchedulerConfig])
async def read_configs(db: AsyncSession = Depends(get_db)):
    return await services.get_configs(db)


@router.get("/config/{task_type}", response_model=schemas.SchedulerConfig)
async def read_config(task_type: str, db: AsyncSession = Depends(get_db)):
    return await services.get_config(db, task_type)


@router.post("/config", response_model=schemas.SchedulerConfig)
async def create_config(
    config: schemas.SchedulerConfigCreate, db: AsyncSession = Depends(get_db)
):
    return await services.create_config(db, config)


@router.put("/config/{task_type}", response_model=schemas.SchedulerConfig)
async def update_config(
    task_type: str,
    config: schemas.SchedulerConfigUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await services.update_config(db, task_type, config)
