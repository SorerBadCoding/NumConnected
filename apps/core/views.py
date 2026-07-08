from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.utils import timezone
from django.views.generic import TemplateView

from announcements.models import Announcement
from events.models import Event
from resources_app.models import Resource


class GlobalSearchView(LoginRequiredMixin, TemplateView):
    template_name = "core/search_results.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get("q", "").strip()
        context["query"] = query

        if not query:
            context.update(announcements=[], resources=[], events=[], total_count=0)
            return context

        announcements = Announcement.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )
        if not self.request.user.is_staff:
            now = timezone.now()
            announcements = announcements.filter(publish_at__lte=now).exclude(expires_at__lt=now)

        resources = Resource.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        ).select_related("category")

        events = Event.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query) | Q(location__icontains=query)
        )

        context.update(
            announcements=announcements[:20],
            resources=resources[:20],
            events=events[:20],
            total_count=announcements.count() + resources.count() + events.count(),
        )
        return context
