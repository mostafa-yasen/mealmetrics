# MealsMetrics

**MealsMetrics** is a scalable Django-based reporting system that asynchronously generates detailed nutrition and food log reports. It supports user-based activity tracking, Excel report generation, secure downloads, and background processing using Celery + Redis.

---

## Features

- Users can request nutrition reports via a secure API
- Reports are generated asynchronously using Celery
- Excel reports include:
  - Food log trends over time
  - Most frequently logged items
  - Category-wise breakdowns
- Signed, time-limited download URLs
- Full test coverage using `pytest`
- Resource-isolated, production-ready Docker setup

---

## Architecture & Flow

```text
Client
  │
  ├── POST /api/reports/ ───────> Django API
  │                                 │
  │                                 └── Create Report (status=PENDING)
  │                                       │
  │
  │                                Celery Worker (async)
  │                                 │  - Load data from DB
  │                                 │  - Generate Excel file
  │                                 │  - Save file path + update status
  │
  └── GET /api/reports/<id>/ ─────▶ Returns status + download URL (if ready)
                                    │
                                    /api/reports/download/<signed-token>
                                    │
                                    └── Validates + streams file
```

### Tools
- Backend: Django + DRF
- Async: Celery worker + Redis broker
- DB: PostgreSQL
- Storage: Files saved locally (`media/reports/`)
- Security: Signed download URLs via `itsdangerous`


## How to Run (Locally with Docker)

### 1. Clone the repo

```bash
git clone https://github.com/<your-username>/mealsmetrics.git
cd mealsmetrics
```

### 2. Create your `.env` file

You can find starter file as `.env.example`.

```
DJANGO_SECRET_KEY=A_VERY_SECRET_KEY
DJANGO_DEBUG=True
POSTGRES_DB=mealsmetrics
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=db
POSTGRES_PORT=5432
REDIS_URL=redis://redis:6379/0
```

### 3. Start services

```bash
docker compose --compatibility up --build
```

The `--compatibility` flag to make resource limits work with docker compose.

### 4. Create superuser

```bash
docker compose exec web python manage.py createsuperuser
```

### 5. Seed with test data

```bash
docker compose exec web python manage.py seed_food_logs --users 100 --logs 5000
```

### 6. Access locally

+ API: http://localhost:8000/api/reports/
+ Admin: http://localhost:8000/admin/


## Celery Task Behavior

- Asynchronous report generation
- Retries up to 3 times on failure
- Timeouts after 1 minute
- Final status set to COMPLETED or FAILED

## Secure Downloads

- Signed download links expire after 5 minutes
- Download endpoint validates the token and file path

## Performance & Resource Management

### Query Optimization

- Uses `.values()`, `.values_list()` and `annotate()` instead of loading full model objects
- Aggregations and counts performed in the database layer

### Docker Resource Limits

Each service is isolated with memory & CPU caps via Docker Compose:

```yaml
deploy:
  resources:
    limits:
      cpus: '0.5'
      memory: 512M
```
Use docker compose --compatibility up to enforce limits.

## Running Tests

```bash
docker compose exec web pytest
```

## CI Pipeline

- GitHub Actions runs on push/PR to main
- Tests run inside isolated services: PostgreSQL + Redis
- uv is used for dependency management

## Roadmap

+ [ ] Add user-specified filters (date range, category)
+ [ ] Schedule recurring reports (weekly/monthly)

## Developer Notes

### Local Dev Commands
```bash
uv pip install --system      # Install from lock file
pre-commit run --all-files   # Run all code checks
```

## License

MIT License
