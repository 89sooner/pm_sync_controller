# /config/settings.py
# 애플리케이션 정의(필요에 따라 추가)

from pydantic_settings import BaseSettings
from typing import Optional
import os
from pathlib import Path


class Settings(BaseSettings):
    # Proxy 설정
    HTTP_PROXY: Optional[str] = None
    HTTPS_PROXY: Optional[str] = None
    NO_PROXY: Optional[str] = None

    # 데이터베이스 설정
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_URL: Optional[str] = None  # 생성자에서 동적으로 설정
    # DATABASE_URL: Optional[str]

    # 애플리케이션 설정
    PROJECT_NAME: str = "FastAPI PM Sync Control App"
    VERSION: str = "1.0.0"
    PORT: Optional[int]
    PYTHONPATH: Optional[str]

    # Node.js 프로젝트 설정
    NODE_APP_NAME: str
    HOST_USER: str  # 호스트 머신의 사용자 이름
    HOST_WORKSPACE: str = "work"  # 작업 디렉토리 이름
    NODE_APP_PORT: int

    @property
    def NODE_APP_DIR(self) -> str:
        return f"/home/{self.HOST_USER}/{self.HOST_WORKSPACE}/pension_manager/{self.NODE_APP_NAME}"

    def model_post_init(self, *args, **kwargs) -> None:
        # DB_URL을 환경변수에서 읽은 값으로 동적 생성
        if not self.DB_URL:
            self.DB_URL = f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    def verify_node_app_path(self) -> bool:
        """Node.js 애플리케이션 경로를 검증합니다."""
        return os.path.exists(self.NODE_APP_DIR)

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"  # 추가 필드 허용


settings = Settings()
