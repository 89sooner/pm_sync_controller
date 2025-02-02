# api/scheduler_config/schemas.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class SchedulerConfigBase(BaseModel):
    task_type: str
    is_active: bool


class SchedulerConfigCreate(SchedulerConfigBase):
    pass


class SchedulerConfigUpdate(BaseModel):
    is_active: bool


class SchedulerConfig(SchedulerConfigBase):
    id: int
    last_run: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
