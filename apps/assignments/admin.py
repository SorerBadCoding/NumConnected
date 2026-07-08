from django.contrib import admin

from .models import Assignment


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "course", "due_date", "priority", "status")
    list_filter = ("status", "priority", "course")
    search_fields = ("title", "description", "course", "owner__username")
    date_hierarchy = "due_date"
