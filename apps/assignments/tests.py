from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Assignment, Priority, Status

User = get_user_model()


class AssignmentCRUDTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="owner", password="pw123456", email="owner@x.edu")
        self.other = User.objects.create_user(username="other", password="pw123456", email="other@x.edu")
        self.client.login(username="owner", password="pw123456")

    def test_create_assignment(self):
        response = self.client.post(
            reverse("assignments:create"),
            {
                "title": "Essay",
                "course": "ENG101",
                "description": "Write an essay",
                "due_date": "2026-08-01T10:00",
                "priority": Priority.HIGH,
                "status": Status.NOT_STARTED,
            },
        )
        self.assertEqual(response.status_code, 302)
        assignment = Assignment.objects.get(title="Essay")
        self.assertEqual(assignment.owner, self.owner)

    def test_toggle_completion(self):
        assignment = Assignment.objects.create(
            owner=self.owner, title="HW1", due_date=timezone.now(), status=Status.NOT_STARTED
        )
        self.client.post(reverse("assignments:toggle", args=[assignment.pk]))
        assignment.refresh_from_db()
        self.assertEqual(assignment.status, Status.COMPLETED)
        self.assertIsNotNone(assignment.completed_at)

    def test_other_user_cannot_edit(self):
        assignment = Assignment.objects.create(owner=self.owner, title="Private", due_date=timezone.now())
        self.client.logout()
        self.client.login(username="other", password="pw123456")

        response = self.client.get(reverse("assignments:update", args=[assignment.pk]))
        self.assertEqual(response.status_code, 302)

        response = self.client.post(reverse("assignments:delete", args=[assignment.pk]))
        self.assertTrue(Assignment.objects.filter(pk=assignment.pk).exists())

    def test_list_only_shows_own_assignments(self):
        Assignment.objects.create(owner=self.owner, title="Mine", due_date=timezone.now())
        Assignment.objects.create(owner=self.other, title="Not Mine", due_date=timezone.now())

        response = self.client.get(reverse("assignments:list"))
        titles = {a.title for a in response.context["assignments"]}
        self.assertEqual(titles, {"Mine"})

    def test_search_filters_by_title(self):
        Assignment.objects.create(owner=self.owner, title="Physics Lab", due_date=timezone.now())
        Assignment.objects.create(owner=self.owner, title="History Essay", due_date=timezone.now())

        response = self.client.get(reverse("assignments:list"), {"q": "physics"})
        titles = {a.title for a in response.context["assignments"]}
        self.assertEqual(titles, {"Physics Lab"})
