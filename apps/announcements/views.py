from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from core.mixins import StaffRequiredMixin

from .forms import AnnouncementForm, AnnouncementSearchForm
from .models import Announcement


class AnnouncementListView(LoginRequiredMixin, ListView):
    model = Announcement
    template_name = "announcements/list.html"
    context_object_name = "announcements"
    paginate_by = 9

    def get_queryset(self):
        queryset = Announcement.objects.select_related("author")
        if not self.request.user.is_staff:
            now = timezone.now()
            queryset = queryset.filter(publish_at__lte=now).exclude(expires_at__lt=now)

        form = AnnouncementSearchForm(self.request.GET)
        if form.is_valid():
            query = form.cleaned_data.get("q")
            category = form.cleaned_data.get("category")
            if query:
                queryset = queryset.filter(Q(title__icontains=query) | Q(content__icontains=query))
            if category:
                queryset = queryset.filter(category=category)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_form"] = AnnouncementSearchForm(self.request.GET)
        querydict = self.request.GET.copy()
        querydict.pop("page", None)
        context["querystring"] = querydict.urlencode()
        return context


class AnnouncementDetailView(LoginRequiredMixin, DetailView):
    model = Announcement
    template_name = "announcements/detail.html"
    context_object_name = "announcement"


class AnnouncementCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = Announcement
    form_class = AnnouncementForm
    template_name = "announcements/form.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, "Announcement published successfully.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_create"] = True
        return context


class AnnouncementUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = Announcement
    form_class = AnnouncementForm
    template_name = "announcements/form.html"

    def form_valid(self, form):
        messages.success(self.request, "Announcement updated successfully.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_create"] = False
        return context


class AnnouncementDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = Announcement
    template_name = "announcements/confirm_delete.html"
    success_url = reverse_lazy("announcements:list")

    def form_valid(self, form):
        messages.success(self.request, "Announcement deleted.")
        return super().form_valid(form)
