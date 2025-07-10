from django.contrib import admin

from .models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "created_at", "completed_at")
    list_filter = ("status", "created_at")
    search_fields = ("user__username", "id")
    readonly_fields = ("id", "created_at", "completed_at", "file_path", "error")
