from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.LandingPageView.as_view(), name="landing"),
    path("contact/", views.ContactMessageView.as_view(), name="contact"),
    path("search/", views.GlobalSearchView.as_view(), name="search"),
]
