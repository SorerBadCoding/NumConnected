from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone

from core.models import TimeStampedModel


class FeedbackType(models.TextChoices):
    SUGGESTION = "suggestion", "Suggestion"
    BUG = "bug", "Bug Report"
    FEATURE_REQUEST = "feature_request", "Feature Request"
    RATING = "rating", "Platform Rating"


class FeedbackStatus(models.TextChoices):
    OPEN = "open", "Open"
    IN_PROGRESS = "in_progress", "In Progress"
    RESOLVED = "resolved", "Resolved"
    ARCHIVED = "archived", "Archived"


STATUS_BADGE_CLASSES = {
    FeedbackStatus.OPEN: "badge-soft-info",
    FeedbackStatus.IN_PROGRESS: "badge-soft-warning",
    FeedbackStatus.RESOLVED: "badge-soft-success",
    FeedbackStatus.ARCHIVED: "badge-soft-muted",
}


class Feedback(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="feedback_submissions"
    )
    feedback_type = models.CharField(max_length=20, choices=FeedbackType.choices)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    rating = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    status = models.CharField(max_length=20, choices=FeedbackStatus.choices, default=FeedbackStatus.OPEN)
    admin_reply = models.TextField(blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["status"])]

    def __str__(self):
        return self.subject

    def get_absolute_url(self):
        return reverse("feedback:detail", kwargs={"pk": self.pk})

    @property
    def status_badge_class(self):
        return STATUS_BADGE_CLASSES.get(self.status, "badge-soft-muted")

    @property
    def rating_stars(self):
        """Range object for the template to loop over when rendering star
        icons, since Django templates have no built-in numeric range."""
        return range(self.rating or 0)

    def save(self, *args, **kwargs):
        if self.status == FeedbackStatus.RESOLVED and self.resolved_at is None:
            self.resolved_at = timezone.now()
        elif self.status != FeedbackStatus.RESOLVED:
            self.resolved_at = None
        super().save(*args, **kwargs)
