import calendar
from datetime import date, timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.utils import timezone
from django.views.generic import TemplateView

from assignments.models import Assignment, Status
from events.models import Event

from .models import Exam, Holiday


class CalendarBaseMixin:
    def _collect_items(self, range_start, range_end, query=""):
        """Return a dict keyed by date with color-coded calendar items for
        assignments, events, exams, and holidays overlapping the range."""
        user = self.request.user
        items_by_date = {}

        def add(day, entry):
            items_by_date.setdefault(day, []).append(entry)

        assignments = Assignment.objects.filter(
            owner=user, due_date__date__gte=range_start, due_date__date__lte=range_end
        ).exclude(status=Status.COMPLETED)
        if query:
            assignments = assignments.filter(title__icontains=query)
        for assignment in assignments:
            add(
                assignment.due_date.date(),
                {
                    "kind": "assignment",
                    "label": assignment.title,
                    "time": assignment.due_date,
                    "url": assignment.get_absolute_url(),
                    "badge_class": "badge-soft-accent",
                },
            )

        events = Event.objects.filter(
            start_datetime__date__gte=range_start, start_datetime__date__lte=range_end
        )
        if query:
            events = events.filter(title__icontains=query)
        for event in events:
            add(
                event.start_datetime.date(),
                {
                    "kind": "event",
                    "label": event.title,
                    "time": event.start_datetime,
                    "url": event.get_absolute_url(),
                    "badge_class": "badge-soft-warning",
                },
            )

        exams = Exam.objects.filter(date__gte=range_start, date__lte=range_end)
        if query:
            exams = exams.filter(title__icontains=query)
        for exam in exams:
            add(
                exam.date,
                {
                    "kind": "exam",
                    "label": f"{exam.course}: {exam.title}",
                    "time": exam.start_time,
                    "url": "",
                    "badge_class": "badge-soft-danger",
                },
            )

        # NULL end_date means a single-day holiday. `.exclude(end_date__lt=x)`
        # would silently drop those rows (SQL's three-valued NULL logic), so
        # this is expressed as an explicit either/or instead.
        holidays = Holiday.objects.filter(date__lte=range_end).filter(
            Q(end_date__isnull=True, date__gte=range_start) | Q(end_date__gte=range_start)
        )
        for holiday in holidays:
            if query and query.lower() not in holiday.name.lower():
                continue
            start = max(holiday.date, range_start)
            end = min(holiday.last_day, range_end)
            current = start
            while current <= end:
                add(
                    current,
                    {
                        "kind": "holiday",
                        "label": holiday.name,
                        "time": None,
                        "url": "",
                        "badge_class": "badge-soft-success",
                    },
                )
                current += timedelta(days=1)

        return items_by_date


class CalendarMonthView(LoginRequiredMixin, CalendarBaseMixin, TemplateView):
    template_name = "calendar_app/month.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.localdate()
        year = int(self.kwargs.get("year") or today.year)
        month = int(self.kwargs.get("month") or today.month)
        query = self.request.GET.get("q", "").strip()

        first_day = date(year, month, 1)

        cal = calendar.Calendar(firstweekday=0)
        grid_dates = list(cal.itermonthdates(year, month))
        items_by_date = self._collect_items(grid_dates[0], grid_dates[-1], query)

        weeks = []
        for i in range(0, len(grid_dates), 7):
            week = [
                {
                    "date": day,
                    "is_current_month": day.month == month,
                    "is_today": day == today,
                    "items": items_by_date.get(day, []),
                }
                for day in grid_dates[i : i + 7]
            ]
            weeks.append(week)

        prev_month = month - 1 or 12
        prev_year = year - 1 if month == 1 else year
        next_month = month % 12 + 1
        next_year = year + 1 if month == 12 else year

        context.update(
            {
                "weeks": weeks,
                "month_name": first_day.strftime("%B"),
                "year": year,
                "month": month,
                "prev_year": prev_year,
                "prev_month": prev_month,
                "next_year": next_year,
                "next_month": next_month,
                "query": query,
                "today": today,
            }
        )
        return context


class CalendarWeekView(LoginRequiredMixin, CalendarBaseMixin, TemplateView):
    template_name = "calendar_app/week.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.localdate()
        year = int(self.kwargs.get("year") or today.year)
        month = int(self.kwargs.get("month") or today.month)
        day = int(self.kwargs.get("day") or today.day)
        anchor = date(year, month, day)

        week_start = anchor - timedelta(days=anchor.weekday())
        week_end = week_start + timedelta(days=6)
        query = self.request.GET.get("q", "").strip()

        items_by_date = self._collect_items(week_start, week_end, query)
        days = []
        for offset in range(7):
            day_date = week_start + timedelta(days=offset)
            days.append(
                {
                    "date": day_date,
                    "is_today": day_date == today,
                    "items": sorted(
                        items_by_date.get(day_date, []),
                        key=lambda item: (item["time"] is None, str(item["time"])),
                    ),
                }
            )

        prev_week = week_start - timedelta(days=7)
        next_week = week_start + timedelta(days=7)

        context.update(
            {
                "days": days,
                "week_start": week_start,
                "week_end": week_end,
                "prev_week": prev_week,
                "next_week": next_week,
                "query": query,
                "today": today,
            }
        )
        return context
