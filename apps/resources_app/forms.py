from django import forms

from core.forms import BootstrapFormMixin

from .models import Resource, ResourceCategory, Tag


class ResourceForm(BootstrapFormMixin, forms.ModelForm):
    tags_input = forms.CharField(
        required=False,
        label="Tags",
        widget=forms.TextInput(attrs={"placeholder": "e.g. midterm, review, chapter-3 (comma-separated)"}),
        help_text="Comma-separated tags to help classmates find this resource.",
    )

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
        if self.instance.pk:
            self.fields["tags_input"].initial = ", ".join(t.name for t in self.instance.tags.all())

    def clean_tags_input(self):
        raw = self.cleaned_data.get("tags_input", "")
        return [name.strip() for name in raw.split(",") if name.strip()]

    def save(self, commit=True):
        instance = super().save(commit=commit)

        def sync_tags():
            tag_names = self.cleaned_data.get("tags_input", [])
            tags = [Tag.objects.get_or_create(name=name)[0] for name in tag_names]
            instance.tags.set(tags)

        if commit:
            sync_tags()
        else:
            original_save_m2m = self.save_m2m

            def save_m2m():
                original_save_m2m()
                sync_tags()

            self.save_m2m = save_m2m
        return instance


class ResourceSearchForm(forms.Form):
    SORT_CHOICES = [
        ("newest", "Newest first"),
        ("oldest", "Oldest first"),
        ("popular", "Most downloaded"),
        ("title", "Title A–Z"),
    ]

    q = forms.CharField(required=False, widget=forms.TextInput(attrs={
        "class": "form-control", "placeholder": "Search study resources...",
    }))
    category = forms.ModelChoiceField(
        required=False,
        queryset=ResourceCategory.objects.all(),
        empty_label="All categories",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    tag = forms.ModelChoiceField(
        required=False,
        queryset=Tag.objects.all(),
        empty_label="All tags",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    sort = forms.ChoiceField(
        required=False,
        choices=SORT_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    favorites_only = forms.BooleanField(required=False)
