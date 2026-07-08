from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import ChatConversation, FAQEntry
from .providers import LocalFAQProvider

User = get_user_model()


class LocalFAQProviderTests(TestCase):
    def setUp(self):
        FAQEntry.objects.create(
            question="How do I reset my password?",
            keywords="password, reset, forgot password",
            answer="Go to My Profile > Change Password.",
        )

    def test_matches_best_keyword(self):
        provider = LocalFAQProvider()
        reply = provider.respond("I forgot password, help!")
        self.assertEqual(reply, "Go to My Profile > Change Password.")

    def test_falls_back_when_no_match(self):
        provider = LocalFAQProvider()
        reply = provider.respond("What is the airspeed velocity of an unladen swallow?")
        self.assertEqual(reply, LocalFAQProvider.FALLBACK_RESPONSE)

    def test_ignores_inactive_entries(self):
        FAQEntry.objects.create(question="Old", keywords="library hours", answer="Old answer", is_active=False)
        provider = LocalFAQProvider()
        reply = provider.respond("what are the library hours")
        self.assertEqual(reply, LocalFAQProvider.FALLBACK_RESPONSE)


class ChatViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="student", password="pw123456", email="s@x.edu")
        self.client.login(username="student", password="pw123456")

    def test_chat_page_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("ai_assistant:chat"))
        self.assertEqual(response.status_code, 302)

    def test_chat_page_creates_conversation(self):
        self.client.get(reverse("ai_assistant:chat"))
        self.assertEqual(ChatConversation.objects.filter(user=self.user).count(), 1)

    def test_send_message_creates_user_and_assistant_messages(self):
        response = self.client.post(reverse("ai_assistant:send_message"), {"message": "Hello there"})
        self.assertEqual(response.status_code, 200)
        conversation = ChatConversation.objects.get(user=self.user)
        self.assertEqual(conversation.messages.count(), 2)

    def test_empty_message_rejected(self):
        response = self.client.post(reverse("ai_assistant:send_message"), {"message": "   "})
        self.assertEqual(response.status_code, 400)

    def test_new_conversation_creates_additional_row(self):
        self.client.get(reverse("ai_assistant:chat"))
        before = ChatConversation.objects.filter(user=self.user).count()
        self.client.post(reverse("ai_assistant:new_conversation"))
        after = ChatConversation.objects.filter(user=self.user).count()
        self.assertEqual(after, before + 1)
