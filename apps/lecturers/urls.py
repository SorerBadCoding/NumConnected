from django.urls import path

from . import views

app_name = "lecturers"

urlpatterns = [
    path("", views.LecturerListView.as_view(), name="list"),
    path("<int:pk>/", views.LecturerDetailView.as_view(), name="detail"),
]
