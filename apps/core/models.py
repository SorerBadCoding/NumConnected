from django.conf import settings
from django.db import models


class TimeStampedModel(models.Model):
    """Abstract base providing created/updated timestamps for every model."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]


class ActivityVerb(models.TextChoices):
    ASSIGNMENT_CREATED = "assignment_created", "created an assignment"
    ASSIGNMENT_COMPLETED = "assignment_completed", "completed an assignment"
    RESOURCE_DOWNLOADED = "resource_downloaded", "downloaded a resource"
    CHAT_MESSAGE = "chat_message", "chatted with the AI Assistant"
    POST_CREATED = "post_created", "posted in the discussion board"
    EVENT_JOINED = "event_joined", "joined an event"
    PROFILE_UPDATED = "profile_updated", "updated their profile"


class ActivityLog(TimeStampedModel):
    """Lightweight per-user activity feed, powering the dashboard's Recent
    Activity widget and the analytics study-streak calculation."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="activity_logs"
    )
    verb = models.CharField(max_length=30, choices=ActivityVerb.choices)
    description = models.CharField(max_length=255)
    icon = models.CharField(max_length=40, default="bi-circle-fill")
    url = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "-created_at"])]

    def __str__(self):
        return f"{self.user}: {self.description}"

    @classmethod
    def log(cls, user, verb, description, icon="bi-circle-fill", url=""):
        return cls.objects.create(user=user, verb=verb, description=description, icon=icon, url=url)


class ContactMessage(TimeStampedModel):
    """Submissions from the public landing page's contact form."""

    name = models.CharField(max_length=150)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.subject} ({self.email})"
