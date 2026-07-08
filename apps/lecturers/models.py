from django.db import models
from django.urls import reverse

from core.models import TimeStampedModel


class Department(models.TextChoices):
    COMPUTER_SCIENCE = "computer_science", "Computer Science"
    MATHEMATICS = "mathematics", "Mathematics"
    BUSINESS = "business", "Business Administration"
    BIOLOGY = "biology", "Biology"
    PHYSICS = "physics", "Physics"
    CHEMISTRY = "chemistry", "Chemistry"
    ENGLISH = "english", "English"
    ECONOMICS = "economics", "Economics"


class Lecturer(TimeStampedModel):
    name = models.CharField(max_length=150)
    photo = models.ImageField(upload_to="lecturers/", blank=True, null=True)
    department = models.CharField(max_length=30, choices=Department.choices)
    subjects = models.CharField(
        max_length=300, help_text="Comma-separated list, e.g. 'Data Structures, Algorithms'"
    )
    email = models.EmailField()
    office_hours = models.CharField(max_length=200, blank=True, help_text="e.g. Mon/Wed 2:00–4:00 PM")
    office_location = models.CharField(max_length=200, blank=True)
    biography = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]
        indexes = [models.Index(fields=["department"])]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("lecturers:detail", kwargs={"pk": self.pk})

    @property
    def subject_list(self):
        return [s.strip() for s in self.subjects.split(",") if s.strip()]

    @property
    def initials(self):
        """First letters of the name, skipping honorifics like 'Dr.'/'Prof.'
        so avatars don't all render as the same letter."""
        titles = {"dr", "dr.", "prof", "prof.", "mr", "mr.", "mrs", "mrs.", "ms", "ms."}
        words = [w for w in self.name.split() if w.lower().strip(".") not in {t.strip(".") for t in titles}]
        words = words or self.name.split()
        return "".join(word[0] for word in words[:2]).upper()
