from django.urls import path

from . import views

app_name = "assignments"

urlpatterns = [
    path("", views.AssignmentListView.as_view(), name="list"),
    path("create/", views.AssignmentCreateView.as_view(), name="create"),
    path("<int:pk>/", views.AssignmentDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", views.AssignmentUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", views.AssignmentDeleteView.as_view(), name="delete"),
    path("<int:pk>/toggle/", views.AssignmentToggleCompleteView.as_view(), name="toggle"),
]
