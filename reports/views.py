from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any

from django.conf import settings
from django.http import FileResponse, Http404
from rest_framework import generics, permissions, status  # type: ignore[import-untyped]
from rest_framework.exceptions import NotFound  # type: ignore[import-untyped]
from rest_framework.permissions import AllowAny  # type: ignore[import-untyped]
from rest_framework.response import Response  # type: ignore[import-untyped]
from rest_framework.views import APIView  # type: ignore[import-untyped]

from reports.models import Report
from reports.tasks import generate_report
from reports.utils import generate_signed_url, verify_signed_url

from .serializers import ReportCreateSerializer, ReportDetailSerializer

if TYPE_CHECKING:
    from rest_framework.request import Request  # type: ignore[import-untyped]


class ReportCreateView(generics.CreateAPIView):  # type: ignore[misc]
    serializer_class = ReportCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer: ReportCreateSerializer) -> None:
        self.report: Report = serializer.save(user=self.request.user)
        generate_report.delay(str(self.report.id))

    def create(
        self, request: Request, *args: list[str], **kwargs: dict[str, Any]
    ) -> Response:
        existing = Report.objects.filter(
            user=self.request.user,
            status__in=[Report.Status.PENDING, Report.Status.PROCESSING],
        ).first()

        if existing:
            return Response(
                {"detail": "You already have a report being generated."}, status=400
            )

        super().create(request, *args, **kwargs)
        return Response(
            {"id": str(self.report.id), "status": self.report.status},
            status=status.HTTP_201_CREATED,
        )


class ReportDetailView(generics.RetrieveAPIView):  # type: ignore[misc]
    serializer_class = ReportDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"
    queryset = Report.objects.all()

    def retrieve(
        self, request: Request, *args: list[str], **kwargs: dict[str, Any]
    ) -> Response:
        report = self.get_object()

        if report.user != request.user:
            raise NotFound("Report not found")

        data = ReportDetailSerializer(report).data
        if report.status == Report.Status.COMPLETED:
            data["download_url"] = generate_signed_url(report.file_path)

        return Response(data)


class ReportDownloadView(APIView):  # type: ignore[misc]
    permission_classes = [AllowAny]

    def get(self, request: Request, token: str) -> FileResponse:
        path = verify_signed_url(token, max_age=int(request.GET.get("expires_in", 300)))
        if not path:
            raise Http404("Invalid or expired token")

        full_path = os.path.join(settings.BASE_DIR, "media", path)
        if not os.path.exists(full_path):
            raise Http404("File not found")

        return FileResponse(open(full_path, "rb"), as_attachment=True)
