import os

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from core.models import TimeStampedModel


class ResourceCategory(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=110, unique=True, blank=True)
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Resource categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("resources:list") + f"?category={self.slug}"


class Resource(TimeStampedModel):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.ForeignKey(
        ResourceCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="resources",
    )
    file = models.FileField(upload_to="resources/%Y/%m/")
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="uploaded_resources",
        limit_choices_to={"is_staff": True},
    )
    download_count = models.PositiveIntegerField(default=0)
    file_size = models.PositiveIntegerField(default=0, help_text="Size in bytes.")

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["category"])]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("resources:detail", kwargs={"pk": self.pk})

    def save(self, *args, **kwargs):
        if self.file:
            try:
                self.file_size = self.file.size
            except (FileNotFoundError, ValueError):
                pass
        super().save(*args, **kwargs)

    @property
    def filename(self):
        return os.path.basename(self.file.name) if self.file else ""

    @property
    def file_extension(self):
        return os.path.splitext(self.filename)[1].lstrip(".").upper()

    @property
    def file_size_display(self):
        size = self.file_size
        for unit in ("B", "KB", "MB", "GB"):
            if size < 1024:
                return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
