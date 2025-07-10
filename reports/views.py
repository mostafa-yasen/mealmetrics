from __future__ import annotations

from rest_framework import generics, permissions
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from reports.models import Report

from .serializers import ReportCreateSerializer, ReportDetailSerializer


class ReportCreateView(generics.CreateAPIView):
    serializer_class = ReportCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        report = serializer.save(user=self.request.user)

        # TODO: implement report generation async task
        # generate_report.delay(str(report.id))
        return Response(report, status=201)


class ReportDetailView(generics.RetrieveAPIView):
    serializer_class = ReportDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"
    queryset = Report.objects.all()

    def retrieve(self, request, *args, **kwargs):
        report = self.get_object()

        if report.user != request.user:
            raise NotFound("Report not found")

        data = ReportDetailSerializer(report).data
        if report.status == Report.Status.COMPLETED:
            # TODO: implement signed URL generation for file download
            # generate_signed_url(report.file_path)
            data["download_url"] = "Download URL Placeholder"

        return Response(data)
