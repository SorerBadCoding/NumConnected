from django import forms

from core.forms import BootstrapFormMixin

from .models import Comment, Post, PostCategory


class PostForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "content", "category", "image"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Give your post a clear title"}),
            "content": forms.Textarea(attrs={"rows": 6, "placeholder": "Share details, code, or a question..."}),
        }


class CommentForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(attrs={"rows": 3, "placeholder": "Write a comment..."}),
        }


class PostSearchForm(forms.Form):
    q = forms.CharField(required=False, widget=forms.TextInput(attrs={
        "class": "form-control", "placeholder": "Search discussions...",
    }))
    category = forms.ChoiceField(
        required=False,
        choices=[("", "All categories")] + list(PostCategory.choices),
        widget=forms.Select(attrs={"class": "form-select"}),
    )
