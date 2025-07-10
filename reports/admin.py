from django.contrib import admin

from .models import FoodLog, Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin[Report]):
    list_display = ("id", "user", "status", "created_at", "completed_at")
    list_filter = ("status", "created_at", "user")
    search_fields = ("user__username", "id")
    readonly_fields = ("id", "created_at", "completed_at", "file_path", "error")
    ordering = ("-created_at",)


@admin.register(FoodLog)
class FoodLogAdmin(admin.ModelAdmin[FoodLog]):
    list_display = ("id", "user", "food_name", "category", "date_logged")
    list_filter = ("category", "date_logged")
    search_fields = ("user__username", "food_name")
    readonly_fields = ("id", "date_logged")
    raw_id_fields = ("user",)
