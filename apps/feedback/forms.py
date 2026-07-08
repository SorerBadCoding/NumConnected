from django import forms

from core.forms import BootstrapFormMixin

from .models import Feedback, FeedbackStatus, FeedbackType


class FeedbackForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ["feedback_type", "subject", "message", "rating"]
        widgets = {
            "subject": forms.TextInput(attrs={"placeholder": "Short summary"}),
            "message": forms.Textarea(attrs={"rows": 5, "placeholder": "Describe your suggestion, bug, or feedback in detail..."}),
            "rating": forms.Select(choices=[(i, f"{i} star{'s' if i != 1 else ''}") for i in range(1, 6)]),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["rating"].required = False

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("feedback_type") == FeedbackType.RATING and not cleaned_data.get("rating"):
            self.add_error("rating", "Please select a rating from 1 to 5 stars.")
        return cleaned_data


class AdminReplyForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ["status", "admin_reply"]
        widgets = {
            "admin_reply": forms.Textarea(attrs={"rows": 4, "placeholder": "Write a reply to the student..."}),
        }
