import subprocess
import json
import os
from fastapi import HTTPException
from . import schemas
from .repositories import (
    create_platform,
    get_platforms,
    get_platforms_active,
    get_platform,
    update_platform,
    delete_platform,
)
from config.logging_config import logger
from config.settings import settings


async def create_new_platform(db, platform: schemas.PlatformCreate):
    return await create_platform(db=db, platform=platform)


async def get_platforms_list(db, skip: int = 0, limit: int = 100):
    return await get_platforms(db=db, skip=skip, limit=limit)


async def get_active_platforms(db):
    platforms = await get_platforms_active(db=db)
    return [platform for platform in platforms if platform.active]


async def get_platform_by_id(db, platform_id: int):
    return await get_platform(db=db, platform_id=platform_id)


async def modify_platform(db, platform_id: int, platform: schemas.PlatformUpdate):
    return await update_platform(db=db, platform_id=platform_id, platform=platform)


async def remove_platform(db, platform_id: int):
    return await delete_platform(db=db, platform_id=platform_id)


async def execute_platform_operation(operation_type: str):
    logger.info(f"Starting {operation_type} operation")

    try:
        # Node.js 앱 경로 검증
        if not settings.verify_node_app_path():
            logger.error(
                f"Node.js application directory not found: {settings.NODE_APP_DIR}"
            )
            raise ValueError(
                f"Node.js application directory not found: {settings.NODE_APP_DIR}"
            )

        # Playwright 브라우저 설치 확인 및 설치
        try:
            logger.info("Checking Playwright browser installation")
            install_process = subprocess.run(
                ["npx", "playwright", "install", "chromium"],
                cwd=settings.NODE_APP_DIR,
                capture_output=True,
                text=True,
                check=True,
            )
            logger.info("Playwright browser installation completed successfully")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install Playwright browser: {e.stderr}")
            raise

        # 실행 디렉토리 설정
        work_dir = settings.NODE_APP_DIR

        # Node.js 애플리케이션 실행을 위한 환경 변수 설정
        env_vars = {
            **os.environ.copy(),
            "PLAYWRIGHT_BROWSERS_PATH": "/root/.cache/ms-playwright",
            "NODE_ENV": "production",
            "DB_HOST": settings.DB_HOST,
            "DB_PORT": str(settings.DB_PORT),
            "DB_USER": settings.DB_USER,
            "DB_PASSWORD": settings.DB_PASSWORD,
            "DB_NAME": settings.DB_NAME,
        }

        # operation_type에 따라 실행할 스크립트 결정
        command = f"npm run {operation_type}"
        logger.info(f"Executing command in directory: {work_dir}")

        # Node.js 프로젝트 디렉토리에서 명령 실행
        process = subprocess.Popen(
            command,
            cwd=work_dir,
            shell=True,
            env=env_vars,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # 프로세스 실행 결과 수집
        stdout, stderr = process.communicate()

        if process.returncode == 0:
            try:
                # 표준 출력에서 JSON 결과 찾기
                result_data = []
                output_lines = stdout.strip().split("\n")
                for line in output_lines:
                    if line.startswith("[") and line.endswith("]"):
                        try:
                            result_data = json.loads(line)
                            break
                        except json.JSONDecodeError:
                            continue

                logger.info(f"Successfully completed {operation_type} operation")
                return {
                    "message": f"Task {operation_type} executed successfully",
                    "result": {
                        "status": "success",
                        "output": stdout,
                        "data": result_data,
                    },
                }
            except Exception as e:
                logger.warning(f"Could not parse results: {e}")
                return {
                    "message": f"Task {operation_type} executed with output parsing warning",
                    "result": {"status": "success", "output": stdout},
                }
        else:
            error_message = stderr or stdout
            logger.error(f"Error in {operation_type} operation: {error_message}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to execute {operation_type} operation: {error_message}",
            )

    except Exception as e:
        logger.error(f"Error during {operation_type} operation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to execute {operation_type} operation: {str(e)}",
        )
