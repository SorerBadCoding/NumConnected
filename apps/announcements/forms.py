from django import forms

from core.forms import BootstrapFormMixin

from .models import Announcement, AnnouncementCategory


class AnnouncementForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ["title", "content", "category", "is_pinned", "publish_at", "expires_at"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Announcement title"}),
            "content": forms.Textarea(attrs={"rows": 6, "placeholder": "Write the announcement details..."}),
            "publish_at": forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
            "expires_at": forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["publish_at"].input_formats = ["%Y-%m-%dT%H:%M"]
        self.fields["expires_at"].input_formats = ["%Y-%m-%dT%H:%M"]
        self.fields["expires_at"].required = False

    def clean(self):
        cleaned_data = super().clean()
        publish_at = cleaned_data.get("publish_at")
        expires_at = cleaned_data.get("expires_at")
        if publish_at and expires_at and expires_at <= publish_at:
            self.add_error("expires_at", "Expiry must be after the publish date.")
        return cleaned_data


class AnnouncementSearchForm(forms.Form):
    q = forms.CharField(required=False, widget=forms.TextInput(attrs={
        "class": "form-control", "placeholder": "Search announcements...",
    }))
    category = forms.ChoiceField(
        required=False,
        choices=[("", "All categories")] + list(AnnouncementCategory.choices),
        widget=forms.Select(attrs={"class": "form-select"}),
    )
