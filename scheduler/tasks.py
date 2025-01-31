from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import HTTPException, APIRouter
from typing import List
from api.platform.services import get_platforms_active  # Adjust the import as needed
from config.db import get_db
from config.logging_config import logger
from contextlib import asynccontextmanager

router = APIRouter()


@asynccontextmanager
async def get_db_context():
    async for db in get_db():
        yield db


async def start_scheduler():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(fetch_active_platforms, "interval", minutes=1)
    scheduler.start()


async def fetch_active_platforms():
    async with get_db_context() as db:
        return await get_platforms_active(db)


@router.post("/run/{param}")
async def run_active_platforms_task(param: str, platforms: List[str]):
    if param not in ["valid", "sync"]:
        raise HTTPException(status_code=400, detail="Invalid parameter")

    active_platforms = await fetch_active_platforms()
    active_platform_names = [platform.name for platform in active_platforms]

    if not all(name in active_platform_names for name in platforms):
        raise HTTPException(status_code=400, detail="Some platforms are not active")

    # Add logic to handle the 'valid' or 'sync' type with the provided platforms

    return {
        "message": "Task executed successfully",
    }
