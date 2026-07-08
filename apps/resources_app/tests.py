import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Resource, ResourceCategory

User = get_user_model()


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class ResourcePermissionTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        from django.conf import settings

        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.staff = User.objects.create_user(username="staff", password="pw123456", email="staff@x.edu", is_staff=True)
        self.student = User.objects.create_user(username="student", password="pw123456", email="student@x.edu")
        self.category = ResourceCategory.objects.create(name="Lecture Notes")

    def test_student_cannot_upload(self):
        self.client.login(username="student", password="pw123456")
        response = self.client.get(reverse("resources:create"))
        self.assertEqual(response.status_code, 302)

    def test_staff_can_upload(self):
        self.client.login(username="staff", password="pw123456")
        upload = SimpleUploadedFile("notes.txt", b"content", content_type="text/plain")
        response = self.client.post(
            reverse("resources:create"),
            {"title": "Week 1 Notes", "description": "Intro", "category": self.category.pk, "file": upload},
        )
        self.assertEqual(response.status_code, 302)
        resource = Resource.objects.get(title="Week 1 Notes")
        self.assertEqual(resource.uploaded_by, self.staff)
        self.assertGreater(resource.file_size, 0)

    def test_download_increments_counter_and_redirects_to_file(self):
        upload = SimpleUploadedFile("guide.txt", b"guide content", content_type="text/plain")
        resource = Resource.objects.create(title="Guide", category=self.category, uploaded_by=self.staff, file=upload)
        self.client.login(username="student", password="pw123456")

        response = self.client.get(reverse("resources:download", args=[resource.pk]))
        self.assertEqual(response.status_code, 302)
        resource.refresh_from_db()
        self.assertEqual(resource.download_count, 1)

    def test_search_by_title(self):
        upload = SimpleUploadedFile("apa.txt", b"apa", content_type="text/plain")
        Resource.objects.create(title="APA Citation Guide", category=self.category, uploaded_by=self.staff, file=upload)
        self.client.login(username="student", password="pw123456")

        response = self.client.get(reverse("resources:list"), {"q": "apa"})
        self.assertContains(response, "APA Citation Guide")
