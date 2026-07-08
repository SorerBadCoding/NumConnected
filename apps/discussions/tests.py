from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Comment, Post, PostCategory

User = get_user_model()


class PostCRUDTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="author", password="pw123456", email="a@x.edu")
        self.other = User.objects.create_user(username="other", password="pw123456", email="o@x.edu")

    def test_create_post(self):
        self.client.login(username="author", password="pw123456")
        response = self.client.post(reverse("discussions:create"), {
            "title": "Help with recursion",
            "content": "Can someone explain base cases?",
            "category": PostCategory.PROGRAMMING,
        })
        self.assertEqual(response.status_code, 302)
        post = Post.objects.get(title="Help with recursion")
        self.assertEqual(post.author, self.author)

    def test_non_author_cannot_delete(self):
        post = Post.objects.create(author=self.author, title="Mine", content="x", category=PostCategory.GENERAL)
        self.client.login(username="other", password="pw123456")
        self.client.post(reverse("discussions:delete", args=[post.pk]))
        self.assertTrue(Post.objects.filter(pk=post.pk).exists())

    def test_author_can_delete(self):
        post = Post.objects.create(author=self.author, title="Mine", content="x", category=PostCategory.GENERAL)
        self.client.login(username="author", password="pw123456")
        self.client.post(reverse("discussions:delete", args=[post.pk]))
        self.assertFalse(Post.objects.filter(pk=post.pk).exists())

    def test_toggle_like(self):
        post = Post.objects.create(author=self.author, title="Like me", content="x", category=PostCategory.GENERAL)
        self.client.login(username="other", password="pw123456")

        response = self.client.post(
            reverse("discussions:toggle_like", args=[post.pk]),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.json(), {"liked": True, "like_count": 1})

        response = self.client.post(
            reverse("discussions:toggle_like", args=[post.pk]),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.json(), {"liked": False, "like_count": 0})

    def test_add_comment(self):
        post = Post.objects.create(author=self.author, title="Question", content="x", category=PostCategory.QUESTIONS)
        self.client.login(username="other", password="pw123456")
        self.client.post(reverse("discussions:add_comment", args=[post.pk]), {"content": "Great question!"})
        self.assertEqual(Comment.objects.filter(post=post).count(), 1)

    def test_search_and_filter(self):
        Post.objects.create(author=self.author, title="Python tips", content="x", category=PostCategory.PROGRAMMING)
        Post.objects.create(author=self.author, title="Calculus help", content="x", category=PostCategory.MATHEMATICS)
        self.client.login(username="other", password="pw123456")

        response = self.client.get(reverse("discussions:list"), {"q": "python"})
        titles = [p.title for p in response.context["posts"]]
        self.assertEqual(titles, ["Python tips"])

        response = self.client.get(reverse("discussions:list"), {"category": PostCategory.MATHEMATICS})
        titles = [p.title for p in response.context["posts"]]
        self.assertEqual(titles, ["Calculus help"])

    def test_list_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("discussions:list"))
        self.assertEqual(response.status_code, 302)
