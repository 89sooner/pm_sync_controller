# /api/webhooks/schemas.py
from pydantic import BaseModel, Field
from typing import List, Dict, Any


class ContactPoint(BaseModel):
    name: str
    type: str
    settings: Any


class Alert(BaseModel):
    status: str
    labels: Dict[str, Any]
    annotations: Dict[str, Any]
    startsAt: str
    endsAt: str
    generatorURL: str
    fingerprint: str


class AlertManagerPayload(BaseModel):
    receiver: str
    status: str
    alerts: List[Alert]
    groupLabels: Dict[str, Any] = Field(default_factory=dict)
    commonLabels: Dict[str, Any] = Field(default_factory=dict)
    commonAnnotations: Dict[str, Any] = Field(default_factory=dict)
    externalURL: str
    version: str
    groupKey: str
    truncatedAlerts: int


class WebhookPayload(BaseModel):
    botEnv: str
    botId: str
    contentsType: str
    contentsId: str
    targetUserId: str
    contentsParams: Dict[str, Any]
    chatType: str
    target: str


class WebhookStatusResponse(BaseModel):
    status: str
    message: str
