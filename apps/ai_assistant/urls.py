from django.urls import path

from . import views

app_name = "ai_assistant"

urlpatterns = [
    path("", views.ChatView.as_view(), name="chat"),
    path("send/", views.SendMessageView.as_view(), name="send_message"),
    path("new/", views.NewConversationView.as_view(), name="new_conversation"),
]
