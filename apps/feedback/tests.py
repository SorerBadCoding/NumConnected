from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Feedback, FeedbackStatus, FeedbackType

User = get_user_model()


class FeedbackTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(username="staff", password="pw123456", email="staff@x.edu", is_staff=True)
        self.student = User.objects.create_user(username="student", password="pw123456", email="s@x.edu")
        self.other_student = User.objects.create_user(username="other", password="pw123456", email="o@x.edu")

    def test_submit_feedback(self):
        self.client.login(username="student", password="pw123456")
        response = self.client.post(reverse("feedback:create"), {
            "feedback_type": FeedbackType.BUG,
            "subject": "Broken download button",
            "message": "The download button on resources does nothing.",
        })
        self.assertEqual(response.status_code, 302)
        feedback = Feedback.objects.get(subject="Broken download button")
        self.assertEqual(feedback.user, self.student)
        self.assertEqual(feedback.status, FeedbackStatus.OPEN)

    def test_rating_type_requires_rating_value(self):
        self.client.login(username="student", password="pw123456")
        response = self.client.post(reverse("feedback:create"), {
            "feedback_type": FeedbackType.RATING,
            "subject": "Loving the app",
            "message": "Great platform overall.",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Feedback.objects.filter(subject="Loving the app").exists())

    def test_student_only_sees_own_feedback(self):
        Feedback.objects.create(user=self.student, feedback_type=FeedbackType.SUGGESTION, subject="Mine", message="x")
        Feedback.objects.create(user=self.other_student, feedback_type=FeedbackType.SUGGESTION, subject="Not mine", message="x")

        self.client.login(username="student", password="pw123456")
        response = self.client.get(reverse("feedback:list"))
        subjects = [f.subject for f in response.context["feedback_items"]]
        self.assertEqual(subjects, ["Mine"])

    def test_staff_sees_all_feedback(self):
        Feedback.objects.create(user=self.student, feedback_type=FeedbackType.SUGGESTION, subject="From student", message="x")
        self.client.login(username="staff", password="pw123456")
        response = self.client.get(reverse("feedback:list"))
        subjects = [f.subject for f in response.context["feedback_items"]]
        self.assertIn("From student", subjects)

    def test_student_cannot_view_others_feedback(self):
        item = Feedback.objects.create(user=self.other_student, feedback_type=FeedbackType.SUGGESTION, subject="Private", message="x")
        self.client.login(username="student", password="pw123456")
        response = self.client.get(reverse("feedback:detail", args=[item.pk]))
        self.assertEqual(response.status_code, 302)

    def test_staff_can_reply_and_resolve(self):
        item = Feedback.objects.create(user=self.student, feedback_type=FeedbackType.BUG, subject="Bug", message="x")
        self.client.login(username="staff", password="pw123456")
        response = self.client.post(reverse("feedback:reply", args=[item.pk]), {
            "status": FeedbackStatus.RESOLVED,
            "admin_reply": "Fixed in the latest release.",
        })
        self.assertEqual(response.status_code, 302)
        item.refresh_from_db()
        self.assertEqual(item.status, FeedbackStatus.RESOLVED)
        self.assertIsNotNone(item.resolved_at)
        self.assertEqual(item.admin_reply, "Fixed in the latest release.")

    def test_student_cannot_reply(self):
        item = Feedback.objects.create(user=self.student, feedback_type=FeedbackType.BUG, subject="Bug", message="x")
        self.client.login(username="student", password="pw123456")
        response = self.client.post(reverse("feedback:reply", args=[item.pk]), {
            "status": FeedbackStatus.RESOLVED, "admin_reply": "Nice try",
        })
        self.assertEqual(response.status_code, 302)
        item.refresh_from_db()
        self.assertEqual(item.status, FeedbackStatus.OPEN)
