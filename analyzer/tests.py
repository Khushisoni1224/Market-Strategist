
from datetime import date

from django.test import TestCase
from django.urls import reverse

from .models import MarketingPerformance
from .marketing_metrics import (
    calculate_marketing_summary,
    calculate_rate,
)


class MarketingMetricsTests(TestCase):

    def setUp(self):
        MarketingPerformance.objects.create(
            content_date=date(2026, 10, 1),
            content_id="TEST001",
            content_type="Image",
            product_name="Test Dress",
            reach=1000,
            impressions=2000,
            views=1500,
            likes=100,
            comments=20,
            saves=30,
            shares=10,
            profile_visits=100,
            clicks=80,
            enquiries=15,
            conversions=8,
        )

        MarketingPerformance.objects.create(
            content_date=date(2026, 10, 2),
            content_id="TEST002",
            content_type="Reel",
            product_name="Test Shirt",
            reach=500,
            impressions=1000,
            views=800,
            likes=50,
            comments=10,
            saves=20,
            shares=5,
            profile_visits=60,
            clicks=40,
            enquiries=8,
            conversions=4,
        )

    def test_record_count(self):
        summary = calculate_marketing_summary()
        self.assertEqual(summary["record_count"], 2)

    def test_total_reach(self):
        summary = calculate_marketing_summary()
        self.assertEqual(summary["total_reach"], 1500)

    def test_total_impressions(self):
        summary = calculate_marketing_summary()
        self.assertEqual(summary["total_impressions"], 3000)

    def test_total_engagement(self):
        summary = calculate_marketing_summary()
        self.assertEqual(summary["total_engagement"], 245)

    def test_engagement_rate(self):
        summary = calculate_marketing_summary()
        self.assertEqual(summary["engagement_rate"], 8.17)

    def test_click_through_rate(self):
        summary = calculate_marketing_summary()
        self.assertEqual(summary["click_through_rate"], 4.0)

    def test_conversion_rate(self):
        summary = calculate_marketing_summary()
        self.assertEqual(summary["conversion_rate"], 10.0)

    def test_rate_with_zero_denominator(self):
        self.assertIsNone(calculate_rate(10, 0))

    def test_rate_with_missing_value(self):
        self.assertIsNone(calculate_rate(None, 100))
        self.assertIsNone(calculate_rate(10, None))

    def test_missing_metrics_are_not_treated_as_zero(self):
        MarketingPerformance.objects.create(
            content_date=date(2026, 10, 3),
            content_id="TEST003",
            content_type="Image",
            product_name="Test Shoes",
            reach=None,
            impressions=None,
            likes=None,
            comments=None,
            saves=None,
            shares=None,
            clicks=None,
            conversions=None,
        )

        summary = calculate_marketing_summary()

        self.assertEqual(summary["record_count"], 3)
        self.assertIsNone(summary["engagement_rate"])
        self.assertIsNone(summary["click_through_rate"])
        self.assertIsNone(summary["conversion_rate"])

    def test_dashboard_loads(self):
        response = self.client.get(reverse("marketing_dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Marketing Performance Analytics")

    def test_product_filter(self):
        response = self.client.get(
            reverse("marketing_dashboard"),
            {"product": "Test Dress"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["summary"]["record_count"], 1)
        self.assertEqual(
            response.context["summary"]["total_reach"],
            1000,
        )


import io
from django.core.files.uploadedfile import SimpleUploadedFile

from .marketing_import import process_marketing_csv


class MarketingCSVImportTests(TestCase):

    def make_csv(self, content, filename="test_marketing.csv"):
        return SimpleUploadedFile(
            filename,
            content.encode("utf-8"),
            content_type="text/csv",
        )

    def valid_csv(self):
        return (
            "content_date,content_id,content_type,product_name,"
            "reach,impressions,views,likes,comments,saves,shares,"
            "profile_visits,clicks,enquiries,conversions\n"
            "2026-10-01,TEST001,Image,Test Dress,"
            "1000,2000,1500,100,20,30,10,100,80,15,8\n"
        )

    def test_valid_csv_import(self):
        uploaded_file = self.make_csv(self.valid_csv())

        result = process_marketing_csv(uploaded_file)

        self.assertEqual(result["total_rows"], 1)
        self.assertEqual(result["saved_count"], 1)
        self.assertEqual(result["invalid_count"], 0)

    
    def test_blank_metrics_are_saved_as_null(self):
        headers = [
            "content_date", "content_id", "content_type", "product_name",
            "reach", "impressions", "views", "likes", "comments",
            "saves", "shares", "profile_visits", "clicks", "enquiries",
            "conversions",
        ]
        row = [
            "2026-10-01", "TEST002", "Image", "Test Shoes",
            "", "", "", "", "", "", "", "", "", "", "",
        ]
        content = ",".join(headers) + "\n" + ",".join(row) + "\n"

        result = process_marketing_csv(self.make_csv(content))

        self.assertEqual(result["saved_count"], 1)
        self.assertEqual(result["invalid_count"], 0)

        record = MarketingPerformance.objects.get(content_id="TEST002")
        self.assertIsNone(record.reach)
        self.assertIsNone(record.impressions)
        self.assertIsNone(record.clicks)
        self.assertIsNone(record.conversions)

    def test_malformed_row_is_rejected(self):
        content = self.valid_csv() + "2026-10-02,TEST003,Image\n"
        result = process_marketing_csv(self.make_csv(content))

        self.assertEqual(result["invalid_count"], 1)

    def test_empty_file_is_rejected(self):
        uploaded_file = SimpleUploadedFile(
            "empty.csv", b"", content_type="text/csv"
        )

        with self.assertRaises(ValueError):
            process_marketing_csv(uploaded_file)

    def test_non_csv_file_is_rejected(self):
        uploaded_file = SimpleUploadedFile(
            "test.txt", b"sample content", content_type="text/plain"
        )

        with self.assertRaises(ValueError):
            process_marketing_csv(uploaded_file)


    def test_missing_required_column(self):
        content = (
            "content_date,content_id,content_type,reach\n"
            "2026-10-01,TEST001,Image,1000\n"
        )

        uploaded_file = self.make_csv(content)

        with self.assertRaisesMessage(
            ValueError, "Missing required columns"
        ):
            process_marketing_csv(uploaded_file)

    def test_invalid_date_is_rejected(self):
        content = self.valid_csv().replace(
            "2026-10-01", "not-a-date"
        )

        result = process_marketing_csv(self.make_csv(content))

        self.assertEqual(result["saved_count"], 0)
        self.assertEqual(result["invalid_count"], 1)

    def test_negative_metric_is_rejected(self):
        content = self.valid_csv().replace(
            "1000,2000,1500", "-1000,2000,1500"
        )

        result = process_marketing_csv(self.make_csv(content))

        self.assertEqual(result["saved_count"], 0)
        self.assertEqual(result["invalid_count"], 1)

    def test_non_numeric_metric_is_rejected(self):
        content = self.valid_csv().replace(
            "1000,2000,1500", "abc,2000,1500"
        )

        result = process_marketing_csv(self.make_csv(content))

        self.assertEqual(result["saved_count"], 0)
        self.assertEqual(result["invalid_count"], 1)

    
def test_blank_metrics_are_saved_as_null(self):
    content = (
        "content_date,content_id,content_type,product_name,"
        "reach,impressions,views,likes,comments,saves,shares,"
        "profile_visits,clicks,enquiries,conversions\n"
        "2026-10-01,TEST002,Image,Test Shoes,"
        ",,,,,,,,,,\n"
    )

    result = process_marketing_csv(self.make_csv(content))

    self.assertEqual(result["saved_count"], 1)
    self.assertEqual(result["invalid_count"], 0)

    record = MarketingPerformance.objects.get(
        content_id="TEST002"
    )

    self.assertIsNone(record.reach)
    self.assertIsNone(record.impressions)
    self.assertIsNone(record.clicks)
    self.assertIsNone(record.conversions)

    def test_malformed_row_is_rejected(self):
        content = (
            "content_date,content_id,content_type,product_name,"
            "reach,impressions,views,likes,comments,saves,shares,"
            "profile_visits,clicks,enquiries,conversions\n"
            "2026-10-01,TEST003,Image,Test Bag,1000,2000\n"
        )

        result = process_marketing_csv(self.make_csv(content))

        self.assertEqual(result["saved_count"], 0)
        self.assertEqual(result["invalid_count"], 1)

    def test_empty_file_is_rejected(self):
        uploaded_file = SimpleUploadedFile(
            "empty.csv",
            b"",
            content_type="text/csv",
        )

        with self.assertRaisesMessage(
            ValueError, "uploaded file is empty"
        ):
            process_marketing_csv(uploaded_file)

    def test_non_csv_file_is_rejected(self):
        uploaded_file = SimpleUploadedFile(
            "test.txt",
            b"some text",
            content_type="text/plain",
        )

        with self.assertRaisesMessage(
            ValueError, "Only CSV files are supported"
        ):
            process_marketing_csv(uploaded_file)

