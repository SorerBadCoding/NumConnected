from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import CampusLocation, LocationCategory

User = get_user_model()


class CampusMapTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="student", password="pw123456", email="s@x.edu")
        self.client.login(username="student", password="pw123456")
        self.library = CampusLocation.objects.create(
            name="Main Library", category=LocationCategory.LIBRARY,
            description="Central library", x_position=40, y_position=30,
        )
        self.lab = CampusLocation.objects.create(
            name="Computer Lab 1", category=LocationCategory.LAB,
            description="CS department lab", x_position=60, y_position=50,
        )

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("campus_map:map"))
        self.assertEqual(response.status_code, 302)

    def test_map_shows_all_locations(self):
        response = self.client.get(reverse("campus_map:map"))
        self.assertContains(response, "Main Library")
        self.assertContains(response, "Computer Lab 1")

    def test_search_filters_location_list(self):
        response = self.client.get(reverse("campus_map:map"), {"q": "library"})
        names = [loc.name for loc in response.context["locations"]]
        self.assertEqual(names, ["Main Library"])
        # The map itself always shows every marker regardless of the filter.
        all_names = [loc.name for loc in response.context["all_locations"]]
        self.assertIn("Computer Lab 1", all_names)

    def test_filter_by_category(self):
        response = self.client.get(reverse("campus_map:map"), {"category": LocationCategory.LAB})
        names = [loc.name for loc in response.context["locations"]]
        self.assertEqual(names, ["Computer Lab 1"])
