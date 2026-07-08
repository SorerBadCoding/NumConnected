from django import forms

from .models import Department


class LecturerSearchForm(forms.Form):
    q = forms.CharField(required=False, widget=forms.TextInput(attrs={
        "class": "form-control", "placeholder": "Search by name or subject...",
    }))
    department = forms.ChoiceField(
        required=False,
        choices=[("", "All departments")] + list(Department.choices),
        widget=forms.Select(attrs={"class": "form-select"}),
    )
