# syntax=docker/dockerfile:1
FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN pip install --no-cache-dir uv

ENV UV_PROJECT_ENVIRONMENT="/usr/local/"
RUN uv sync --locked

COPY . .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
