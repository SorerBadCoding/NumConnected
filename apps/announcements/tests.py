from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Announcement, AnnouncementCategory

User = get_user_model()


class AnnouncementPermissionTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(username="staff", password="pw123456", email="staff@x.edu", is_staff=True)
        self.student = User.objects.create_user(username="student", password="pw123456", email="student@x.edu")

    def test_student_cannot_create(self):
        self.client.login(username="student", password="pw123456")
        response = self.client.get(reverse("announcements:create"))
        self.assertEqual(response.status_code, 302)

    def test_staff_can_create(self):
        self.client.login(username="staff", password="pw123456")
        response = self.client.post(
            reverse("announcements:create"),
            {
                "title": "Exam Schedule",
                "content": "Details here",
                "category": AnnouncementCategory.ACADEMIC,
                "publish_at": "2026-01-01T09:00",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Announcement.objects.filter(title="Exam Schedule").exists())

    def test_student_can_read_and_search(self):
        Announcement.objects.create(
            title="Library Hours", content="Extended hours", category=AnnouncementCategory.GENERAL,
            author=self.staff, publish_at=timezone.now(),
        )
        self.client.login(username="student", password="pw123456")

        response = self.client.get(reverse("announcements:list"))
        self.assertContains(response, "Library Hours")

        response = self.client.get(reverse("announcements:list"), {"q": "library"})
        self.assertContains(response, "Library Hours")

    def test_future_announcement_hidden_from_students(self):
        Announcement.objects.create(
            title="Future News", content="Not yet", category=AnnouncementCategory.GENERAL,
            author=self.staff, publish_at=timezone.now() + timezone.timedelta(days=5),
        )
        self.client.login(username="student", password="pw123456")
        response = self.client.get(reverse("announcements:list"))
        self.assertNotContains(response, "Future News")

    def test_student_cannot_delete(self):
        announcement = Announcement.objects.create(
            title="Delete Me", content="x", category=AnnouncementCategory.GENERAL,
            author=self.staff, publish_at=timezone.now(),
        )
        self.client.login(username="student", password="pw123456")
        self.client.post(reverse("announcements:delete", args=[announcement.pk]))
        self.assertTrue(Announcement.objects.filter(pk=announcement.pk).exists())
