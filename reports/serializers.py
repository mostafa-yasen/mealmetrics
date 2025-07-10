from __future__ import annotations

from rest_framework import serializers  # type: ignore[import-untyped]

from .models import Report


class ReportCreateSerializer(serializers.ModelSerializer):  # type: ignore[misc]
    class Meta:
        model = Report
        fields: list[str] = []

    def create(self, validated_data: dict[str, str]) -> Report:
        user = self.context["request"].user
        return Report.objects.create(user=user)


class ReportDetailSerializer(serializers.ModelSerializer):  # type: ignore[misc]
    class Meta:
        model = Report
        fields = (
            "id",
            "status",
            "created_at",
            "completed_at",
            "file_path",
        )
