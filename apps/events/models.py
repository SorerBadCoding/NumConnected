from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone

from core.models import TimeStampedModel


class EventCategory(models.TextChoices):
    ACADEMIC = "academic", "Academic"
    SOCIAL = "social", "Social"
    SPORTS = "sports", "Sports"
    CAREER = "career", "Career"
    WORKSHOP = "workshop", "Workshop"
    OTHER = "other", "Other"


class Event(TimeStampedModel):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(
        max_length=20, choices=EventCategory.choices, default=EventCategory.OTHER
    )
    location = models.CharField(max_length=200)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="organized_events",
        limit_choices_to={"is_staff": True},
    )
    image = models.ImageField(upload_to="events/", blank=True, null=True)
    attendees = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name="attending_events"
    )

    class Meta:
        ordering = ["start_datetime"]
        indexes = [
            models.Index(fields=["start_datetime"]),
            models.Index(fields=["category"]),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("events:detail", kwargs={"pk": self.pk})

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.start_datetime and self.end_datetime and self.end_datetime <= self.start_datetime:
            raise ValidationError({"end_datetime": "End time must be after the start time."})

    @property
    def is_past(self):
        return self.end_datetime < timezone.now()

    @property
    def is_ongoing(self):
        now = timezone.now()
        return self.start_datetime <= now <= self.end_datetime

    @property
    def is_upcoming(self):
        return self.start_datetime > timezone.now()

    @property
    def attendee_count(self):
        return self.attendees.count()
