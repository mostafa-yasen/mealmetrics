from django.urls import path

from .views import ReportCreateView, ReportDetailView

urlpatterns = [
    path("reports/", ReportCreateView.as_view(), name="report-create"),
    path("reports/<uuid:id>/", ReportDetailView.as_view(), name="report-detail"),
]
