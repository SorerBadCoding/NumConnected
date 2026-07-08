from django.conf import settings
from django.db import models

from core.models import TimeStampedModel


class FAQEntry(TimeStampedModel):
    """A single local knowledge-base entry the assistant can match against.

    This is the "local provider" knowledge source. See
    `ai_assistant.providers` for how a real AI provider would plug in
    alongside (or instead of) this table.
    """

    question = models.CharField(max_length=255)
    keywords = models.CharField(
        max_length=255,
        help_text="Comma-separated keywords/phrases used to match student questions.",
    )
    answer = models.TextField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["question"]
        verbose_name = "FAQ entry"
        verbose_name_plural = "FAQ entries"

    def __str__(self):
        return self.question

    @property
    def keyword_list(self):
        return [kw.strip().lower() for kw in self.keywords.split(",") if kw.strip()]


class ChatConversation(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="chat_conversations"
    )
    title = models.CharField(max_length=120, blank=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return self.title or f"Conversation #{self.pk}"


class MessageSender(models.TextChoices):
    USER = "user", "Student"
    ASSISTANT = "assistant", "Assistant"


class ChatMessage(TimeStampedModel):
    conversation = models.ForeignKey(
        ChatConversation, on_delete=models.CASCADE, related_name="messages"
    )
    sender = models.CharField(max_length=10, choices=MessageSender.choices)
    content = models.TextField()

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.sender}: {self.content[:40]}"
