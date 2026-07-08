from django.contrib import admin

from .models import CampusLocation


@admin.register(CampusLocation)
class CampusLocationAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "building_code", "x_position", "y_position")
    list_filter = ("category",)
    search_fields = ("name", "description", "building_code")
