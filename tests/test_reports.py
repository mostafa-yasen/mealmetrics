import os

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase

from reports.models import Report
from reports.utils import generate_signed_url


class ReportFlowTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="pass")
        self.client.force_authenticate(self.user)  # type: ignore

    def test_create_report(self):
        url = reverse("report-create")
        response = self.client.post(url)
        self.assertEqual(response.status_code, 201)
        self.assertIn("id", response.data)  # type: ignore

    def test_poll_report_status(self):
        report = Report.objects.create(user=self.user)
        url = reverse("report-detail", args=[report.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "PENDING")  # type: ignore

    def test_get_signed_url_when_completed(self):
        # Simulate completed report
        report = Report.objects.create(
            user=self.user,
            status=Report.Status.COMPLETED,
            file_path="reports/fakefile.xlsx",
        )
        url = reverse("report-detail", args=[report.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("download_url", response.data)  # type: ignore

    def test_download_file_with_valid_token(self):
        path = "test.xlsx"
        # Create a fake file for test
        with open("media/" + path, "wb") as f:
            f.write(b"dummy report content")

        token = generate_signed_url(path).split("/download/")[1].split("?")[0]
        download_url = reverse("report-download", args=[token])

        response = self.client.get(download_url)
        self.assertEqual(response.status_code, 200)

        retrieved_content = b"".join(response.streaming_content)  # type: ignore
        self.assertEqual(retrieved_content, b"dummy report content")

        os.remove("media/" + path)

    def test_download_file_with_invalid_token(self):
        url = reverse("report-download", args=["invalid-token"])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
