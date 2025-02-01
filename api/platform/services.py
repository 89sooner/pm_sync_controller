from fastapi import HTTPException
from . import schemas
from .repositories import (
    create_platform,
    get_platforms,
    get_platforms_active,
    get_platform,
    update_platform,
    delete_platform,
)
from config.logging_config import logger
from typing import List


async def create_new_platform(db, platform: schemas.PlatformCreate):
    return await create_platform(db=db, platform=platform)


async def get_platforms_list(db, skip: int = 0, limit: int = 100):
    return await get_platforms(db=db, skip=skip, limit=limit)


async def get_active_platforms(db):
    platforms = await get_platforms_active(db=db)
    return [platform for platform in platforms if platform.active]


async def get_platform_by_id(db, platform_id: int):
    return await get_platform(db=db, platform_id=platform_id)


async def modify_platform(db, platform_id: int, platform: schemas.PlatformUpdate):
    return await update_platform(db=db, platform_id=platform_id, platform=platform)


async def remove_platform(db, platform_id: int):
    return await delete_platform(db=db, platform_id=platform_id)


async def execute_platform_operation(
    db, platform_names: List[str], operation_type: str
):
    """
    플랫폼 작업을 실행하는 통합 함수입니다.

    Args:
        db: 데이터베이스 세션
        platform_names: 작업을 실행할 플랫폼 이름 리스트
        operation_type: 작업 유형 (valid/sync)
    """
    logger.info(f"Starting {operation_type} operation for platforms: {platform_names}")

    try:
        # 여기에 실제 플랫폼 작업 로직 구현
        # operation_type에 따라 다른 로직 실행
        if operation_type == "valid":
            # 검증 로직
            logger.info(f"Validating platforms: {platform_names}")
            result = ""
            # result = await validate_platforms(db, platform_names)
        else:
            # 동기화 로직
            logger.info(f"Synchronizing platforms: {platform_names}")
            result = ""
            # result = await sync_platforms(db, platform_names)

        logger.info(f"Successfully completed {operation_type} operation")
        return result

    except Exception as e:
        logger.error(f"Error during {operation_type} operation: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to execute {operation_type} operation"
        )
