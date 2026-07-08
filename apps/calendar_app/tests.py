from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from assignments.models import Assignment, Priority, Status
from events.models import Event, EventCategory

from .models import Exam, Holiday

User = get_user_model()


class CalendarViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="cal", password="pw123456", email="c@x.edu")
        self.client.login(username="cal", password="pw123456")
        self.today = timezone.localdate()

        Assignment.objects.create(
            owner=self.user, title="Physics HW", due_date=timezone.now(),
            priority=Priority.MEDIUM, status=Status.NOT_STARTED,
        )
        Event.objects.create(
            title="Club Fair", description="", category=EventCategory.SOCIAL, location="Quad",
            start_datetime=timezone.now(), end_datetime=timezone.now() + timezone.timedelta(hours=2),
        )
        Exam.objects.create(
            course="CS201", title="Midterm", date=self.today,
            start_time="09:00", end_time="11:00", location="Hall A",
        )
        Holiday.objects.create(name="Founders Day", date=self.today)

    def test_month_view_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("calendar_app:month"))
        self.assertEqual(response.status_code, 302)

    def test_month_view_shows_all_item_types(self):
        # Checked via response.context rather than raw HTML: the day cell
        # template caps visible chips at 3 with a "+N more" overflow, and this
        # test intentionally stacks 4 items (assignment/event/exam/holiday) on
        # the same day to prove all four sources feed the calendar.
        response = self.client.get(reverse("calendar_app:month"))
        self.assertEqual(response.status_code, 200)
        all_labels = [
            item["label"]
            for week in response.context["weeks"]
            for day in week
            for item in day["items"]
        ]
        self.assertIn("Physics HW", all_labels)
        self.assertIn("Club Fair", all_labels)
        self.assertIn("CS201: Midterm", all_labels)
        self.assertIn("Founders Day", all_labels)

    def test_month_navigation(self):
        response = self.client.get(reverse("calendar_app:month", args=[self.today.year, self.today.month]))
        self.assertEqual(response.status_code, 200)

    def test_week_view(self):
        response = self.client.get(reverse("calendar_app:week"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Midterm")

    def test_search_filters_items(self):
        # Check the calendar grid data itself (response.context) rather than
        # raw page text — "Club Fair" also legitimately appears in the navbar's
        # unrelated notification dropdown ("New event: Club Fair"), which would
        # make a whole-page substring assertion a false positive.
        response = self.client.get(reverse("calendar_app:month"), {"q": "physics"})
        all_labels = [
            item["label"]
            for week in response.context["weeks"]
            for day in week
            for item in day["items"]
        ]
        self.assertIn("Physics HW", all_labels)
        self.assertNotIn("Club Fair", all_labels)
