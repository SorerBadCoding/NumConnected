from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("search/", views.GlobalSearchView.as_view(), name="search"),
]
