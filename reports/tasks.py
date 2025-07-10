from __future__ import annotations

from celery import shared_task


@shared_task  # type: ignore
def debug_celery_task() -> str:
    print("Celery is working!")
    return "Success"
