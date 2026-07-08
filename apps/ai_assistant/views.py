from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView

from core.models import ActivityLog, ActivityVerb

from .forms import ChatMessageForm
from .models import ChatConversation, FAQEntry, MessageSender, ChatMessage
from .providers import get_provider

QUICK_ACTIONS = [
    {
        "key": "study_tips",
        "label": "Study Tips",
        "icon": "bi-lightbulb",
        "prompt": "Can you give me some effective study tips for my upcoming exams?",
    },
    {
        "key": "programming_helper",
        "label": "Programming Helper",
        "icon": "bi-code-slash",
        "prompt": "I need help with a programming problem: ",
    },
    {
        "key": "summarize_notes",
        "label": "Summarize Notes",
        "icon": "bi-file-text",
        "prompt": "Please summarize these notes for me:\n\n",
    },
    {
        "key": "generate_quiz",
        "label": "Generate Quiz",
        "icon": "bi-patch-question",
        "prompt": "Generate a short practice quiz on this topic: ",
    },
    {
        "key": "explain_code",
        "label": "Explain Code",
        "icon": "bi-braces",
        "prompt": "Can you explain what this code does?\n\n",
    },
]


class ChatView(LoginRequiredMixin, TemplateView):
    template_name = "ai_assistant/chat.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        pk = self.kwargs.get("pk")

        if pk:
            conversation = get_object_or_404(ChatConversation, pk=pk, user=user)
        else:
            conversation = ChatConversation.objects.filter(user=user).order_by("-updated_at").first()
            if conversation is None:
                conversation = ChatConversation.objects.create(user=user)

        context["conversation"] = conversation
        context["chat_messages"] = conversation.messages.all()
        context["suggested_questions"] = FAQEntry.objects.filter(is_active=True)[:4]
        context["quick_actions"] = QUICK_ACTIONS
        context["recent_conversations"] = (
            ChatConversation.objects.filter(user=user).exclude(pk=conversation.pk).order_by("-updated_at")[:8]
        )
        return context


class SendMessageView(LoginRequiredMixin, View):
    def post(self, request):
        form = ChatMessageForm(request.POST)
        if not form.is_valid():
            return JsonResponse({"error": "Please enter a message before sending."}, status=400)

        message_text = form.cleaned_data["message"]
        conversation_id = form.cleaned_data.get("conversation_id")

        if conversation_id:
            conversation = get_object_or_404(ChatConversation, pk=conversation_id, user=request.user)
        else:
            conversation = ChatConversation.objects.filter(user=request.user).order_by("-updated_at").first()
            if conversation is None:
                conversation = ChatConversation.objects.create(user=request.user)

        is_first_message = not conversation.messages.exists()
        if not conversation.title:
            conversation.title = message_text[:60]

        user_message = ChatMessage.objects.create(
            conversation=conversation, sender=MessageSender.USER, content=message_text
        )

        if is_first_message:
            ActivityLog.log(
                request.user,
                ActivityVerb.CHAT_MESSAGE,
                "Started a conversation with the AI Assistant",
                icon="bi-stars",
                url=reverse("ai_assistant:chat"),
            )

        provider = get_provider()
        try:
            reply_text = provider.respond(
                message_text,
                user=request.user,
                history=list(conversation.messages.order_by("created_at")),
            )
        except Exception:
            reply_text = "Sorry, the assistant is temporarily unavailable. Please try again in a moment."

        assistant_message = ChatMessage.objects.create(
            conversation=conversation, sender=MessageSender.ASSISTANT, content=reply_text
        )
        conversation.save()

        return JsonResponse(
            {
                "conversation_id": conversation.pk,
                "user_message": {
                    "content": user_message.content,
                    "time": user_message.created_at.strftime("%I:%M %p"),
                },
                "assistant_message": {
                    "content": assistant_message.content,
                    "time": assistant_message.created_at.strftime("%I:%M %p"),
                },
            }
        )


class NewConversationView(LoginRequiredMixin, View):
    def post(self, request):
        conversation = ChatConversation.objects.create(user=request.user)
        return redirect("ai_assistant:conversation", pk=conversation.pk)
