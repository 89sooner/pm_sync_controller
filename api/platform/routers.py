from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from . import services, schemas
from config.db import get_db
from config.logging_config import logger

router = APIRouter()


@router.post("/platforms/", response_model=schemas.Platform)
async def create_platform(
    platform: schemas.PlatformCreate, db: AsyncSession = Depends(get_db)
):
    return await services.create_new_platform(db=db, platform=platform)


@router.get("/platforms/", response_model=list[schemas.Platform])
async def read_platforms(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    platforms = await services.get_platforms_list(db=db, skip=skip, limit=limit)
    return platforms


@router.get("/platforms/active", response_model=list[schemas.Platform])
async def get_active_platforms_list(db: AsyncSession = Depends(get_db)):
    active_platforms = await services.get_active_platforms(db)
    return active_platforms


@router.get("/platforms/{platform_id}", response_model=schemas.Platform)
async def read_platform(platform_id: int, db: AsyncSession = Depends(get_db)):
    db_platform = await services.get_platform_by_id(db=db, platform_id=platform_id)
    if db_platform is None:
        raise HTTPException(status_code=404, detail="Platform not found")
    return db_platform


@router.put("/platforms/{platform_id}", response_model=schemas.Platform)
async def update_platform(
    platform_id: int,
    platform: schemas.PlatformUpdate,
    db: AsyncSession = Depends(get_db),
):
    db_platform = await services.modify_platform(
        db=db, platform_id=platform_id, platform=platform
    )
    if db_platform is None:
        raise HTTPException(status_code=404, detail="Platform not found")
    return db_platform


@router.delete("/platforms/{platform_id}")
async def delete_platform(platform_id: int, db: AsyncSession = Depends(get_db)):
    db_platform = await services.remove_platform(db=db, platform_id=platform_id)
    if db_platform is None:
        raise HTTPException(status_code=404, detail="Platform not found")
    return {"message": "Platform deleted"}


@router.post("/run/{param}")
async def run_platforms(param: str):
    if param not in ["valid", "sync"]:
        logger.error(f"Invalid parameter received: {param}")
        raise HTTPException(status_code=400, detail="Invalid parameter")

    result = await services.execute_platform_operation(param)

    return {
        "message": f"Task {param} executed successfully",
        "result": result,
    }
