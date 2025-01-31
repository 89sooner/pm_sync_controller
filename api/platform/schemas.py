from pydantic import BaseModel
from typing import Literal


class PlatformBase(BaseModel):
    name: str
    active: bool
    status: Literal["connected", "disconnected"]


class PlatformCreate(PlatformBase):
    pass


class PlatformUpdate(PlatformBase):
    pass


class Platform(PlatformBase):
    id: int

    class Config:
        from_attributes = True
