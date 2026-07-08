from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import User
from announcements.models import Announcement
from events.models import Event
from resources_app.models import Resource

from .models import Notification, NotificationType


def _notify_all_students(notification_type, title, message, url):
    students = User.objects.filter(is_staff=False, is_active=True)
    Notification.objects.bulk_create(
        [
            Notification(
                user=student,
                notification_type=notification_type,
                title=title,
                message=message,
                url=url,
            )
            for student in students
        ]
    )


@receiver(post_save, sender=Announcement)
def notify_new_announcement(sender, instance, created, **kwargs):
    # Scheduled announcements (publish_at in the future) shouldn't notify
    # students before they're actually visible in the announcements list.
    if created and instance.is_active:
        _notify_all_students(
            NotificationType.NEW_ANNOUNCEMENT,
            f"New announcement: {instance.title}",
            instance.content[:150],
            instance.get_absolute_url(),
        )


@receiver(post_save, sender=Event)
def notify_new_event(sender, instance, created, **kwargs):
    if created:
        _notify_all_students(
            NotificationType.EVENT_REMINDER,
            f"New event: {instance.title}",
            f"{instance.location} · {instance.start_datetime:%b %d, %Y}",
            instance.get_absolute_url(),
        )


@receiver(post_save, sender=Resource)
def notify_new_resource(sender, instance, created, **kwargs):
    if created:
        _notify_all_students(
            NotificationType.NEW_RESOURCE,
            f"New resource: {instance.title}",
            instance.description[:150],
            instance.get_absolute_url(),
        )
