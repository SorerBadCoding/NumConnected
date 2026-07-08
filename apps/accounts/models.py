from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse

from core.models import TimeStampedModel


class User(AbstractUser):
    """Custom user model so the project can grow auth requirements later
    (e.g. school-email verification) without a disruptive migration."""

    email = models.EmailField("email address", unique=True)

    class Meta:
        ordering = ["first_name", "last_name"]

    def __str__(self):
        return self.get_full_name() or self.username

    @property
    def initials(self):
        first = self.first_name[:1] if self.first_name else self.username[:1]
        last = self.last_name[:1] if self.last_name else ""
        return f"{first}{last}".upper()


class AcademicYear(models.TextChoices):
    FRESHMAN = "freshman", "Freshman (Year 1)"
    SOPHOMORE = "sophomore", "Sophomore (Year 2)"
    JUNIOR = "junior", "Junior (Year 3)"
    SENIOR = "senior", "Senior (Year 4)"
    GRADUATE = "graduate", "Graduate Student"


class Profile(TimeStampedModel):
    """Student-facing profile information, kept separate from the auth
    model so authentication concerns stay decoupled from student data."""

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile"
    )
    profile_picture = models.ImageField(
        upload_to="profile_pictures/",
        blank=True,
        null=True,
        help_text="Square images look best (min. 200x200px).",
    )
    student_id = models.CharField(
        max_length=20,
        unique=True,
        help_text="Your official university student ID.",
    )
    major = models.CharField(max_length=120)
    academic_year = models.CharField(
        max_length=20, choices=AcademicYear.choices, default=AcademicYear.FRESHMAN
    )
    bio = models.TextField(
        max_length=500, blank=True, help_text="A short introduction (max 500 characters)."
    )

    class Meta:
        ordering = ["user__first_name", "user__last_name"]

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}'s profile"

    def get_absolute_url(self):
        return reverse("accounts:profile")

    @property
    def profile_picture_url(self):
        if self.profile_picture and hasattr(self.profile_picture, "url"):
            return self.profile_picture.url
        return None
