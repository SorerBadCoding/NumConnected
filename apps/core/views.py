from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.generic import TemplateView

from accounts.models import User
from announcements.models import Announcement
from events.models import Event
from resources_app.models import Resource

from .forms import ContactMessageForm

TESTIMONIALS = [
    {
        "name": "Amina K.",
        "role": "Senior, Computer Science",
        "quote": "NUM Connect replaced four different apps I used to juggle. Everything about my academic life lives in one calm, fast place now.",
    },
    {
        "name": "David T.",
        "role": "Junior, Business Administration",
        "quote": "The AI Assistant answers the questions I used to email my advisor about. The dashboard alone saves me twenty minutes every morning.",
    },
    {
        "name": "Priya R.",
        "role": "Sophomore, Biology",
        "quote": "I never miss a deadline anymore. The reminders and the clean assignment tracker genuinely changed how I plan my week.",
    },
]

FAQ_ITEMS = [
    {
        "question": "Is NUM Connect free for students?",
        "answer": "Yes — NUM Connect is provided to all enrolled students at no cost as part of the university's digital campus initiative.",
    },
    {
        "question": "How do I get an account?",
        "answer": "Register with your university email and student ID. Your account is active immediately — no approval wait.",
    },
    {
        "question": "Can instructors post announcements and resources?",
        "answer": "Yes, staff accounts can publish announcements, campus events, and study resources that appear instantly to all students.",
    },
    {
        "question": "Does the AI Assistant replace my advisor?",
        "answer": "No — it's a fast first stop for common questions. For anything account-specific, it will point you to your advisor.",
    },
    {
        "question": "Is my data private?",
        "answer": "Your profile and academic data are visible only to you and university staff who manage the relevant content.",
    },
]


class LandingPageView(TemplateView):
    template_name = "core/landing.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("dashboard:home")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()

        context["stats"] = {
            "students": User.objects.filter(is_staff=False).count(),
            "resources": Resource.objects.count(),
            "announcements": Announcement.objects.count(),
            "events": Event.objects.count(),
        }
        context["latest_announcements"] = (
            Announcement.objects.filter(publish_at__lte=now).exclude(expires_at__lt=now)[:3]
        )
        context["upcoming_events"] = Event.objects.filter(end_datetime__gte=now).order_by("start_datetime")[:3]
        context["testimonials"] = TESTIMONIALS
        context["faq_items"] = FAQ_ITEMS
        context["contact_form"] = ContactMessageForm()
        return context


class ContactMessageView(TemplateView):
    """Handles the landing page's contact form submission (POST only)."""

    def post(self, request, *args, **kwargs):
        form = ContactMessageForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thanks for reaching out! We'll get back to you soon.")
        else:
            messages.error(request, "Please correct the errors in your message and try again.")
        return redirect(f"{request.META.get('HTTP_REFERER', '/')}#contact")


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
