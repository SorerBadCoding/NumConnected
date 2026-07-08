from django import forms

from core.forms import BootstrapFormMixin

from .models import Event, EventCategory


class EventForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Event
        fields = ["title", "description", "category", "location", "start_datetime", "end_datetime", "image"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "e.g. Freshman Welcome Mixer"}),
            "description": forms.Textarea(attrs={"rows": 5, "placeholder": "What should students expect?"}),
            "location": forms.TextInput(attrs={"placeholder": "e.g. Main Auditorium, Building A"}),
            "start_datetime": forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
            "end_datetime": forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["start_datetime"].input_formats = ["%Y-%m-%dT%H:%M"]
        self.fields["end_datetime"].input_formats = ["%Y-%m-%dT%H:%M"]

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start_datetime")
        end = cleaned_data.get("end_datetime")
        if start and end and end <= start:
            self.add_error("end_datetime", "End time must be after the start time.")
        return cleaned_data


class EventSearchForm(forms.Form):
    TIME_CHOICES = [
        ("upcoming", "Upcoming"),
        ("past", "Past"),
        ("all", "All"),
    ]

    q = forms.CharField(required=False, widget=forms.TextInput(attrs={
        "class": "form-control", "placeholder": "Search events by name or location...",
    }))
    category = forms.ChoiceField(
        required=False,
        choices=[("", "All categories")] + list(EventCategory.choices),
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    when = forms.ChoiceField(
        required=False,
        choices=TIME_CHOICES,
        initial="upcoming",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
