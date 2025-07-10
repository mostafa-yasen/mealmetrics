from __future__ import annotations

import logging
import os
import time
from datetime import date, timedelta

import pandas as pd  # type: ignore[import-untyped]
from celery import shared_task  # type: ignore[import-untyped]
from celery.exceptions import MaxRetriesExceededError  # type: ignore[import-untyped]
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from .models import FoodLog, Report

_logger = logging.getLogger(__name__)


@shared_task  # type: ignore
def debug_celery_task() -> str:
    """A simple task to test if Celery is working."""
    _logger.debug("Celery is working!")
    return "Success"


@shared_task(rate_limit="10/m", bind=True, max_retries=3, default_retry_delay=1 * 60)  # type: ignore[misc]
def generate_report(self, report_id: str) -> None:  # type: ignore
    start = time.time()
    _logger.info(f"Generating report for ID: {report_id}")
    try:
        report = Report.objects.get(id=report_id)
        report.status = Report.Status.PROCESSING
        report.save()

        users_with_logs = User.objects.filter(food_logs__isnull=False).distinct()
        total_users = users_with_logs.count()

        unique_foods = FoodLog.objects.values_list("food_name", flat=True).distinct()
        total_unique_foods = unique_foods.count()

        today = date.today()
        start_date = today - timedelta(days=29)

        date_counts = (
            FoodLog.objects.filter(date_logged__range=(start_date, today))
            .values("date_logged")
            .annotate(count=models.Count("id"))
            .order_by("date_logged")
        )
        trend_df = pd.DataFrame(date_counts)

        food_counts = (
            FoodLog.objects.values("food_name")
            .annotate(count=models.Count("id"))
            .order_by("-count")[:10]
        )
        top_foods_df = pd.DataFrame(food_counts)

        category_counts = (
            FoodLog.objects.values("category")
            .annotate(count=models.Count("id"))
            .order_by("-count")
        )
        category_df = pd.DataFrame(category_counts)

        output_dir = os.path.join(settings.BASE_DIR, "media")
        os.makedirs(output_dir, exist_ok=True)

        filename = f"report_{report.id}.xlsx"
        file_path = os.path.join(output_dir, filename)

        with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
            pd.DataFrame(
                [{"Total Users": total_users, "Unique Food Items": total_unique_foods}]
            ).to_excel(writer, index=False, sheet_name="Summary")

            trend_df.rename(
                columns={"date_logged": "Date", "count": "Entries"}
            ).to_excel(writer, index=False, sheet_name="Trends")
            top_foods_df.rename(
                columns={"food_name": "Food", "count": "Count"}
            ).to_excel(writer, index=False, sheet_name="Top Foods")
            category_df.rename(
                columns={"category": "Category", "count": "Count"}
            ).to_excel(writer, index=False, sheet_name="By Category")

        report.status = Report.Status.COMPLETED
        report.file_path = filename
        report.completed_at = timezone.now()
        report.save()
        msg = f"✅ Report generated in {time.time() - start} seconds"
        _logger.info(msg)
    except Report.DoesNotExist:
        msg = f"Report {report_id} does not exist."
        _logger.error(msg)

    except Exception as e:
        _logger.exception(f"Failed to generate report {report_id}: {e}")
        try:
            self.retry(
                exc=e,
            )
        except MaxRetriesExceededError:
            report = Report.objects.get(id=report_id)
            if report:
                report.status = Report.Status.FAILED
                report.error = str(e)
                report.save()
