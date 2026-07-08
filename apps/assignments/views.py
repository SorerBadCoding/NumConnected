from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from core.mixins import OwnerRequiredMixin

from .forms import AssignmentForm, AssignmentSearchForm
from .models import Assignment, Status


class AssignmentListView(LoginRequiredMixin, ListView):
    model = Assignment
    template_name = "assignments/list.html"
    context_object_name = "assignments"
    paginate_by = 9

    def get_queryset(self):
        queryset = Assignment.objects.filter(owner=self.request.user)
        form = AssignmentSearchForm(self.request.GET)
        if form.is_valid():
            query = form.cleaned_data.get("q")
            status = form.cleaned_data.get("status")
            priority = form.cleaned_data.get("priority")
            if query:
                queryset = queryset.filter(
                    Q(title__icontains=query)
                    | Q(course__icontains=query)
                    | Q(description__icontains=query)
                )
            if status:
                queryset = queryset.filter(status=status)
            if priority:
                queryset = queryset.filter(priority=priority)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_form"] = AssignmentSearchForm(self.request.GET)
        querydict = self.request.GET.copy()
        querydict.pop("page", None)
        context["querystring"] = querydict.urlencode()
        all_assignments = Assignment.objects.filter(owner=self.request.user)
        context["total_count"] = all_assignments.count()
        context["completed_count"] = all_assignments.filter(status=Status.COMPLETED).count()
        context["overdue_count"] = sum(1 for a in all_assignments if a.is_overdue)
        return context


class AssignmentDetailView(LoginRequiredMixin, OwnerRequiredMixin, DetailView):
    model = Assignment
    template_name = "assignments/detail.html"
    context_object_name = "assignment"


class AssignmentCreateView(LoginRequiredMixin, CreateView):
    model = Assignment
    form_class = AssignmentForm
    template_name = "assignments/form.html"

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, "Assignment created successfully.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_create"] = True
        return context


class AssignmentUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    model = Assignment
    form_class = AssignmentForm
    template_name = "assignments/form.html"

    def form_valid(self, form):
        messages.success(self.request, "Assignment updated successfully.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_create"] = False
        return context


class AssignmentDeleteView(LoginRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = Assignment
    template_name = "assignments/confirm_delete.html"
    success_url = reverse_lazy("assignments:list")

    def form_valid(self, form):
        messages.success(self.request, "Assignment deleted.")
        return super().form_valid(form)


class AssignmentToggleCompleteView(LoginRequiredMixin, OwnerRequiredMixin, View):
    """Quick one-click toggle between Completed and Not Started, used by the
    checkbox on the list/detail views without needing the full edit form."""

    def get_object(self):
        return get_object_or_404(Assignment, pk=self.kwargs["pk"])

    def post(self, request, pk):
        assignment = self.get_object()
        if assignment.status == Status.COMPLETED:
            assignment.status = Status.NOT_STARTED
        else:
            assignment.status = Status.COMPLETED
        assignment.save()
        messages.success(request, f'"{assignment.title}" marked as {assignment.get_status_display()}.')
        next_url = request.POST.get("next") or reverse("assignments:list")
        return HttpResponseRedirect(next_url)
