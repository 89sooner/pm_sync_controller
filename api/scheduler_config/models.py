# api/scheduler_config/models.py
from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.sql import func
from config.db import Base


class SchedulerConfig(Base):
    __tablename__ = "scheduler_config"

    id = Column(Integer, primary_key=True, index=True)
    task_type = Column(String(50), unique=True, nullable=False)  # 'valid' 또는 'sync'
    is_active = Column(Boolean, default=True)
    last_run = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
