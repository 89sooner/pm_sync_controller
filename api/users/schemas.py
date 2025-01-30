# /api/users/schemas.py
# 사용자 스키마 정의

from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: EmailStr
    name: str | None = None
        
class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True  # 이전의 orm_mode=True 대신
