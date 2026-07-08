from django import forms

from core.forms import BootstrapFormMixin

from .models import Resource, ResourceCategory


class ResourceForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Resource
        fields = ["title", "description", "category", "file"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "e.g. Calculus II Midterm Review Sheet"}),
            "description": forms.Textarea(attrs={"rows": 4, "placeholder": "Briefly describe what this resource covers..."}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].required = False
        self.fields["category"].empty_label = "Uncategorized"


class ResourceSearchForm(forms.Form):
    q = forms.CharField(required=False, widget=forms.TextInput(attrs={
        "class": "form-control", "placeholder": "Search study resources...",
    }))
    category = forms.ModelChoiceField(
        required=False,
        queryset=ResourceCategory.objects.all(),
        empty_label="All categories",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
