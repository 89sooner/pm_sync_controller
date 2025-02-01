from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import HTTPException
from config.logging_config import logger
import httpx
from config.settings import settings

# 전역 변수로 스케줄러 객체 선언
scheduler = AsyncIOScheduler()


async def start_scheduler():
    """스케줄러 초기화 및 시작"""
    global scheduler

    # 기존 스케줄러가 실행 중이면 중지
    if scheduler.running:
        scheduler.shutdown()
        scheduler = AsyncIOScheduler()

    scheduler.add_job(execute_scheduled_task, "interval", minutes=1, id="platform_sync")
    scheduler.start()
    logger.info("Scheduler started - Platform sync task scheduled for every minute")


async def stop_scheduler():
    """스케줄러 중지"""
    global scheduler

    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler stopped successfully")
    else:
        logger.info("Scheduler is not running")


async def pause_scheduler():
    """스케줄러 일시 중지 (기존 작업은 유지)"""
    global scheduler
    if scheduler.running:
        scheduler.pause_job("platform_sync")
        logger.info("Scheduler paused - Task will resume when unpaused")
    else:
        logger.info("Scheduler is not running")


async def resume_scheduler():
    """스케줄러 재개"""
    global scheduler
    if scheduler.running:
        scheduler.resume_job("platform_sync")
        logger.info("Scheduler resumed - Task will continue as scheduled")
    else:
        logger.info("Scheduler is not running")


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
