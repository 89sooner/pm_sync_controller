# /api/users/repositories.py
# 사용자 crud 동작 정의

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from . import models


async def create_user(db: AsyncSession, user_data: dict):
    db_user = models.User(**user_data)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def get_user_by_email(db, email: str):
    query = select(models.User).where(models.User.email == email)
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def get_user(db, user_id: int):
    query = select(models.User).where(models.User.id == user_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def get_users(db, skip: int = 0, limit: int = 10):
    query = select(models.User).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()
