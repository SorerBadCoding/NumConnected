from django.conf import settings


def site_context(request):
    """Global template context available on every page."""
    return {
        "SITE_NAME": "NUM Connect",
        "SITE_TAGLINE": "Smart Student Portal",
        "current_theme": getattr(request, "theme", "light"),
        "ai_assistant_provider": settings.AI_ASSISTANT_PROVIDER,
    }
