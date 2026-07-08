from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from assignments.models import Assignment, Status
from notifications.models import Notification, NotificationType


class Command(BaseCommand):
    help = (
        "Create 'assignment due soon' notifications for assignments due within "
        "the next 24 hours. Intended to be run periodically (e.g. hourly via "
        "cron or a task scheduler) since this project has no background task "
        "runner installed."
    )

    def handle(self, *args, **options):
        now = timezone.now()
        window_end = now + timedelta(hours=24)
        due_soon = Assignment.objects.filter(
            due_date__gte=now, due_date__lte=window_end
        ).exclude(status=Status.COMPLETED)

        created = 0
        for assignment in due_soon:
            already_notified = Notification.objects.filter(
                user=assignment.owner,
                notification_type=NotificationType.ASSIGNMENT_DUE,
                url=assignment.get_absolute_url(),
                created_at__gte=now - timedelta(hours=24),
            ).exists()
            if already_notified:
                continue

            Notification.objects.create(
                user=assignment.owner,
                notification_type=NotificationType.ASSIGNMENT_DUE,
                title=f'"{assignment.title}" is due soon',
                message=f"Due {assignment.due_date:%b %d, %Y at %I:%M %p}",
                url=assignment.get_absolute_url(),
            )
            created += 1

        self.stdout.write(self.style.SUCCESS(f"Created {created} due-date reminder notification(s)."))
