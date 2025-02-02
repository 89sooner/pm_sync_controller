# /app.py
# FastAPI 애플리케이션(라우터 포함) 초기화

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from scheduler.tasks import start_scheduler

from api.users import routers as users_routers
from api.webhooks import routers as webhooks_routers
from api.platform import routers as platform_routers
from api.scheduler_config import routers as scheduler_routers
from config.db import Base, engine
from config.logging_config import logger

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 비동기로 테이블 생성하는 함수
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# 애플리케이션 시작 시 테이블 생성
@app.on_event("startup")
async def startup_event():
    await create_tables()
    await start_scheduler()


# 요청 및 응답 로깅 미들웨어
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logger.info(f"Request: {request.method} {request.url}")
        logger.info(f"Request headers: {request.headers}")

        # 요청 본문 로깅
        try:
            request_body = await request.json()
            logger.info(f"Request body: {request_body}")
        except Exception as e:
            logger.error(f"Failed to log request body: {e}")

        response = await call_next(request)
        logger.info(f"Response status: {response.status_code}")
        return response


# 미들웨어 등록
# app.add_middleware(LoggingMiddleware)


# 라우터 등록
# app.include_router(users_routers.router, prefix="/api/v1")
# app.include_router(webhooks_routers.router, prefix="/api/v1")
app.include_router(platform_routers.router, prefix="/api/v1")
app.include_router(scheduler_routers.router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=True)
