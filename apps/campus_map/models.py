from django.db import models

from core.models import TimeStampedModel


class LocationCategory(models.TextChoices):
    BUILDING = "building", "Academic Building"
    LIBRARY = "library", "Library"
    LAB = "lab", "Laboratory"
    CAFETERIA = "cafeteria", "Cafeteria"
    STUDENT_AFFAIRS = "student_affairs", "Student Affairs"
    PARKING = "parking", "Parking"
    OTHER = "other", "Other"


CATEGORY_ICONS = {
    LocationCategory.BUILDING: "bi-building",
    LocationCategory.LIBRARY: "bi-book",
    LocationCategory.LAB: "bi-cpu",
    LocationCategory.CAFETERIA: "bi-cup-hot",
    LocationCategory.STUDENT_AFFAIRS: "bi-people",
    LocationCategory.PARKING: "bi-p-square",
    LocationCategory.OTHER: "bi-geo-alt",
}


class CampusLocation(TimeStampedModel):
    name = models.CharField(max_length=150)
    category = models.CharField(max_length=20, choices=LocationCategory.choices, default=LocationCategory.OTHER)
    description = models.TextField(blank=True)
    building_code = models.CharField(max_length=20, blank=True, help_text="e.g. 'Bldg A'")
    # Stored as percentages (0-100) so markers scale with the map image at
    # any size, without needing real GPS coordinates.
    x_position = models.DecimalField(max_digits=5, decimal_places=2, help_text="Horizontal position, 0-100%")
    y_position = models.DecimalField(max_digits=5, decimal_places=2, help_text="Vertical position, 0-100%")

    class Meta:
        ordering = ["name"]
        indexes = [models.Index(fields=["category"])]

    def __str__(self):
        return self.name

    @property
    def icon(self):
        return CATEGORY_ICONS.get(self.category, "bi-geo-alt")
