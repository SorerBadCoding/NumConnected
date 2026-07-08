from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone

from core.models import TimeStampedModel


class Priority(models.TextChoices):
    LOW = "low", "Low"
    MEDIUM = "medium", "Medium"
    HIGH = "high", "High"


class Status(models.TextChoices):
    NOT_STARTED = "not_started", "Not Started"
    IN_PROGRESS = "in_progress", "In Progress"
    COMPLETED = "completed", "Completed"


class Assignment(TimeStampedModel):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="assignments"
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    course = models.CharField(
        max_length=120, blank=True, help_text="e.g. CS101, Calculus II"
    )
    due_date = models.DateTimeField()
    priority = models.CharField(
        max_length=10, choices=Priority.choices, default=Priority.MEDIUM
    )
    status = models.CharField(
        max_length=15, choices=Status.choices, default=Status.NOT_STARTED
    )
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["due_date"]
        indexes = [
            models.Index(fields=["owner", "status"]),
            models.Index(fields=["due_date"]),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("assignments:detail", kwargs={"pk": self.pk})

    def save(self, *args, **kwargs):
        if self.status == Status.COMPLETED and self.completed_at is None:
            self.completed_at = timezone.now()
        elif self.status != Status.COMPLETED:
            self.completed_at = None
        super().save(*args, **kwargs)

    @property
    def is_completed(self):
        return self.status == Status.COMPLETED

    @property
    def is_overdue(self):
        return not self.is_completed and self.due_date < timezone.now()

    @property
    def days_until_due(self):
        delta = self.due_date.date() - timezone.now().date()
        return delta.days
