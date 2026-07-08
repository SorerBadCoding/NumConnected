from django.test import TestCase
from django.urls import reverse

from .models import AcademicYear, Profile, User


class RegistrationTests(TestCase):
    def test_register_creates_user_and_profile(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "newstudent",
                "first_name": "New",
                "last_name": "Student",
                "email": "new@student.edu",
                "student_id": "2026-00001",
                "major": "Mathematics",
                "academic_year": AcademicYear.FRESHMAN,
                "password1": "SuperSecret123!",
                "password2": "SuperSecret123!",
            },
        )
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username="newstudent")
        self.assertEqual(user.profile.student_id, "2026-00001")
        self.assertEqual(user.profile.major, "Mathematics")

    def test_duplicate_student_id_rejected(self):
        User.objects.create_user(username="existing", password="pw", email="e@x.edu")
        Profile.objects.filter(user__username="existing").update(student_id="2026-00099")

        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "another",
                "first_name": "A",
                "last_name": "B",
                "email": "another@student.edu",
                "student_id": "2026-00099",
                "major": "Physics",
                "academic_year": AcademicYear.SOPHOMORE,
                "password1": "SuperSecret123!",
                "password2": "SuperSecret123!",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="another").exists())


class ProfileTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="jamie", password="pw123456", email="jamie@x.edu")
        self.user.profile.student_id = "2026-00042"
        self.user.profile.save()

    def test_profile_requires_login(self):
        response = self.client.get(reverse("accounts:profile"))
        self.assertEqual(response.status_code, 302)

    def test_profile_edit_updates_user_and_profile(self):
        self.client.login(username="jamie", password="pw123456")
        response = self.client.post(
            reverse("accounts:profile_edit"),
            {
                "first_name": "Jamie",
                "last_name": "Updated",
                "email": "jamie@x.edu",
                "student_id": "2026-00042",
                "major": "Biology",
                "academic_year": AcademicYear.JUNIOR,
                "bio": "Hello world",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.last_name, "Updated")
        self.assertEqual(self.user.profile.major, "Biology")
