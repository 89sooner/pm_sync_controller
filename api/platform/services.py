import httpx
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
from config.settings import settings
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


async def execute_platform_operation(operation_type: str):
    logger.info(f"Starting {operation_type} operation")

    try:
        # Node.js Platform Service 앱 경로 검증
        if not settings.verify_node_app_path():
            logger.error(
                f"Node.js application directory not found: {settings.NODE_APP_DIR}"
            )
            raise ValueError(
                f"Node.js application directory not found: {settings.NODE_APP_DIR}"
            )

        #  Node.js Platform Service 앱 URL 구성
        node_app_url = f"http://localhost:{settings.NODE_APP_PORT}/{operation_type}"
        logger.info(f"Sending request to platform service: {node_app_url}")

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(node_app_url, timeout=60.0)

                if response.status_code == 200:
                    result_data = response.json()
                    logger.info(f"Successfully completed {operation_type} operation")
                    return {
                        "message": f"Task {operation_type} executed successfully",
                        "result": result_data,
                    }
                else:
                    error_message = response.text
                    logger.error(f"Platform service error: {error_message}")
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Platform service error: {error_message}",
                    )

            except httpx.TimeoutError:
                logger.error(f"Request to platform service timed out after 60 seconds")
                raise HTTPException(
                    status_code=504, detail="Platform service request timed out"
                )

            except httpx.RequestError as e:
                logger.error(f"Failed to connect to platform service: {str(e)}")
                raise HTTPException(
                    status_code=503, detail=f"Platform service unavailable: {str(e)}"
                )

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Unexpected error during {operation_type} operation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to execute {operation_type} operation: {str(e)}",
        )
