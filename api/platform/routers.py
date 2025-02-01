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
async def run_platforms(param: str, db: AsyncSession = Depends(get_db)):
    """
    플랫폼 동기화 또는 검증 작업을 실행합니다.

    Args:
        param: 실행할 작업 유형 (valid/sync)
        db: 데이터베이스 세션
    """
    if param not in ["valid", "sync"]:
        logger.error(f"Invalid parameter received: {param}")
        raise HTTPException(status_code=400, detail="Invalid parameter")

    active_platforms = await services.get_active_platforms(db)

    if not active_platforms:
        logger.warning("No active platforms found")
        raise HTTPException(status_code=404, detail="No active platforms found")

    active_platform_names = [platform.name for platform in active_platforms]
    logger.info(f"Executing {param} operation for platforms: {active_platform_names}")

    # 실제 동기화/검증 로직 구현
    result = await services.execute_platform_operation(db, active_platform_names, param)

    return {
        "message": f"Task {param} executed successfully",
        "platforms": active_platform_names,
        "result": result,
    }
