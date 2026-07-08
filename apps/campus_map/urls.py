from django.urls import path

from . import views

app_name = "campus_map"

urlpatterns = [
    path("", views.CampusMapView.as_view(), name="map"),
]
