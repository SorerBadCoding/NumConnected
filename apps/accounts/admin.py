from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Profile, User


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    fk_name = "user"
    extra = 0


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    inlines = [ProfileInline]
    list_display = ("username", "email", "first_name", "last_name", "is_staff", "is_active")
    list_filter = ("is_staff", "is_superuser", "is_active")
    search_fields = ("username", "email", "first_name", "last_name")


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "student_id", "major", "academic_year", "created_at")
    list_filter = ("academic_year", "major")
    search_fields = ("user__username", "user__email", "student_id", "major")
