from django.contrib import admin

from .models import Exam, Holiday


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "date", "start_time", "end_time", "location")
    list_filter = ("course",)
    search_fields = ("title", "course", "location")
    date_hierarchy = "date"


@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ("name", "date", "end_date")
    search_fields = ("name",)
    date_hierarchy = "date"
