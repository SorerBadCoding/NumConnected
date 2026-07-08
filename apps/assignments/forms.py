from django import forms

from core.forms import BootstrapFormMixin

from .models import Assignment, Priority, Status


class AssignmentForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ["title", "course", "description", "due_date", "priority", "status"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "e.g. Essay on Renewable Energy"}),
            "course": forms.TextInput(attrs={"placeholder": "e.g. CS101"}),
            "description": forms.Textarea(attrs={"rows": 4, "placeholder": "Add any notes or requirements..."}),
            "due_date": forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["due_date"].input_formats = ["%Y-%m-%dT%H:%M"]


class AssignmentSearchForm(forms.Form):
    q = forms.CharField(required=False, widget=forms.TextInput(attrs={
        "class": "form-control", "placeholder": "Search assignments by title, course, or notes...",
    }))
    status = forms.ChoiceField(
        required=False,
        choices=[("", "All statuses")] + list(Status.choices),
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    priority = forms.ChoiceField(
        required=False,
        choices=[("", "All priorities")] + list(Priority.choices),
        widget=forms.Select(attrs={"class": "form-select"}),
    )
