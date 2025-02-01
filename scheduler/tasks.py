from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import HTTPException
from config.logging_config import logger
import httpx
from config.settings import settings


async def start_scheduler():
    """스케줄러 초기화 및 시작"""
    scheduler = AsyncIOScheduler()
    scheduler.add_job(execute_scheduled_task, "interval", minutes=1)
    scheduler.start()
    logger.info("Scheduler started - Platform sync task scheduled for every minute")


async def execute_scheduled_task():
    """스케줄러에 의해 실행되는 작업"""
    try:
        async with httpx.AsyncClient() as client:
            # 내부 API 호출
            base_url = f"http://localhost:{settings.PORT}/api/v1"
            response = await client.post(f"{base_url}/run/valid")

            if response.status_code == 200:
                logger.info("Scheduled platform task executed successfully")
                logger.info(f"Response: {response.json()}")
            else:
                logger.error(
                    f"Failed to execute scheduled task. Status: {response.status_code}"
                )
                logger.error(f"Error: {response.text}")

    except Exception as e:
        logger.error(f"Error in scheduled task execution: {str(e)}")
