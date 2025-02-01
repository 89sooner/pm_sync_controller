# ./Dockerfile
FROM python:3.12-slim

# 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# NVM 설치 및 Node.js 20.12.0 설치
ENV NVM_DIR /root/.nvm
ENV NODE_VERSION 20.12.0

RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash \
    && . $NVM_DIR/nvm.sh \
    && nvm install $NODE_VERSION \
    && nvm alias default $NODE_VERSION \
    && nvm use default

# PATH 환경변수 설정
ENV PATH $NVM_DIR/versions/node/v$NODE_VERSION/bin:$PATH

# Node.js 및 npm 버전 확인
RUN node --version && npm --version

# 작업 디렉토리 설정
WORKDIR /app


# Poetry 및 프로젝트 의존성 설치
COPY pyproject.toml poetry.lock ./
RUN pip install poetry
RUN poetry install --no-interaction --no-root

COPY . .

ENV PYTHONPATH=${PYTHONPATH}
ENV PORT=${PORT}
ENV NODE_APP_NAME=${NODE_APP_NAME}

EXPOSE ${PORT}

CMD ["sh", "-c", "poetry run alembic upgrade head && poetry run uvicorn app:app --host 0.0.0.0 --port ${PORT}"]
