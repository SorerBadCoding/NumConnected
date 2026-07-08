from django.contrib import admin

from .models import Feedback


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("subject", "user", "feedback_type", "status", "created_at")
    list_filter = ("feedback_type", "status")
    search_fields = ("subject", "message", "user__username")
