from . import schemas
from .repositories import (
    create_platform,
    get_platforms,
    get_platform,
    update_platform,
    delete_platform,
)


async def create_new_platform(db, platform: schemas.PlatformCreate):
    return await create_platform(db=db, platform=platform)


async def get_platforms_list(db, skip: int = 0, limit: int = 100):
    return await get_platforms(db=db, skip=skip, limit=limit)


async def get_platform_by_id(db, platform_id: int):
    return await get_platform(db=db, platform_id=platform_id)


async def modify_platform(db, platform_id: int, platform: schemas.PlatformUpdate):
    return await update_platform(db=db, platform_id=platform_id, platform=platform)


async def remove_platform(db, platform_id: int):
    return await delete_platform(db=db, platform_id=platform_id)
