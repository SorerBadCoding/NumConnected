from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F, Q
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from core.mixins import StaffRequiredMixin
from core.models import ActivityLog, ActivityVerb

from .forms import ResourceForm, ResourceSearchForm
from .models import Resource, ResourceCategory, ResourceDownloadLog, ResourceView, Tag


class ResourceListView(LoginRequiredMixin, ListView):
    model = Resource
    template_name = "resources_app/list.html"
    context_object_name = "resources"
    paginate_by = 12

    def get_queryset(self):
        queryset = Resource.objects.select_related("category", "uploaded_by").prefetch_related("tags", "favorited_by")
        form = ResourceSearchForm(self.request.GET)
        if form.is_valid():
            query = form.cleaned_data.get("q")
            category = form.cleaned_data.get("category")
            tag = form.cleaned_data.get("tag")
            sort = form.cleaned_data.get("sort") or "newest"
            favorites_only = form.cleaned_data.get("favorites_only")

            if query:
                queryset = queryset.filter(Q(title__icontains=query) | Q(description__icontains=query))
            if category:
                queryset = queryset.filter(category=category)
            if tag:
                queryset = queryset.filter(tags=tag)
            if favorites_only:
                queryset = queryset.filter(favorited_by=self.request.user)

            queryset = queryset.order_by(
                {
                    "newest": "-created_at",
                    "oldest": "created_at",
                    "popular": "-download_count",
                    "title": "title",
                }.get(sort, "-created_at")
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_form"] = ResourceSearchForm(self.request.GET)
        context["categories"] = ResourceCategory.objects.all()
        context["tags"] = Tag.objects.all()
        querydict = self.request.GET.copy()
        querydict.pop("page", None)
        context["querystring"] = querydict.urlencode()
        context["recently_viewed"] = (
            ResourceView.objects.filter(user=self.request.user).select_related("resource")[:5]
        )
        return context


class ResourceDetailView(LoginRequiredMixin, DetailView):
    model = Resource
    template_name = "resources_app/detail.html"
    context_object_name = "resource"

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        ResourceView.objects.update_or_create(user=request.user, resource=self.object)
        return response


class ResourceDownloadView(LoginRequiredMixin, View):
    def get(self, request, pk):
        resource = get_object_or_404(Resource, pk=pk)
        Resource.objects.filter(pk=pk).update(download_count=F("download_count") + 1)
        ResourceDownloadLog.objects.create(user=request.user, resource=resource)
        ActivityLog.log(
            request.user,
            ActivityVerb.RESOURCE_DOWNLOADED,
            f'Downloaded "{resource.title}"',
            icon="bi-download",
            url=resource.get_absolute_url(),
        )
        return HttpResponseRedirect(resource.file.url)


class ToggleFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        resource = get_object_or_404(Resource, pk=pk)
        if request.user in resource.favorited_by.all():
            resource.favorited_by.remove(request.user)
            favorited = False
        else:
            resource.favorited_by.add(request.user)
            favorited = True

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"favorited": favorited})
        return HttpResponseRedirect(resource.get_absolute_url())


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
