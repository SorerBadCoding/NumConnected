from django.contrib import admin

from .models import Lecturer


@admin.register(Lecturer)
class LecturerAdmin(admin.ModelAdmin):
    list_display = ("name", "department", "email", "office_location")
    list_filter = ("department",)
    search_fields = ("name", "subjects", "email")
