from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from announcements.models import Announcement, AnnouncementCategory
from events.models import Event, EventCategory

User = get_user_model()


class GlobalSearchTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(username="staff", password="pw123456", email="staff@x.edu", is_staff=True)
        self.student = User.objects.create_user(username="student", password="pw123456", email="student@x.edu")
        self.client.login(username="student", password="pw123456")

        Announcement.objects.create(
            title="Library Hours Extended", content="Open until midnight", category=AnnouncementCategory.GENERAL,
            author=self.staff, publish_at=timezone.now(),
        )
        Event.objects.create(
            title="Library Study Marathon", description="Group study", category=EventCategory.ACADEMIC,
            location="Main Library", organizer=self.staff,
            start_datetime=timezone.now(), end_datetime=timezone.now() + timezone.timedelta(hours=3),
        )

    def test_search_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("core:search"), {"q": "library"})
        self.assertEqual(response.status_code, 302)

    def test_search_finds_matches_across_apps(self):
        response = self.client.get(reverse("core:search"), {"q": "library"})
        self.assertContains(response, "Library Hours Extended")
        self.assertContains(response, "Library Study Marathon")

    def test_empty_query_shows_prompt(self):
        response = self.client.get(reverse("core:search"))
        self.assertEqual(response.context["total_count"], 0)

    def test_no_results_message(self):
        response = self.client.get(reverse("core:search"), {"q": "zzzznotfound"})
        self.assertContains(response, "No results found")
