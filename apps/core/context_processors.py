from django.conf import settings


def site_context(request):
    """Global template context available on every page."""
    context = {
        "SITE_NAME": "NUM Connect",
        "SITE_TAGLINE": "Smart Student Portal",
        "current_theme": getattr(request, "theme", "light"),
        "ai_assistant_provider": settings.AI_ASSISTANT_PROVIDER,
    }

    if request.user.is_authenticated:
        from notifications.models import Notification

        notifications_qs = Notification.objects.filter(user=request.user)
        context["nav_unread_notifications_count"] = notifications_qs.filter(is_read=False).count()
        context["nav_recent_notifications"] = notifications_qs[:6]

    return context
