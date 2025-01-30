# /api/webhooks/routers.py
# FastAPI 웹훅 라우터 정의

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from . import schemas, services
from config.db import get_db

router = APIRouter()


@router.post(
    "/webhook",
    response_model=schemas.WebhookStatusResponse,
    status_code=status.HTTP_200_OK,
)
async def handle_webhook(
    webhook: schemas.AlertManagerPayload, db: AsyncSession = Depends(get_db)
):
    try:
        response = await services.process_and_forward_webhook(db, webhook)
        return response

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/contact-points", response_model=List[schemas.ContactPoint])
async def get_contact_points(db: AsyncSession = Depends(get_db)):
    return await services.get_grafana_contact_points(db)
