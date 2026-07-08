"""
AI provider abstraction.

Every backend (local FAQ matching today, OpenAI or another vendor later)
implements `BaseAIProvider.respond()`. Views only ever call `get_provider()`
and never talk to a concrete provider class directly, so switching backends
is a one-line settings change (`AI_ASSISTANT_PROVIDER`) with no changes to
views, templates, or the chat JS.
"""

from abc import ABC, abstractmethod

from django.conf import settings

from .models import FAQEntry


class BaseAIProvider(ABC):
    @abstractmethod
    def respond(self, message: str, *, user=None, history=None) -> str:
        """Return a plain-text reply to the student's `message`.

        `history` is an iterable of ChatMessage instances for the current
        conversation (oldest first), provided so providers that support
        multi-turn context (like a real LLM) can use it.
        """
        raise NotImplementedError


class LocalFAQProvider(BaseAIProvider):
    """Keyword-matches the message against the FAQEntry knowledge base.

    Fully offline — no network calls, no API key required. This is the
    default provider until a real AI backend is configured.
    """

    FALLBACK_RESPONSE = (
        "I'm not sure about that one yet. Try rephrasing your question, or "
        "browse Announcements and Study Resources — a lot of common "
        "questions are answered there. For anything account-specific, "
        "reach out to your academic advisor."
    )

    def respond(self, message: str, *, user=None, history=None) -> str:
        message_lower = message.lower()
        best_entry, best_score = None, 0

        for entry in FAQEntry.objects.filter(is_active=True):
            score = sum(1 for keyword in entry.keyword_list if keyword and keyword in message_lower)
            if score > best_score:
                best_entry, best_score = entry, score

        if best_entry:
            return best_entry.answer
        return self.FALLBACK_RESPONSE


class OpenAIProvider(BaseAIProvider):
    """Real AI-backed provider — inactive until explicitly enabled.

    To switch on: set `AI_ASSISTANT_PROVIDER=openai` and `OPENAI_API_KEY`,
    then `pip install openai`. The `openai` package is imported lazily so it
    is never required while the local provider is active.
    """

    SYSTEM_PROMPT = (
        "You are the NUM Connect assistant, helping university students "
        "with questions about assignments, announcements, campus events, "
        "and study resources. Be concise, friendly, and specific."
    )

    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model

    def respond(self, message: str, *, user=None, history=None) -> str:
        if not settings.OPENAI_API_KEY:
            raise RuntimeError(
                "AI_ASSISTANT_PROVIDER is 'openai' but OPENAI_API_KEY is not "
                "set. Configure it in your environment to enable this provider."
            )

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError(
                "The 'openai' package is required for OpenAIProvider. "
                "Install it with: pip install openai"
            ) from exc

        chat_messages = [{"role": "system", "content": self.SYSTEM_PROMPT}]
        for turn in history or []:
            role = "assistant" if turn.sender == "assistant" else "user"
            chat_messages.append({"role": role, "content": turn.content})
        chat_messages.append({"role": "user", "content": message})

        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        completion = client.chat.completions.create(model=self.model, messages=chat_messages)
        return completion.choices[0].message.content


def get_provider() -> BaseAIProvider:
    """Return the active provider instance based on settings.AI_ASSISTANT_PROVIDER."""
    provider_name = getattr(settings, "AI_ASSISTANT_PROVIDER", "local")
    if provider_name == "openai":
        return OpenAIProvider()
    return LocalFAQProvider()
