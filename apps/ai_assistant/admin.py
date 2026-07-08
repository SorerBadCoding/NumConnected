from django.contrib import admin

from .models import ChatConversation, ChatMessage, FAQEntry


@admin.register(FAQEntry)
class FAQEntryAdmin(admin.ModelAdmin):
    list_display = ("question", "keywords", "is_active")
    list_filter = ("is_active",)
    search_fields = ("question", "keywords", "answer")


class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ("sender", "content", "created_at")
    can_delete = False


@admin.register(ChatConversation)
class ChatConversationAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "created_at", "updated_at")
    search_fields = ("title", "user__username")
    inlines = [ChatMessageInline]
