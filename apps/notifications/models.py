from django.conf import settings
from django.db import models

from core.models import TimeStampedModel


class NotificationType(models.TextChoices):
    ASSIGNMENT_DUE = "assignment_due", "Assignment Due"
    NEW_ANNOUNCEMENT = "new_announcement", "New Announcement"
    EVENT_REMINDER = "event_reminder", "Event Reminder"
    NEW_RESOURCE = "new_resource", "New Study Resource"
    ACCOUNT_UPDATE = "account_update", "Account Update"


NOTIFICATION_ICONS = {
    NotificationType.ASSIGNMENT_DUE: "bi-alarm",
    NotificationType.NEW_ANNOUNCEMENT: "bi-megaphone",
    NotificationType.EVENT_REMINDER: "bi-calendar-event",
    NotificationType.NEW_RESOURCE: "bi-folder2-open",
    NotificationType.ACCOUNT_UPDATE: "bi-person-gear",
}


class Notification(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications"
    )
    notification_type = models.CharField(max_length=30, choices=NotificationType.choices)
    title = models.CharField(max_length=200)
    message = models.CharField(max_length=255, blank=True)
    url = models.CharField(max_length=255, blank=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_read"]),
            models.Index(fields=["user", "-created_at"]),
        ]

    def __str__(self):
        return self.title

    @property
    def icon(self):
        return NOTIFICATION_ICONS.get(self.notification_type, "bi-bell")
