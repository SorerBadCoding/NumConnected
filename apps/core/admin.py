from django.contrib import admin

from .models import ActivityLog, ContactMessage


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ("user", "verb", "description", "created_at")
    list_filter = ("verb",)
    search_fields = ("description", "user__username")
    readonly_fields = ("user", "verb", "description", "icon", "url", "created_at", "updated_at")


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("subject", "name", "email", "is_resolved", "created_at")
    list_filter = ("is_resolved",)
    search_fields = ("subject", "name", "email", "message")
