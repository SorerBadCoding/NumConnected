from django.urls import path

from . import views

app_name = "feedback"

urlpatterns = [
    path("", views.FeedbackListView.as_view(), name="list"),
    path("submit/", views.FeedbackCreateView.as_view(), name="create"),
    path("<int:pk>/", views.FeedbackDetailView.as_view(), name="detail"),
    path("<int:pk>/reply/", views.FeedbackReplyView.as_view(), name="reply"),
]
