from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.views.generic import TemplateView

from announcements.models import Announcement
from assignments.models import Assignment, Status
from events.models import Event


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        user = self.request.user

        assignments_qs = Assignment.objects.filter(owner=user)
        upcoming_assignments = (
            assignments_qs.exclude(status=Status.COMPLETED).order_by("due_date")[:5]
        )

        active_announcements = (
            Announcement.objects.filter(publish_at__lte=now)
            .exclude(expires_at__lt=now)
            .select_related("author")[:5]
        )

        upcoming_events = Event.objects.filter(end_datetime__gte=now).order_by("start_datetime")[:5]

        pending_qs = assignments_qs.exclude(status=Status.COMPLETED)

        local_hour = timezone.localtime(now).hour
        if local_hour < 12:
            greeting = "Good morning"
        elif local_hour < 18:
            greeting = "Good afternoon"
        else:
            greeting = "Good evening"

        context.update(
            {
                "greeting": greeting,
                "upcoming_assignments": upcoming_assignments,
                "announcements": active_announcements,
                "upcoming_events": upcoming_events,
                "pending_count": pending_qs.count(),
                "completed_count": assignments_qs.filter(status=Status.COMPLETED).count(),
                "overdue_count": sum(1 for a in pending_qs if a.is_overdue),
                "events_count": upcoming_events.count(),
            }
        )
        return context
