from fastapi import HTTPException
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import httpx
import asyncio
from typing import Dict, List, Any
from config.logging_config import logger
from config.settings import settings
from config.db import AsyncSessionLocal  # AsyncSessionLocal import 추가
from api.scheduler_config import services, repositories  # repositories import 추가

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
        async with AsyncSessionLocal() as db:
            valid_enabled = await services.is_task_enabled(db, "valid")
            sync_enabled = await services.is_task_enabled(db, "sync")

            tasks = []
            async with httpx.AsyncClient() as client:
                if valid_enabled:
                    tasks.append(call_platform_api(client, "valid"))
                if sync_enabled:
                    tasks.append(call_platform_api(client, "sync"))

                if not tasks:
                    logger.info("All scheduled tasks are disabled")
                    return

                results = await asyncio.gather(*tasks, return_exceptions=True)

                # 결과 처리 및 last_run 업데이트
                for i, result in enumerate(results):
                    task_type = "valid" if i == 0 and valid_enabled else "sync"
                    if isinstance(result, Exception):
                        logger.error(f"Task execution failed: {str(result)}")
                    else:
                        await repositories.update_last_run(db, task_type)
                        logger.info(f"{task_type} task completed successfully")

                return {
                    "valid": results[0] if valid_enabled else {"status": "disabled"},
                    "sync": results[-1] if sync_enabled else {"status": "disabled"},
                }

    except Exception as e:
        logger.error(f"Error in scheduled task execution: {str(e)}")
        return {"error": str(e)}
