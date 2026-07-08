from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DetailView, ListView

from core.mixins import OwnerRequiredMixin, StaffRequiredMixin

from .forms import AdminReplyForm, FeedbackForm
from .models import Feedback, FeedbackStatus


class FeedbackListView(LoginRequiredMixin, ListView):
    model = Feedback
    template_name = "feedback/list.html"
    context_object_name = "feedback_items"
    paginate_by = 15

    def get_queryset(self):
        if self.request.user.is_staff:
            queryset = Feedback.objects.select_related("user")
            status = self.request.GET.get("status")
            if status:
                queryset = queryset.filter(status=status)
            return queryset
        return Feedback.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status_choices"] = FeedbackStatus.choices
        context["selected_status"] = self.request.GET.get("status", "")
        return context


class FeedbackCreateView(LoginRequiredMixin, CreateView):
    model = Feedback
    form_class = FeedbackForm
    template_name = "feedback/form.html"
    success_url = reverse_lazy("feedback:list")

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "Thanks for your feedback! We'll take a look soon.")
        return super().form_valid(form)


class FeedbackDetailView(LoginRequiredMixin, OwnerRequiredMixin, DetailView):
    model = Feedback
    template_name = "feedback/detail.html"
    context_object_name = "item"
    owner_field = "user"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_staff:
            context["reply_form"] = AdminReplyForm(instance=self.object)
        return context


class FeedbackReplyView(LoginRequiredMixin, StaffRequiredMixin, View):
    """Staff-only: reply to and/or change the status of a feedback item."""

    def post(self, request, pk):
        item = get_object_or_404(Feedback, pk=pk)
        form = AdminReplyForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, "Feedback updated.")
        else:
            messages.error(request, "Please correct the errors below.")
        return redirect("feedback:detail", pk=pk)
