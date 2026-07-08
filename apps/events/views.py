from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from core.mixins import StaffRequiredMixin
from core.models import ActivityLog, ActivityVerb

from .forms import EventForm, EventSearchForm
from .models import Event


class EventListView(LoginRequiredMixin, ListView):
    model = Event
    template_name = "events/list.html"
    context_object_name = "events"
    paginate_by = 9

    def get_queryset(self):
        queryset = Event.objects.select_related("organizer")
        form = EventSearchForm(self.request.GET or {"when": "upcoming"})
        if form.is_valid():
            query = form.cleaned_data.get("q")
            category = form.cleaned_data.get("category")
            when = form.cleaned_data.get("when") or "upcoming"

            now = timezone.now()
            if when == "upcoming":
                queryset = queryset.filter(end_datetime__gte=now).order_by("start_datetime")
            elif when == "past":
                queryset = queryset.filter(end_datetime__lt=now).order_by("-start_datetime")
            else:
                queryset = queryset.order_by("start_datetime")

            if query:
                queryset = queryset.filter(Q(title__icontains=query) | Q(location__icontains=query) | Q(description__icontains=query))
            if category:
                queryset = queryset.filter(category=category)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        initial = self.request.GET or {"when": "upcoming"}
        context["search_form"] = EventSearchForm(initial)
        querydict = self.request.GET.copy()
        querydict.pop("page", None)
        context["querystring"] = querydict.urlencode()
        return context


class EventDetailView(LoginRequiredMixin, DetailView):
    model = Event
    template_name = "events/detail.html"
    context_object_name = "event"


class ToggleRSVPView(LoginRequiredMixin, View):
    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        if request.user in event.attendees.all():
            event.attendees.remove(request.user)
            joined = False
        else:
            event.attendees.add(request.user)
            joined = True
            ActivityLog.log(
                request.user,
                ActivityVerb.EVENT_JOINED,
                f'RSVP\'d to "{event.title}"',
                icon="bi-calendar-check",
                url=event.get_absolute_url(),
            )

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"joined": joined, "attendee_count": event.attendee_count})
        return HttpResponseRedirect(event.get_absolute_url())


class EventCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = Event
    form_class = EventForm
    template_name = "events/form.html"

    def form_valid(self, form):
        form.instance.organizer = self.request.user
        messages.success(self.request, "Event created successfully.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_create"] = True
        return context


class EventUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = Event
    form_class = EventForm
    template_name = "events/form.html"

    def form_valid(self, form):
        messages.success(self.request, "Event updated successfully.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_create"] = False
        return context


class EventDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = Event
    template_name = "events/confirm_delete.html"
    success_url = reverse_lazy("events:list")

    def form_valid(self, form):
        messages.success(self.request, "Event deleted.")
        return super().form_valid(form)
