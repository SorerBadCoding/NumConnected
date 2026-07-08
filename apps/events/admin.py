from django.contrib import admin

from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "location", "start_datetime", "end_datetime", "organizer")
    list_filter = ("category",)
    search_fields = ("title", "description", "location")
    date_hierarchy = "start_datetime"

    def save_model(self, request, obj, form, change):
        if not obj.organizer_id:
            obj.organizer = request.user
        super().save_model(request, obj, form, change)
