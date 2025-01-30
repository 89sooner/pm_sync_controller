# /api/webhooks/services.py
# 웹훅 비즈니스 로직 정의

from .schemas import AlertManagerPayload, WebhookStatusResponse
from .repositories import save_webhook_data, fetch_grafana_contact_points
from .grafana_client import GrafanaClient
from config.settings import settings
from datetime import datetime
import httpx
import json
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError


async def process_and_forward_webhook(
    db, webhook_in: AlertManagerPayload
) -> WebhookStatusResponse:

    # 외부 API로 전송할 Payload 생성
    alerts_summary = [
        {
            "alertname": alert.labels.get("alertname", ""),
            "status": alert.status,
            "instance": alert.labels.get("instance", ""),
            "job": alert.labels.get("job", ""),
            "severity": alert.labels.get("severity", ""),
            "description": alert.annotations.get("description", ""),
            "summary": alert.annotations.get("summary", ""),
            "startsAt": alert.startsAt,
            "endsAt": alert.endsAt,
            "generatorURL": alert.generatorURL,
        }
        for alert in webhook_in.alerts
    ]

    # 프록시 설정
    transport = httpx.AsyncHTTPTransport(proxy=httpx.Proxy(url=settings.HTTP_PROXY))

    # Webhook 데이터를 외부 API로 전송
    async with httpx.AsyncClient(transport=transport) as client:
        for alert in alerts_summary:

            payload = {
                "botEnv": settings.BOT_ENV,
                "botId": settings.BOT_ID,
                "contentsType": settings.BOT_CONTENTS_TYPE,
                "contentsId": settings.BOT_CONTENTS_ID,
                "targetUserId": settings.BOT_TARGET_USER_ID,
                "contentsParams": {
                    "subject": alert["alertname"],
                    "contents": alert["description"],
                    "status": alert["status"],
                    "instance": alert["instance"],
                    "job": alert["job"],
                    "severity": alert["severity"],
                    "summary": alert["summary"],
                    "startsAt": alert["startsAt"],
                    "endsAt": alert["endsAt"],
                    "generatorURL": alert["generatorURL"],
                },
                "chatType": "general",
                "target": "user",
            }

            try:
                # Webhook 데이터를 DB에 저장
                await save_webhook_data(db, payload)
            except SQLAlchemyError as e:
                print(f"Database error occurred: {str(e)}")
                raise HTTPException(
                    status_code=500, detail="Failed to save webhook data"
                )
            except Exception as e:
                print(f"Unexpected error occurred: {str(e)}")
                raise HTTPException(
                    status_code=500, detail="An unexpected error occurred"
                )

            try:
                response = await client.post(
                    settings.BOT_TARGET_URL,
                    json=payload,
                    headers={
                        "Accept": "application/json",
                        "Authorization": f"Bearer {settings.BOT_AUTH_TOKEN}",
                        "Content-Type": "application/json",
                    },
                )
                response.raise_for_status()
                print(f"Successfully sent webhook. Status code: {response.status_code}")

            except httpx.HTTPStatusError as exc:
                print(
                    f"HTTP error occurred: {exc.response.status_code} - {exc.response.text}"
                )
                return WebhookStatusResponse(
                    status="error", message="processed with an error"
                )

            except httpx.ConnectError as exc:
                print(f"Connection error occurred: {exc}")
                raise HTTPException(
                    status_code=500, detail="Failed to connect to the external server"
                )
            except Exception as exc:
                print(f"An unexpected error occurred: {exc}")
                raise HTTPException(
                    status_code=500, detail="An unexpected error occurred"
                )

    return WebhookStatusResponse(
        status="success",
        message=f"Webhook processed successfully push alerts",
    )


async def get_grafana_contact_points(db):
    # Grafana 클라이언트를 통해 contact points 가져오기
    grafana_client = GrafanaClient()
    contact_points = await fetch_grafana_contact_points(grafana_client)
    return contact_points
