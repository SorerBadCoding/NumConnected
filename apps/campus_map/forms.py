from django import forms

from .models import LocationCategory


class LocationSearchForm(forms.Form):
    q = forms.CharField(required=False, widget=forms.TextInput(attrs={
        "class": "form-control", "placeholder": "Search buildings, labs, offices...",
    }))
    category = forms.ChoiceField(
        required=False,
        choices=[("", "All categories")] + list(LocationCategory.choices),
        widget=forms.Select(attrs={"class": "form-select"}),
    )
