# Platform Sync Controller

Platform Sync Controller는 숙박 예약 플랫폼의 동기화 및 검증을 관리하는 FastAPI 기반의 컨트롤러 시스템입니다. 다양한 플랫폼의 예약, 가격, 재고 정보를 검증하고 동기화하는 작업을 스케줄링하고 모니터링하는 기능을 제공합니다.

## 참고 자료

본 프로젝트는 아래 문서를 참고하여 구조화되었습니다:

- [FastAPI 풀스택 블로그 프로젝트 구조](https://www.gdsanadevlog.com/planguages/real-python-fastapi-%ED%92%80%EC%8A%A4%ED%83%9D-%EB%B8%94%EB%A1%9C%EA%B7%B8-%EA%B0%9C%EB%B0%9C%ED%95%98%EA%B8%B0-%ED%94%84%EB%A1%9C%EC%A0%9D%ED%8A%B8-%EA%B5%AC%EC%A1%B0-%EB%A7%8C%EB%93%A4%EA%B8%B0/)

## 시스템 아키텍처

본 프로젝트는 FastAPI를 기반으로 한 마이크로서비스 아키텍처를 채택하여 플랫폼 동기화와 검증 작업을 효율적으로 관리합니다. 각 컴포넌트는 특정 비즈니스 도메인을 담당하며, 모듈화된 구조를 통해 유지보수성과 확장성을 확보합니다.

### 주요 컴포넌트

1. Platform Service

   - 플랫폼 CRUD 작업 처리
   - 활성 플랫폼 관리
   - RESTful API 엔드포인트 제공

2. Scheduler Service

   - 주기적인 동기화/검증 작업 스케줄링
   - 작업 실행 상태 관리
   - 스케줄러 제어 (시작/일시정지/재개/중지)

3. API Gateway
   - 요청/응답 로깅
   - CORS 미들웨어
   - 에러 핸들링

### 주요 기능

1. 플랫폼 관리

   - 플랫폼 등록/조회/수정/삭제
   - 활성 플랫폼 필터링
   - 플랫폼 상태 관리

2. 작업 스케줄링

   - 매 분마다 동기화/검증 작업 실행
   - 비동기 작업 처리
   - 작업 결과 모니터링

3. 에러 처리 및 로깅
   - 상세한 에러 메시지 제공
   - 시스템 작동 상태 로깅
   - 요청/응답 모니터링

## 개발 환경 설정

### 요구사항

- Python 3.12 이상
- Poetry
- PostgreSQL
- Docker & Docker Compose
- pyenv (Python 버전 관리)

### 초기 설정

1. pyenv 설치 및 Python 버전 설정

```bash
# pyenv 설치 (시스템별 설치 방법은 공식 문서 참고)
pyenv install 3.12.0
pyenv local 3.12.0
```

2. Poetry 설치 및 의존성 관리

```bash
# Poetry 설치 (시스템별 설치 방법은 공식 문서 참고)
curl -sSL https://install.python-poetry.org | python3 -
poetry install
poetry lock
```

### Migrations 설정 및 관리

1. Alembic 설치 및 초기화

```bash
# Alembic 설치
poetry add alembic

# migrations 디렉토리 생성
mkdir -p migrations/versions
chmod -R 777 migrations/versions

# 비동기 마이그레이션 초기화
poetry run alembic init -t async migrations
```

2. env.py 설정

- migrations/env.py 파일에 모델 import 추가

```python
from config.settings import settings
from config.db import Base
from api.users import models
from api.scheduler.models import SchedulerConfig  # 새로운 모델 추가 시 import 필요

target_metadata = Base.metadata
```

3. 마이그레이션 파일 생성 및 적용

```bash
# 새로운 마이그레이션 파일 생성
poetry run alembic revision --autogenerate -m "설명"

# 마이그레이션 적용
poetry run alembic upgrade head

# 마이그레이션 롤백 (필요한 경우)
poetry run alembic downgrade -1
```

4. 마이그레이션 히스토리 확인

```bash
# 현재 마이그레이션 상태 확인
poetry run alembic current

# 마이그레이션 히스토리 확인
poetry run alembic history
```

5. 데이터 마이그레이션

- 데이터 마이그레이션이 필요한 경우 별도의 스크립트 작성
- migrations/versions 디렉토리에 데이터 마이그레이션 파일 추가

### Git 원격 저장소 설정

```bash
git remote rename origin old-origin
git remote add origin [NEW_REPOSITORY_URL]
```

### 실행 방법

다음 세 가지 방법 중 하나를 선택하여 애플리케이션을 실행할 수 있습니다:

#### 방법 1: 직접 실행

```bash
export PYTHONPATH=.
uvicorn main:app --reload --host 0.0.0.0 --port 8080
```

#### 방법 2: Docker Compose 사용

```bash
docker compose up -d --build
```

#### 방법 3: 실행 스크립트 사용

```bash
./run_app.sh
```

실행 후 `http://localhost:8080/docs`에서 API 문서를 확인할 수 있습니다.

## API 엔드포인트

### Platform API

platforms의 활성 상태에 따라 pm_apps 컨트롤

- `POST /api/v1/platforms/`: 새로운 플랫폼 생성
- `GET /api/v1/platforms/`: 전체 플랫폼 목록 조회
- `GET /api/v1/platforms/active`: 활성 플랫폼 목록 조회
- `GET /api/v1/platforms/{platform_id}`: 특정 플랫폼 조회
- `PUT /api/v1/platforms/{platform_id}`: 플랫폼 정보 수정
- `DELETE /api/v1/platforms/{platform_id}`: 플랫폼 삭제
- `POST /api/v1/run/{param}`: 플랫폼 작업 실행 (valid/sync)

### Scheduler API

fastapi scheduler의 컨트롤

1. Scheduler 전체 제어
2. Scheduler task_type에 따른 일부 제어 (schvalid/sync)

- `POST /api/v1/scheduler/pause`: 스케줄러 일시 중지
- `POST /api/v1/scheduler/resume`: 스케줄러 재개
- `POST /api/v1/scheduler/stop`: 스케줄러 중지
- `GET /api/v1/scheduler/config`: 스케줄러 task_type 설정 조회
- `POST /api/v1/scheduler/config`: 스케줄러 task_type 설정 수정
- `GET /api/v1/scheduler/config/{task_type}`: 특정 task_type 설정 조회
- `PUT /api/v1/scheduler/config/{task_type}`: 특정 task_type 설정 수정

## 디렉토리 구조

### platform api 위주

```
platform-sync-controller/
├── api/
│   ├── platform/
│   │   ├── models.py     # 데이터베이스 모델
│   │   ├── repositories.py # 데이터 접근 계층
│   │   ├── routers.py    # API 라우팅
│   │   ├── schemas.py    # Pydantic 스키마
│   │   └── services.py   # 비즈니스 로직
│   ├── scheduler_config/
│   │   ├── __init__.py
│   │   ├── models.py     # 데이터베이스 모델
│   │   ├── repositories.py # 데이터 접근 계층
│   │   ├── routers.py    # API 라우팅
│   │   ├── schemas.py    # Pydantic 스키마
│   │   └── services.py   # 비즈니스 로직
├── config/
│   ├── db.py            # 데이터베이스 설정
│   ├── logging_config.py # 로깅 설정
│   └── settings.py      # 환경 설정
├── scheduler/
│   └── tasks.py       # 스케줄러 작업
└── migrations/          # Alembic 마이그레이션
```

### 전체 구조

```
fastapi_webhooks-app/
├── api/
│   ├── __init__.py
│   ├── platform/
│   │   ├── __init__.py
│   │   ├── models.py     # 데이터베이스 모델
│   │   ├── repositories.py # 데이터 접근 계층
│   │   ├── routers.py    # API 라우팅
│   │   ├── schemas.py    # Pydantic 스키마
│   │   └── services.py   # 비즈니스 로직
│   ├── scheduler_config/
│   │   ├── __init__.py
│   │   ├── models.py     # 데이터베이스 모델
│   │   ├── repositories.py # 데이터 접근 계층
│   │   ├── routers.py    # API 라우팅
│   │   ├── schemas.py    # Pydantic 스키마
│   │   └── services.py   # 비즈니스 로직
├── config/
│   ├── __init__.py
│   ├── db.py            # 데이터베이스 설정
│   ├── logging_config.py # 로깅 설정
│   └── settings.py      # 환경 설정
├── scheduler/
│   ├── __init__.py
│   └── tasks.py       # 스케줄러 작업
├── migrations/          # Alembic 마이그레이션
│   ├── versions/
│   ├── README
│   ├── env.py
│   ├── script.py.mako
│   └── versions
├── .env
├── .env.sample
├── .gitignore
├── alembic.ini
├── app.py
├── docker-compose.yml
├── Dockerfile
├── poetry.lock
├── README.md
├── run_app.sh
└── pyproject.toml
```

## 확장 및 커스터마이징

1. 새로운 플랫폼 추가

   - `api/platform/models.py`에 플랫폼 모델 정의
   - `api/platform/schemas.py`에 검증 스키마 추가
   - `api/platform/services.py`에 비즈니스 로직 구현

2. 스케줄러 작업 추가

   - `scheduler/tasks.py`에 새로운 작업 정의
   - 스케줄러 설정 수정

3. API 엔드포인트 추가
   - 새로운 라우터 모듈 생성
   - `app.py`에 라우터 등록

## 모니터링 및 로깅

- 애플리케이션 로그: `logging_config.py` 설정에 따라 INFO 레벨 이상의 로그 기록
- API 요청/응답 로깅: LoggingMiddleware를 통한 상세 로그 기록
- 스케줄러 작업 상태: 작업 실행 결과 및 에러 로깅

## 문제 해결 및 디버깅

1. 데이터베이스 연결 문제

   - 환경 변수 설정 확인
   - PostgreSQL 서비스 상태 확인
   - 데이터베이스 마이그레이션 상태 확인

2. 마이그레이션 문제

   - migrations/versions 디렉토리 권한 확인
   - 모델 import 확인
   - alembic.ini 설정 확인
   - 마이그레이션 히스토리 검토

3. HTTP 클라이언트 (httpx) 관련 문제

   - TimeoutError 사용 시 주의사항:

     ```python
     # 잘못된 사용
     except httpx.TimeoutError:
         pass

     # 올바른 사용
     except httpx.ReadTimeout:
         pass
     ```

   - 타임아웃 설정:
     ```python
     async with httpx.AsyncClient() as client:
         response = await client.get(url, timeout=60.0)
     ```
   - 에러 처리 모범 사례:
     ```python
     try:
         async with httpx.AsyncClient() as client:
             response = await client.get(url, timeout=60.0)
     except httpx.ReadTimeout:
         raise HTTPException(status_code=504, detail="Request timed out")
     except httpx.RequestError as e:
         raise HTTPException(status_code=503, detail=str(e))
     ```

4. 스케줄러 문제

   - 스케줄러 상태 확인
   - 작업 실행 로그 검토
   - Node.js 플랫폼 서비스 연결 상태 확인

5. SQLAlchemy 관련 문제

   - func 사용 시 import 확인:

     ```python
     from sqlalchemy import func  # 필수 import

     # 올바른 사용
     config.last_run = func.now()
     ```

   - 세션 관리 주의사항:
     ```python
     async with AsyncSessionLocal() as db:
         try:
             # 데이터베이스 작업 수행
             await db.commit()
         except Exception:
             await db.rollback()
             raise
     ```

6. API 오류
   - 요청/응답 로그 확인
   - 에러 메시지 상세 분석
   - 미들웨어 설정 검토

## 개발 시 주의사항

1. HTTP 클라이언트 사용

   - httpx 라이브러리 사용 시 적절한 예외 처리
   - 타임아웃 설정 필수
   - 비동기 컨텍스트 매니저 활용

2. 데이터베이스 작업

   - SQLAlchemy 함수 및 유틸리티 올바른 import
   - 트랜잭션 관리 및 세션 처리
   - 비동기 작업 시 적절한 에러 처리

3. 스케줄러 작업
   - 작업 상태 모니터링
   - 적절한 로깅 설정
   - 오류 발생 시 재시도 메커니즘

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.
