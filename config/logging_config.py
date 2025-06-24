import logging
import logging.config
import sys
from pathlib import Path
from typing import Dict, Any
import json

from .settings import settings


class JsonFormatter(logging.Formatter):
    """JSON 형태로 로그를 포맷하는 커스텀 포맷터"""

    def format(self, record):
        log_obj = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # 예외 정보가 있다면 추가
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_obj, ensure_ascii=False)


def setup_logging() -> logging.Logger:
    """환경별 로깅 설정을 적용하고 로거 반환"""

    log_config = settings.get_logging_config()

    # 로깅 설정 딕셔너리
    logging_config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": log_config["format"],
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_config["level"],
                "formatter": "detailed" if settings.is_development else "default",
                "stream": sys.stdout,
            },
        },
        "loggers": {
            "": {  # 루트 로거
                "level": log_config["level"],
                "handlers": ["console"],
                "propagate": False,
            },
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
            "uvicorn.access": {
                "level": "INFO" if not settings.is_test else "WARNING",
                "handlers": ["console"],
                "propagate": False,
            },
            "sqlalchemy.engine": {
                "level": "INFO" if settings.is_development else "WARNING",
                "handlers": ["console"],
                "propagate": False,
            },
        },
    }

    # 프로덕션 환경에서 파일 로깅 추가
    if settings.is_production and log_config.get("file_path"):
        log_file_path = Path(log_config["file_path"])
        log_file_path.parent.mkdir(parents=True, exist_ok=True)

        logging_config["handlers"]["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "json",  # JSON 포맷터 사용
            "filename": str(log_file_path),
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "encoding": "utf-8",
        }

        # 루트 로거에 파일 핸들러 추가
        logging_config["loggers"][""]["handlers"].append("file")

    # 로깅 설정 적용
    logging.config.dictConfig(logging_config)

    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured for {settings.NODE_ENV} environment")
    logger.info(f"Log level: {log_config['level']}")

    return logger


# 기본 로거 설정
logger = setup_logging()
