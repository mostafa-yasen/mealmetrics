from __future__ import annotations

import logging
import os
from datetime import timedelta

import pandas as pd  # type: ignore[import-untyped]
from celery import shared_task  # type: ignore[import-untyped]
from django.conf import settings
from django.utils import timezone

from .models import Report

_logger = logging.getLogger(__name__)


@shared_task  # type: ignore
def debug_celery_task() -> str:
    """A simple task to test if Celery is working."""
    _logger.debug("Celery is working!")
    return "Success"


@shared_task  # type: ignore
def generate_report(report_id: str) -> None:
    """Generate a report based on the provided report ID."""
    from django.contrib.auth.models import User  # noqa: PLC0415

    try:
        report = Report.objects.get(id=report_id)
        report.status = Report.Status.PROCESSING
        report.save()

        # Mock data
        users = User.objects.filter(reports__isnull=False).distinct()
        total_users = users.count()

        # Simulated food log data
        total_food_items = 10000
        food_logs_per_day = [
            {
                "date": (timezone.now() - timedelta(days=i)).strftime("%Y-%m-%d"),
                "count": i * 13 % 50,
            }
            for i in range(30)
        ]
        most_frequent_foods = [
            {"food": f"Food {i}", "count": 100 - i * 3} for i in range(10)
        ]

        # Create a Pandas Excel writer
        df1 = pd.DataFrame(
            [{"Total Users": total_users, "Total Food Items": total_food_items}]
        )
        df2 = pd.DataFrame(food_logs_per_day)
        df3 = pd.DataFrame(most_frequent_foods)

        output_dir = os.path.join(settings.BASE_DIR, "media")  # "/reports"
        os.makedirs(output_dir, exist_ok=True)
        filename = f"report_{report.id}.xlsx"
        file_path = os.path.join(output_dir, filename)

        with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
            df1.to_excel(writer, index=False, sheet_name="Summary")
            df2.to_excel(writer, index=False, sheet_name="Activity Trends")
            df3.to_excel(writer, index=False, sheet_name="Top Foods")

        report.status = Report.Status.COMPLETED
        report.completed_at = timezone.now()
        report.file_path = filename
        report.save()

    except Exception as e:
        report.status = Report.Status.FAILED
        report.error = str(e)
        report.save()
