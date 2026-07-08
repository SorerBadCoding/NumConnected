from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F, Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from core.mixins import StaffRequiredMixin

from .forms import ResourceForm, ResourceSearchForm
from .models import Resource, ResourceCategory


class ResourceListView(LoginRequiredMixin, ListView):
    model = Resource
    template_name = "resources_app/list.html"
    context_object_name = "resources"
    paginate_by = 12

    def get_queryset(self):
        queryset = Resource.objects.select_related("category", "uploaded_by")
        form = ResourceSearchForm(self.request.GET)
        if form.is_valid():
            query = form.cleaned_data.get("q")
            category = form.cleaned_data.get("category")
            if query:
                queryset = queryset.filter(Q(title__icontains=query) | Q(description__icontains=query))
            if category:
                queryset = queryset.filter(category=category)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_form"] = ResourceSearchForm(self.request.GET)
        context["categories"] = ResourceCategory.objects.all()
        querydict = self.request.GET.copy()
        querydict.pop("page", None)
        context["querystring"] = querydict.urlencode()
        return context


class ResourceDetailView(LoginRequiredMixin, DetailView):
    model = Resource
    template_name = "resources_app/detail.html"
    context_object_name = "resource"


class ResourceDownloadView(LoginRequiredMixin, View):
    def get(self, request, pk):
        resource = get_object_or_404(Resource, pk=pk)
        Resource.objects.filter(pk=pk).update(download_count=F("download_count") + 1)
        return HttpResponseRedirect(resource.file.url)


class ResourceCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = Resource
    form_class = ResourceForm
    template_name = "resources_app/form.html"

    def form_valid(self, form):
        form.instance.uploaded_by = self.request.user
        messages.success(self.request, "Resource uploaded successfully.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_create"] = True
        return context


class ResourceUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = Resource
    form_class = ResourceForm
    template_name = "resources_app/form.html"

    def form_valid(self, form):
        messages.success(self.request, "Resource updated successfully.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_create"] = False
        return context


class ResourceDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = Resource
    template_name = "resources_app/confirm_delete.html"
    success_url = reverse_lazy("resources:list")

    def form_valid(self, form):
        messages.success(self.request, "Resource deleted.")
        return super().form_valid(form)
