import os

from celery import Celery  # type: ignore[import-untyped]

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mealsmetrics.settings")

app = Celery("mealsmetrics")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
