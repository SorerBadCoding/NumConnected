from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone

from core.models import TimeStampedModel


class AnnouncementCategory(models.TextChoices):
    GENERAL = "general", "General"
    ACADEMIC = "academic", "Academic"
    EVENT = "event", "Event"
    URGENT = "urgent", "Urgent"
    CAREER = "career", "Career"


class Announcement(TimeStampedModel):
    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.CharField(
        max_length=20, choices=AnnouncementCategory.choices, default=AnnouncementCategory.GENERAL
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="announcements",
        limit_choices_to={"is_staff": True},
    )
    is_pinned = models.BooleanField(default=False)
    publish_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-is_pinned", "-publish_at"]
        indexes = [
            models.Index(fields=["category"]),
            models.Index(fields=["-publish_at"]),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("announcements:detail", kwargs={"pk": self.pk})

    @property
    def is_expired(self):
        return bool(self.expires_at and self.expires_at < timezone.now())

    @property
    def is_published(self):
        return self.publish_at <= timezone.now()

    @property
    def is_active(self):
        return self.is_published and not self.is_expired
