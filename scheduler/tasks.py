from fastapi import HTTPException
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import httpx
import asyncio
from typing import Dict, List, Any
from config.logging_config import logger
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


async def call_platform_api(
    client: httpx.AsyncClient, operation: str
) -> Dict[str, Any]:
    """플랫폼 API를 호출하는 재사용 가능한 함수"""
    base_url = f"http://localhost:{settings.PORT}/api/v1"
    try:
        response = await client.post(f"{base_url}/run/{operation}")

        if response.status_code == 200:
            logger.info(f"Platform {operation} task executed successfully")
            logger.info(f"Response: {response.json()}")
            return {
                "status": "success",
                "data": response.json(),
                "operation": operation,
            }
        else:
            error_msg = (
                f"Failed to execute {operation} task. Status: {response.status_code}"
            )
            logger.error(error_msg)
            logger.error(f"Error: {response.text}")
            return {"status": "error", "error": response.text, "operation": operation}

    except Exception as e:
        error_msg = f"Error in {operation} API call: {str(e)}"
        logger.error(error_msg)
        return {"status": "error", "error": str(e), "operation": operation}


async def execute_scheduled_task():
    """스케줄러에 의해 실행되는 작업"""
    try:
        async with httpx.AsyncClient() as client:
            # 두 API를 동시에 호출
            results = await asyncio.gather(
                call_platform_api(client, "valid"),
                call_platform_api(client, "sync"),
                return_exceptions=True,
            )

            # 결과 처리 및 로깅
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Task execution failed: {str(result)}")
                elif result["status"] == "error":
                    logger.error(
                        f"{result['operation']} task failed: {result['error']}"
                    )
                else:
                    logger.info(f"{result['operation']} task completed successfully")

            return {
                "valid": (
                    results[0]
                    if not isinstance(results[0], Exception)
                    else {"error": str(results[0])}
                ),
                "sync": (
                    results[1]
                    if not isinstance(results[1], Exception)
                    else {"error": str(results[1])}
                ),
            }

    except Exception as e:
        logger.error(f"Error in scheduled task execution: {str(e)}")
        return {"error": str(e)}
