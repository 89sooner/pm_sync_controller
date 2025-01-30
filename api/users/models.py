# /api/users/models.py
# 사용자 모델 정의

from sqlalchemy import Column, Integer, String, Boolean
from config.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
