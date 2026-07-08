from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView

from core.mixins import OwnerRequiredMixin
from core.models import ActivityLog, ActivityVerb

from .forms import CommentForm, PostForm, PostSearchForm
from .models import Post


class PostListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = "discussions/list.html"
    context_object_name = "posts"
    paginate_by = 8

    def get_queryset(self):
        queryset = Post.objects.select_related("author").prefetch_related("likes")
        form = PostSearchForm(self.request.GET)
        if form.is_valid():
            query = form.cleaned_data.get("q")
            category = form.cleaned_data.get("category")
            if query:
                queryset = queryset.filter(Q(title__icontains=query) | Q(content__icontains=query))
            if category:
                queryset = queryset.filter(category=category)
        return queryset

    def get_template_names(self):
        if self.request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return ["discussions/_post_cards.html"]
        return [self.template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_form"] = PostSearchForm(self.request.GET)
        querydict = self.request.GET.copy()
        querydict.pop("page", None)
        context["querystring"] = querydict.urlencode()
        return context


class PostDetailView(LoginRequiredMixin, DetailView):
    model = Post
    template_name = "discussions/detail.html"
    context_object_name = "post"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comment_form"] = CommentForm()
        context["comments"] = self.object.comments.select_related("author")
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "discussions/form.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, "Your post has been published.")
        ActivityLog.log(
            self.request.user,
            ActivityVerb.POST_CREATED,
            f'Posted "{self.object.title}" in the discussion board',
            icon="bi-chat-square-text",
            url=self.object.get_absolute_url(),
        )
        return response


class PostDeleteView(LoginRequiredMixin, OwnerRequiredMixin, DeleteView):
    model = Post
    template_name = "discussions/confirm_delete.html"
    success_url = reverse_lazy("discussions:list")
    owner_field = "author"

    def form_valid(self, form):
        messages.success(self.request, "Post deleted.")
        return super().form_valid(form)


class CommentCreateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, "Comment added.")
        else:
            messages.error(request, "Comment cannot be empty.")
        return redirect("discussions:detail", pk=pk)


class ToggleLikeView(LoginRequiredMixin, View):
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        if request.user in post.likes.all():
            post.likes.remove(request.user)
            liked = False
        else:
            post.likes.add(request.user)
            liked = True

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"liked": liked, "like_count": post.like_count})
        return redirect("discussions:detail", pk=pk)
