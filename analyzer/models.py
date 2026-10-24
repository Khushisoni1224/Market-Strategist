
from django.db import models


class FeedbackImport(models.Model):
    STATUS_CHOICES = [
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    filename = models.CharField(max_length=255)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="processing",
    )

    total_rows = models.PositiveIntegerField(default=0)
    valid_count = models.PositiveIntegerField(default=0)
    invalid_count = models.PositiveIntegerField(default=0)
    analyzed_count = models.PositiveIntegerField(default=0)

    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.filename} - {self.status}"

    class Meta:
        ordering = ["-created_at"]


class CustomerFeedback(models.Model):
    import_record = models.ForeignKey(
        FeedbackImport,
        on_delete=models.CASCADE,
        related_name="feedback_records",
    )

    row_number = models.PositiveIntegerField()
    review_text = models.TextField()
    sentiment = models.CharField(max_length=20)
    sentiment_score = models.FloatField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review {self.row_number} - {self.sentiment}"

    class Meta:
        ordering = ["row_number"]



class MarketingPerformance(models.Model):
    content_date = models.DateField()
    content_id = models.CharField(max_length=100)
    content_type = models.CharField(max_length=50)
    product_name = models.CharField(max_length=255)

    reach = models.PositiveIntegerField(null=True, blank=True)
    impressions = models.PositiveIntegerField(null=True, blank=True)
    views = models.PositiveIntegerField(null=True, blank=True)

    likes = models.PositiveIntegerField(null=True, blank=True)
    comments = models.PositiveIntegerField(null=True, blank=True)
    saves = models.PositiveIntegerField(null=True, blank=True)
    shares = models.PositiveIntegerField(null=True, blank=True)

    profile_visits = models.PositiveIntegerField(null=True, blank=True)
    clicks = models.PositiveIntegerField(null=True, blank=True)
    enquiries = models.PositiveIntegerField(null=True, blank=True)
    conversions = models.PositiveIntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.content_id} - {self.product_name}"

    class Meta:
        ordering = ["-content_date", "content_id"]
