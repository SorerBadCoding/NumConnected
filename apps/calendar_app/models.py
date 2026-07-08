from django.db import models

from core.models import TimeStampedModel


class Exam(TimeStampedModel):
    course = models.CharField(max_length=120)
    title = models.CharField(max_length=200)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    location = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["date", "start_time"]

    def __str__(self):
        return f"{self.course} — {self.title}"


class Holiday(TimeStampedModel):
    name = models.CharField(max_length=150)
    date = models.DateField()
    end_date = models.DateField(
        null=True, blank=True, help_text="Leave blank for a single-day holiday."
    )

    class Meta:
        ordering = ["date"]

    def __str__(self):
        return self.name

    @property
    def last_day(self):
        return self.end_date or self.date
