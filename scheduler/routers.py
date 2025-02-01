from fastapi import APIRouter
from . import tasks

router = APIRouter(prefix="/scheduler", tags=["scheduler"])


@router.post("/pause")
async def pause_scheduler():
    """스케줄러를 일시 중지합니다."""
    await tasks.pause_scheduler()
    return {"message": "Scheduler paused successfully"}


@router.post("/resume")
async def resume_scheduler():
    """스케줄러를 재개합니다."""
    await tasks.resume_scheduler()
    return {"message": "Scheduler resumed successfully"}


@router.post("/stop")
async def stop_scheduler():
    """스케줄러를 완전히 중지합니다."""
    await tasks.stop_scheduler()
    return {"message": "Scheduler stopped successfully"}
