# ./Dockerfile
FROM python:3.12.8

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN pip install poetry
RUN poetry install --no-interaction --no-root

COPY . .

ENV PYTHONPATH=${PYTHONPATH}
ENV PORT=${PORT}

EXPOSE ${PORT}

CMD ["sh", "-c", "poetry run alembic upgrade head && poetry run uvicorn app:app --host 0.0.0.0 --port ${PORT}"]
