# /api/users/services.py
# 비즈니스 로직 정의

from . import schemas
from .repositories import get_user_by_email, create_user, get_user, get_users
from .security import get_password_hash

# async def authenticate_user(db, email: str, password: str):
#     user = await get_user_by_email(db, email)
#     if not user:
#         return False
#     if not verify_password(password, user.hashed_password):
#         return False
#     return user


async def create_new_user(db, user_in: schemas.UserCreate):
    db_user = await get_user_by_email(db, email=user_in.email)
    if db_user:
        raise ValueError("Email already registered")

    user_data = user_in.model_dump()
    hashed_password = get_password_hash(user_data["password"])
    del user_data["password"]
    user_data["hashed_password"] = hashed_password

    return await create_user(db, user_data)


async def get_user_by_id(db, user_id: int):
    return await get_user(db, user_id)


async def get_user_list(db, skip: int = 0, limit: int = 10):
    return await get_users(db, skip, limit)
