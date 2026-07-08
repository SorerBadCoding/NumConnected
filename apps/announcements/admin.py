from django.contrib import admin

from .models import Announcement


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "author", "is_pinned", "publish_at", "expires_at")
    list_filter = ("category", "is_pinned")
    search_fields = ("title", "content")
    date_hierarchy = "publish_at"

    def save_model(self, request, obj, form, change):
        if not obj.author_id:
            obj.author = request.user
        super().save_model(request, obj, form, change)
