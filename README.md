## 프로젝트 구조

```
fastapi_webhooks-app/
├── api
│   ├── __init__.py
│   ├── platform
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── repositories.py
│   │   ├── routers.py
│   │   ├── schemas.py
│   │   └── services.py
├── config
│   ├── __init__.py
│   ├── db.py
│   └── settings.py
├── scheduler
│   ├── __init__.py
│   └── tasks.py
├── migrations
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
├── pyproject.toml
├── README.md
├── run_app.sh
└── pyproject.toml
```

### 0. 참고

- https://www.gdsanadevlog.com/planguages/real-python-fastapi-%ED%92%80%EC%8A%A4%ED%83%9D-%EB%B8%94%EB%A1%9C%EA%B7%B8-%EA%B0%9C%EB%B0%9C%ED%95%98%EA%B8%B0-%ED%94%84%EB%A1%9C%EC%A0%9D%ED%8A%B8-%EA%B5%AC%EC%A1%B0-%EB%A7%8C%EB%93%A4%EA%B8%B0/

### 1. pyenv 설치

### 2. poetry 설치

- poetry lock

### 3. alembic 설치(로컬에서)

- poetry add alembic
- poetry run alembic init -t async migrations
- poetry run alembic upgrade head

### 4. alembic data migration

### 5. git remote 변경 (rename)

## Usage version 1

```
export PYTHONPATH=.
uvicorn main:app --reload --host 0.0.0.0 --port 8080
```

## Usage version 2

```
docker compose up -d --build
```

## Usage version 3

1. Run the application:

   ```
   ./run_app.sh
   ```

2. Access the API documentation at `http://localhost:8080/docs`.

## API Endpoints

- **Create Platform**: `POST /api/v1/platforms/`
- **Read Platforms**: `GET /api/v1/platforms/`
- **Read Platform by ID**: `GET /api/v1/platforms/{platform_id}`
- **Update Platform**: `PUT /api/v1/platforms/{platform_id}`
- **Delete Platform**: `DELETE /api/v1/platforms/{platform_id}`
- **Run Task**: `POST /api/run/:param` (Accepts JSON body with active platform names and type)

## Scheduler

The application uses APScheduler to read all active platforms every minute.

## License

This project is licensed under the MIT License.
