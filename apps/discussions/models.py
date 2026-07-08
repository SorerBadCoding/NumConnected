from django.conf import settings
from django.db import models
from django.urls import reverse

from core.models import TimeStampedModel


class PostCategory(models.TextChoices):
    GENERAL = "general", "General"
    PROGRAMMING = "programming", "Programming"
    MATHEMATICS = "mathematics", "Mathematics"
    ASSIGNMENTS = "assignments", "Assignments"
    EVENTS = "events", "Events"
    STUDY_TIPS = "study_tips", "Study Tips"
    QUESTIONS = "questions", "Questions"


class Post(TimeStampedModel):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="discussion_posts"
    )
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to="discussions/%Y/%m/", blank=True, null=True)
    category = models.CharField(max_length=20, choices=PostCategory.choices, default=PostCategory.GENERAL)
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="liked_posts", blank=True
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["category"]), models.Index(fields=["-created_at"])]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("discussions:detail", kwargs={"pk": self.pk})

    @property
    def like_count(self):
        return self.likes.count()

    @property
    def comment_count(self):
        return self.comments.count()


class Comment(TimeStampedModel):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="discussion_comments"
    )
    content = models.TextField()

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment by {self.author} on {self.post}"
