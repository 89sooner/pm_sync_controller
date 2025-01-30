# /api/webhooks/models.py
# 웹훅 모델 정의

from sqlalchemy import Column, Integer, JSON, DateTime
from datetime import datetime
from config.db import Base


class Webhook(Base):
    __tablename__ = "message_push_db"

    id = Column(Integer, primary_key=True, index=True)
    payload = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
