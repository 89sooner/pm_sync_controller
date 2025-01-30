# /api/webhooks/repositories.py
# 웹훅 CRUD 동작 정의

from sqlalchemy.ext.asyncio import AsyncSession
from .models import Webhook
from .schemas import WebhookPayload


async def save_webhook_data(db: AsyncSession, payload: WebhookPayload):
    # payload가 이미 딕셔너리일 경우, 변환하지 않도록 합니다
    if isinstance(payload, WebhookPayload):
        payload_dict = payload.dict()
    elif isinstance(payload, dict):
        payload_dict = payload
    else:
        raise ValueError(f"Unsupported payload type: {type(payload)}")

    print(payload_dict)  # payload 내용을 출력하여 확인합니다.

    webhook_dict = {"payload": payload_dict}  # payload 데이터를 JSON 형식으로 저장

    db_webhook = Webhook(**webhook_dict)
    db.add(db_webhook)
    await db.commit()
    await db.refresh(db_webhook)

    return db_webhook


async def fetch_grafana_contact_points(client):
    return await client.get_contact_points()
