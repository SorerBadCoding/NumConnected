from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Event, EventCategory

User = get_user_model()


class EventPermissionTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(username="staff", password="pw123456", email="staff@x.edu", is_staff=True)
        self.student = User.objects.create_user(username="student", password="pw123456", email="student@x.edu")

    def test_student_cannot_create(self):
        self.client.login(username="student", password="pw123456")
        response = self.client.get(reverse("events:create"))
        self.assertEqual(response.status_code, 302)

    def test_staff_can_create_event(self):
        self.client.login(username="staff", password="pw123456")
        response = self.client.post(
            reverse("events:create"),
            {
                "title": "Career Fair",
                "description": "Meet recruiters",
                "category": EventCategory.CAREER,
                "location": "Main Hall",
                "start_datetime": "2026-09-10T10:00",
                "end_datetime": "2026-09-10T16:00",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Event.objects.filter(title="Career Fair").exists())

    def test_end_before_start_rejected(self):
        self.client.login(username="staff", password="pw123456")
        response = self.client.post(
            reverse("events:create"),
            {
                "title": "Bad Event",
                "description": "x",
                "category": EventCategory.OTHER,
                "location": "Nowhere",
                "start_datetime": "2026-09-10T16:00",
                "end_datetime": "2026-09-10T10:00",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Event.objects.filter(title="Bad Event").exists())

    def test_student_can_search_events(self):
        Event.objects.create(
            title="Basketball Finals", description="Championship", category=EventCategory.SPORTS,
            location="Gym", organizer=self.staff,
            start_datetime=timezone.now(), end_datetime=timezone.now() + timezone.timedelta(hours=2),
        )
        self.client.login(username="student", password="pw123456")
        response = self.client.get(reverse("events:list"), {"q": "basketball", "when": "all"})
        self.assertContains(response, "Basketball Finals")
