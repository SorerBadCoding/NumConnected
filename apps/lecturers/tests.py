from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Department, Lecturer

User = get_user_model()


class LecturerDirectoryTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="student", password="pw123456", email="s@x.edu")
        self.client.login(username="student", password="pw123456")
        self.cs_lecturer = Lecturer.objects.create(
            name="Dr. Ada Lovelace",
            department=Department.COMPUTER_SCIENCE,
            subjects="Algorithms, Data Structures",
            email="ada@num.edu",
            office_hours="Mon/Wed 2-4pm",
            office_location="Building A, Room 201",
        )
        self.math_lecturer = Lecturer.objects.create(
            name="Dr. Alan Turing",
            department=Department.MATHEMATICS,
            subjects="Calculus, Number Theory",
            email="alan@num.edu",
        )

    def test_list_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("lecturers:list"))
        self.assertEqual(response.status_code, 302)

    def test_list_shows_all_lecturers(self):
        response = self.client.get(reverse("lecturers:list"))
        self.assertContains(response, "Dr. Ada Lovelace")
        self.assertContains(response, "Dr. Alan Turing")

    def test_search_by_subject(self):
        response = self.client.get(reverse("lecturers:list"), {"q": "algorithms"})
        names = [lecturer.name for lecturer in response.context["lecturers"]]
        self.assertEqual(names, ["Dr. Ada Lovelace"])

    def test_filter_by_department(self):
        response = self.client.get(reverse("lecturers:list"), {"department": Department.MATHEMATICS})
        names = [lecturer.name for lecturer in response.context["lecturers"]]
        self.assertEqual(names, ["Dr. Alan Turing"])

    def test_detail_view(self):
        response = self.client.get(reverse("lecturers:detail", args=[self.cs_lecturer.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ada@num.edu")
        self.assertContains(response, "Data Structures")

    def test_initials_skip_honorific(self):
        # Names commonly share the "Dr." honorific — initials should be
        # derived from the actual name so avatars aren't all identical.
        self.assertEqual(self.cs_lecturer.initials, "AL")
        self.assertEqual(self.math_lecturer.initials, "AT")
