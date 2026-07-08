import json
from datetime import timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F
from django.utils import timezone
from django.views.generic import TemplateView

from announcements.models import Announcement
from assignments.models import Assignment, Priority, Status
from core.models import ActivityLog
from events.models import Event
from notifications.models import Notification
from resources_app.models import Resource, ResourceDownloadLog


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        today = timezone.localdate()
        user = self.request.user

        assignments_qs = Assignment.objects.filter(owner=user)
        pending_qs = assignments_qs.exclude(status=Status.COMPLETED)
        upcoming_assignments = pending_qs.order_by("due_date")[:5]

        active_announcements = (
            Announcement.objects.filter(publish_at__lte=now)
            .exclude(expires_at__lt=now)
            .select_related("author")[:5]
        )

        upcoming_events = Event.objects.filter(end_datetime__gte=now).order_by("start_datetime")[:5]

        # ---- Today's schedule: assignments due today + events today, merged ----
        todays_assignments = pending_qs.filter(due_date__date=today)
        todays_events = Event.objects.filter(start_datetime__date=today)
        schedule_items = [
            {
                "time": a.due_date,
                "title": a.title,
                "subtitle": a.course or "Assignment due",
                "type": "assignment",
                "icon": "bi-journal-text",
                "url": a.get_absolute_url(),
            }
            for a in todays_assignments
        ] + [
            {
                "time": e.start_datetime,
                "title": e.title,
                "subtitle": e.location,
                "type": "event",
                "icon": "bi-calendar-event",
                "url": e.get_absolute_url(),
            }
            for e in todays_events
        ]
        schedule_items.sort(key=lambda item: item["time"])

        # ---- Assignment progress ----
        total_assignments = assignments_qs.count()
        completed_count = assignments_qs.filter(status=Status.COMPLETED).count()
        progress_percent = round((completed_count / total_assignments) * 100) if total_assignments else 0
        priority_breakdown = [
            {
                "label": label,
                "count": pending_qs.filter(priority=value).count(),
            }
            for value, label in Priority.choices
        ]

        # ---- Recent activity + notifications ----
        recent_activity = ActivityLog.objects.filter(user=user)[:6]
        recent_notifications = Notification.objects.filter(user=user)[:5]
        latest_resources = Resource.objects.select_related("category")[:3]

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
                "today": today,
                "upcoming_assignments": upcoming_assignments,
                "announcements": active_announcements,
                "upcoming_events": upcoming_events,
                "pending_count": pending_qs.count(),
                "completed_count": completed_count,
                "overdue_count": sum(1 for a in pending_qs if a.is_overdue),
                "events_count": upcoming_events.count(),
                "schedule_items": schedule_items,
                "total_assignments": total_assignments,
                "progress_percent": progress_percent,
                "priority_breakdown": priority_breakdown,
                "recent_activity": recent_activity,
                "recent_notifications": recent_notifications,
                "latest_resources": latest_resources,
            }
        )
        return context


class AnalyticsView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/analytics.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        today = timezone.localdate()

        assignments_qs = Assignment.objects.filter(owner=user)
        completed_qs = assignments_qs.filter(status=Status.COMPLETED)
        completed_count = completed_qs.count()
        pending_count = assignments_qs.exclude(status=Status.COMPLETED).count()

        resources_downloaded = ResourceDownloadLog.objects.filter(user=user).count()
        events_joined = user.attending_events.count()

        # ---- Study streak: consecutive days (including today) with any activity ----
        activity_dates = set(
            ActivityLog.objects.filter(user=user).values_list("created_at__date", flat=True)
        )
        streak = 0
        cursor = today
        while cursor in activity_dates:
            streak += 1
            cursor -= timedelta(days=1)

        # ---- Weekly activity: last 7 days, activity count per day ----
        week_days = [today - timedelta(days=offset) for offset in range(6, -1, -1)]
        weekly_counts = [
            ActivityLog.objects.filter(user=user, created_at__date=day).count() for day in week_days
        ]
        weekly_labels = [day.strftime("%a") for day in week_days]

        # ---- Recent performance: on-time vs late completions ----
        on_time_count = completed_qs.filter(completed_at__lte=F("due_date")).count()
        late_count = completed_count - on_time_count

        context.update(
            {
                "completed_count": completed_count,
                "pending_count": pending_count,
                "resources_downloaded": resources_downloaded,
                "events_joined": events_joined,
                "study_streak": streak,
                "weekly_labels_json": json.dumps(weekly_labels),
                "weekly_counts_json": json.dumps(weekly_counts),
                "on_time_count": on_time_count,
                "late_count": late_count,
                "has_performance_data": completed_count > 0,
            }
        )
        return context
