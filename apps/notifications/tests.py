from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from announcements.models import Announcement, AnnouncementCategory

from .models import Notification, NotificationType

User = get_user_model()


class NotificationSignalTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(username="staff", password="pw123456", email="staff@x.edu", is_staff=True)
        self.student = User.objects.create_user(username="student", password="pw123456", email="student@x.edu")

    def test_new_announcement_notifies_students_not_staff(self):
        Announcement.objects.create(
            title="Test", content="Body", category=AnnouncementCategory.GENERAL,
            author=self.staff, publish_at=timezone.now(),
        )
        self.assertTrue(
            Notification.objects.filter(user=self.student, notification_type=NotificationType.NEW_ANNOUNCEMENT).exists()
        )
        self.assertFalse(
            Notification.objects.filter(user=self.staff, notification_type=NotificationType.NEW_ANNOUNCEMENT).exists()
        )


class NotificationViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="jamie", password="pw123456", email="j@x.edu")
        self.client.login(username="jamie", password="pw123456")

    def test_mark_read(self):
        notification = Notification.objects.create(
            user=self.user, notification_type=NotificationType.ACCOUNT_UPDATE, title="Hi", url="/",
        )
        self.client.post(reverse("notifications:mark_read", args=[notification.pk]))
        notification.refresh_from_db()
        self.assertTrue(notification.is_read)

    def test_mark_all_read(self):
        Notification.objects.create(user=self.user, notification_type=NotificationType.ACCOUNT_UPDATE, title="A")
        Notification.objects.create(user=self.user, notification_type=NotificationType.ACCOUNT_UPDATE, title="B")
        self.client.post(reverse("notifications:mark_all_read"))
        self.assertEqual(Notification.objects.filter(user=self.user, is_read=False).count(), 0)

    def test_list_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("notifications:list"))
        self.assertEqual(response.status_code, 302)
