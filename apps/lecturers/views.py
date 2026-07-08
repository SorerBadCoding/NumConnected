from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.views.generic import DetailView, ListView

from .forms import LecturerSearchForm
from .models import Lecturer


class LecturerListView(LoginRequiredMixin, ListView):
    model = Lecturer
    template_name = "lecturers/list.html"
    context_object_name = "lecturers"
    paginate_by = 12

    def get_queryset(self):
        queryset = Lecturer.objects.all()
        form = LecturerSearchForm(self.request.GET)
        if form.is_valid():
            query = form.cleaned_data.get("q")
            department = form.cleaned_data.get("department")
            if query:
                queryset = queryset.filter(Q(name__icontains=query) | Q(subjects__icontains=query))
            if department:
                queryset = queryset.filter(department=department)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_form"] = LecturerSearchForm(self.request.GET)
        querydict = self.request.GET.copy()
        querydict.pop("page", None)
        context["querystring"] = querydict.urlencode()
        return context


class LecturerDetailView(LoginRequiredMixin, DetailView):
    model = Lecturer
    template_name = "lecturers/detail.html"
    context_object_name = "lecturer"
