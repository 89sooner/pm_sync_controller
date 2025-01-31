# api/platform/models.py
from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.sql import func

from config.db import Base


class Platform(Base):
    __tablename__ = "platform"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    status = Column(String(50), nullable=False)
