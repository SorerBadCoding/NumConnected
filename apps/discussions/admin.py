from django.contrib import admin

from .models import Comment, Post


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ("author", "content", "created_at")


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "category", "like_count", "comment_count", "created_at")
    list_filter = ("category",)
    search_fields = ("title", "content", "author__username")
    inlines = [CommentInline]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("post", "author", "created_at")
    search_fields = ("content", "author__username")
