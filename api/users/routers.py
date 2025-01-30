# /api/users/routers.py
# FastAPI 사용자 라우터 정의

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from .security import verify_password
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from . import schemas, services
from config.db import get_db

router = APIRouter()

# @router.post("/login", response_model=schemas.Token)
# async def login(
#     form_data: OAuth2PasswordRequestForm = Depends(),
#     db: AsyncSession = Depends(get_db)
# ):
#     user = await services.authenticate_user(db, form_data.username, form_data.password)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     access_token = create_access_token(data={"sub": user.email})
#     return {"access_token": access_token, "token_type": "bearer"}


@router.post(
    "/users/", response_model=schemas.User, status_code=status.HTTP_201_CREATED
)
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    try:
        return await services.create_new_user(db, user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/users/", response_model=List[schemas.User])
async def read_users(
    skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)
):
    return await services.get_users(db, skip, limit)


@router.get("/users/{user_id}", response_model=schemas.User)
async def read_user(user_id: int, db: AsyncSession = Depends(get_db)):
    db_user = await services.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return db_user
