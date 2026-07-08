from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from assignments.models import Assignment, Priority, Status
from core.models import ActivityLog, ActivityVerb
from resources_app.models import ResourceDownloadLog, Resource, ResourceCategory

User = get_user_model()


class AnalyticsViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="analytics", password="pw123456", email="an@x.edu")
        self.client.login(username="analytics", password="pw123456")

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("dashboard:analytics"))
        self.assertEqual(response.status_code, 302)

    def test_completed_and_pending_counts(self):
        now = timezone.now()
        Assignment.objects.create(owner=self.user, title="Done", due_date=now, status=Status.COMPLETED, completed_at=now)
        Assignment.objects.create(owner=self.user, title="Todo", due_date=now, status=Status.NOT_STARTED)

        response = self.client.get(reverse("dashboard:analytics"))
        self.assertEqual(response.context["completed_count"], 1)
        self.assertEqual(response.context["pending_count"], 1)

    def test_on_time_vs_late_breakdown(self):
        due = timezone.now()
        on_time = Assignment.objects.create(owner=self.user, title="OnTime", due_date=due, status=Status.NOT_STARTED)
        on_time.status = Status.COMPLETED
        on_time.completed_at = due - timezone.timedelta(hours=1)
        on_time.save()

        late = Assignment.objects.create(owner=self.user, title="Late", due_date=due, status=Status.NOT_STARTED)
        late.status = Status.COMPLETED
        late.completed_at = due + timezone.timedelta(hours=1)
        late.save()

        response = self.client.get(reverse("dashboard:analytics"))
        self.assertEqual(response.context["on_time_count"], 1)
        self.assertEqual(response.context["late_count"], 1)

    def test_study_streak_counts_consecutive_days(self):
        today = timezone.localdate()
        ActivityLog.objects.create(user=self.user, verb=ActivityVerb.CHAT_MESSAGE, description="today")
        yesterday_log = ActivityLog.objects.create(user=self.user, verb=ActivityVerb.CHAT_MESSAGE, description="yesterday")
        ActivityLog.objects.filter(pk=yesterday_log.pk).update(created_at=timezone.now() - timezone.timedelta(days=1))

        response = self.client.get(reverse("dashboard:analytics"))
        self.assertEqual(response.context["study_streak"], 2)

    def test_resources_downloaded_count(self):
        category = ResourceCategory.objects.create(name="Notes")
        resource = Resource.objects.create(title="Doc", category=category, file="resources/x.txt")
        ResourceDownloadLog.objects.create(user=self.user, resource=resource)

        response = self.client.get(reverse("dashboard:analytics"))
        self.assertEqual(response.context["resources_downloaded"], 1)
