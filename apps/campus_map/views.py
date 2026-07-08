import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.views.generic import ListView

from .forms import LocationSearchForm
from .models import CampusLocation


class CampusMapView(LoginRequiredMixin, ListView):
    model = CampusLocation
    template_name = "campus_map/map.html"
    context_object_name = "locations"
    paginate_by = None

    def get_queryset(self):
        queryset = CampusLocation.objects.all()
        form = LocationSearchForm(self.request.GET)
        if form.is_valid():
            query = form.cleaned_data.get("q")
            category = form.cleaned_data.get("category")
            if query:
                queryset = queryset.filter(Q(name__icontains=query) | Q(description__icontains=query))
            if category:
                queryset = queryset.filter(category=category)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_form"] = LocationSearchForm(self.request.GET)
        all_locations = CampusLocation.objects.all()
        context["all_locations"] = all_locations
        context["locations_json"] = json.dumps(
            {
                location.pk: {
                    "name": location.name,
                    "category": location.get_category_display(),
                    "description": location.description,
                    "icon": location.icon,
                }
                for location in all_locations
            }
        )
        return context
