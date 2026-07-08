import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Resource, ResourceCategory, ResourceDownloadLog, ResourceView, Tag

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

    def test_upload_creates_tags_from_comma_separated_input(self):
        self.client.login(username="staff", password="pw123456")
        upload = SimpleUploadedFile("notes.txt", b"content", content_type="text/plain")
        self.client.post(
            reverse("resources:create"),
            {
                "title": "Tagged Notes", "description": "x", "category": self.category.pk,
                "file": upload, "tags_input": "midterm, review, chapter-3",
            },
        )
        resource = Resource.objects.get(title="Tagged Notes")
        self.assertEqual(
            set(resource.tags.values_list("name", flat=True)),
            {"midterm", "review", "chapter-3"},
        )
        self.assertEqual(Tag.objects.count(), 3)

    def test_toggle_favorite(self):
        upload = SimpleUploadedFile("fav.txt", b"content", content_type="text/plain")
        resource = Resource.objects.create(title="Fav Me", category=self.category, uploaded_by=self.staff, file=upload)
        self.client.login(username="student", password="pw123456")

        response = self.client.post(
            reverse("resources:toggle_favorite", args=[resource.pk]),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.json(), {"favorited": True})
        self.assertTrue(resource.favorited_by.filter(username="student").exists())

        response = self.client.post(
            reverse("resources:toggle_favorite", args=[resource.pk]),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.json(), {"favorited": False})

    def test_favorites_only_filter(self):
        upload1 = SimpleUploadedFile("a.txt", b"a", content_type="text/plain")
        upload2 = SimpleUploadedFile("b.txt", b"b", content_type="text/plain")
        favorited = Resource.objects.create(title="Favorited One", category=self.category, uploaded_by=self.staff, file=upload1)
        Resource.objects.create(title="Not Favorited", category=self.category, uploaded_by=self.staff, file=upload2)
        favorited.favorited_by.add(self.student)

        self.client.login(username="student", password="pw123456")
        response = self.client.get(reverse("resources:list"), {"favorites_only": "on"})
        titles = [r.title for r in response.context["resources"]]
        self.assertEqual(titles, ["Favorited One"])

    def test_detail_view_records_recently_viewed(self):
        upload = SimpleUploadedFile("view.txt", b"content", content_type="text/plain")
        resource = Resource.objects.create(title="Viewed Doc", category=self.category, uploaded_by=self.staff, file=upload)
        self.client.login(username="student", password="pw123456")

        self.client.get(reverse("resources:detail", args=[resource.pk]))
        self.assertTrue(ResourceView.objects.filter(user__username="student", resource=resource).exists())

        # Viewing again should update, not duplicate, the record.
        self.client.get(reverse("resources:detail", args=[resource.pk]))
        self.assertEqual(ResourceView.objects.filter(user__username="student", resource=resource).count(), 1)

    def test_download_creates_log_entry(self):
        upload = SimpleUploadedFile("log.txt", b"content", content_type="text/plain")
        resource = Resource.objects.create(title="Log Doc", category=self.category, uploaded_by=self.staff, file=upload)
        self.client.login(username="student", password="pw123456")

        self.client.get(reverse("resources:download", args=[resource.pk]))
        self.assertEqual(ResourceDownloadLog.objects.filter(user__username="student", resource=resource).count(), 1)

    def test_sort_by_most_downloaded(self):
        upload1 = SimpleUploadedFile("a.txt", b"a", content_type="text/plain")
        upload2 = SimpleUploadedFile("b.txt", b"b", content_type="text/plain")
        popular = Resource.objects.create(title="Popular", category=self.category, uploaded_by=self.staff, file=upload1, download_count=10)
        Resource.objects.create(title="Unpopular", category=self.category, uploaded_by=self.staff, file=upload2, download_count=0)

        self.client.login(username="student", password="pw123456")
        response = self.client.get(reverse("resources:list"), {"sort": "popular"})
        titles = [r.title for r in response.context["resources"]]
        self.assertEqual(titles[0], "Popular")
