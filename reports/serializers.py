from rest_framework import serializers

from .models import Report


class ReportCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = []

    def create(self, validated_data):
        user = self.context["request"].user
        return Report.objects.create(user=user)


class ReportDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = (
            "id",
            "status",
            "created_at",
            "completed_at",
            "file_path",
        )
