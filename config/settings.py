# /config/settings.py
# 애플리케이션 정의(필요에 따라 추가)

from pydantic_settings import BaseSettings
from typing import Optional, Dict, Any
import os
from pathlib import Path


def get_env_file() -> str:
    """환경에 따라 적절한 .env 파일 경로를 반환"""
    node_env = os.getenv("NODE_ENV", "development")

    env_file_map = {
        "production": ".env.prod",
        "development": ".env.dev",
        "test": ".env.test",
    }

    return env_file_map.get(node_env, ".env.dev")


def validate_env_file_exists(env_file: str) -> bool:
    """환경 파일 존재 여부 확인"""
    if not Path(env_file).exists():
        print(
            f"Warning: Environment file '{env_file}' not found. Using environment variables only."
        )
        return False
    return True


class Settings(BaseSettings):
    # === 환경 설정 ===
    NODE_ENV: str = "development"  # development, production, test

    # === Proxy 설정 ===
    HTTP_PROXY: Optional[str] = None
    HTTPS_PROXY: Optional[str] = None
    NO_PROXY: Optional[str] = None

    # === 데이터베이스 설정 ===
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int = 5432
    DB_NAME: str
    DB_URL: Optional[str] = None  # 동적으로 생성됨

    # === 애플리케이션 설정 ===
    PROJECT_NAME: str = "FastAPI PM Sync Control App"
    VERSION: str = "1.0.0"
    PORT: int = 8080
    PYTHONPATH: Optional[str]

    # === 로깅 설정 ===
    LOG_LEVEL: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: Optional[str] = None  # 파일 로깅 경로 (선택사항)

    # === Node.js 프로젝트 설정 ===
    NODE_APP_NAME: str
    HOST_USER: str  # 호스트 머신의 사용자 이름
    HOST_WORKSPACE: str = "work"  # 작업 디렉토리 이름
    NODE_APP_PORT: int = 8090

    # === 환경별 편의 프로퍼티 ===
    @property
    def is_production(self) -> bool:
        """프로덕션 환경인지 확인"""
        return self.NODE_ENV == "production"

    @property
    def is_development(self) -> bool:
        """개발 환경인지 확인"""
        return self.NODE_ENV == "development"

    @property
    def is_test(self) -> bool:
        """테스트 환경인지 확인"""
        return self.NODE_ENV == "test"

    @property
    def NODE_APP_DIR(self) -> str:
        """환경에 따라 다른 경로 반환"""
        if self.NODE_ENV == "production":
            # AWS EC2 프로덕션 환경 경로
            return f"/home/{self.HOST_USER}/{self.HOST_WORKSPACE}/{self.NODE_APP_NAME}"
        else:
            # 개발 환경 경로
            return f"/home/{self.HOST_USER}/{self.HOST_WORKSPACE}/pension_manager/{self.NODE_APP_NAME}"

    @property
    def database_url(self) -> str:
        """데이터베이스 URL 반환 (DB_URL이 없으면 동적 생성)"""
        if self.DB_URL:
            return self.DB_URL
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    def model_post_init(self, *args, **kwargs) -> None:
        """모델 초기화 후 DB_URL 동적 생성"""
        if not self.DB_URL:
            self.DB_URL = self.database_url

    def verify_node_app_path(self) -> bool:
        """Node.js 애플리케이션 경로 검증"""
        path_exists = os.path.exists(self.NODE_APP_DIR)
        if not path_exists:
            print(f"Warning: Node.js app path does not exist: {self.NODE_APP_DIR}")
        return path_exists

    def get_logging_config(self) -> Dict[str, Any]:
        """환경별 로깅 설정 반환"""
        base_config = {
            "level": self.LOG_LEVEL,
            "format": self.LOG_FORMAT,
            "disable_existing_loggers": False,
        }

        if self.is_production:
            # 프로덕션: 파일 로깅 + 구조화된 로그
            base_config.update(
                {
                    "level": "INFO",
                    "handlers": ["file", "console"],
                    "file_path": self.LOG_FILE or "/var/log/pm_sync_controller.log",
                }
            )
        elif self.is_development:
            # 개발: 콘솔 로깅 + 디버그 레벨
            base_config.update(
                {
                    "level": "DEBUG",
                    "handlers": ["console"],
                    "show_sql": True,  # SQL 쿼리 로깅
                }
            )
        else:  # test
            # 테스트: 최소한의 로깅
            base_config.update({"level": "WARNING", "handlers": ["console"]})

        return base_config

    class Config:
        env_file = get_env_file()
        case_sensitive = False
        extra = "allow"
        env_file_encoding = "utf-8"

        @classmethod
        def prepare_field_env_vars(cls, field_name: str, field_info) -> list:
            """환경변수 이름 변환 규칙"""
            return [field_name.upper(), field_name.lower()]


# 글로벌 설정 인스턴스
settings = Settings()

# 환경 파일 존재 여부 확인
env_file = get_env_file()
validate_env_file_exists(env_file)
