from django.contrib import admin

from .models import Resource, ResourceCategory


@admin.register(ResourceCategory)
class ResourceCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "uploaded_by", "download_count", "created_at")
    list_filter = ("category",)
    search_fields = ("title", "description")
    readonly_fields = ("download_count", "file_size")

    def save_model(self, request, obj, form, change):
        if not obj.uploaded_by_id:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)
