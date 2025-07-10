import uuid

from django.contrib.auth.models import User
from django.db import models


class Report(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING"
        PROCESSING = "PROCESSING"
        COMPLETED = "COMPLETED"
        FAILED = "FAILED"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reports")
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    file_path = models.CharField(max_length=512, null=True, blank=True)
    error = models.TextField(null=True, blank=True)

    def __str__(self) -> str:
        return f"Report {self.id} ({self.status})"


class FoodLog(models.Model):
    FOOD_CATEGORIES = [
        ("fruit", "Fruit"),
        ("vegetable", "Vegetable"),
        ("dairy", "Dairy"),
        ("protein", "Protein"),
        ("snack", "Snack"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="food_logs")
    food_name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=FOOD_CATEGORIES)
    date_logged = models.DateField()

    class Meta:
        indexes = [
            models.Index(fields=["date_logged"]),
            models.Index(fields=["category"]),
        ]

    def __str__(self):
        return f"{self.food_name} ({self.category}) - {self.user.username}"
