from django import forms


class BootstrapFormMixin:
    """Apply Bootstrap 5 form-control/form-select/form-check classes.

    Mix into any ModelForm/Form so every field renders styled without each
    app re-declaring widget attrs. Individual widgets can still override
    `attrs` explicitly in the subclass — this only fills in what's missing.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            existing = widget.attrs.get("class", "")

            if isinstance(widget, (forms.CheckboxInput,)):
                base = "form-check-input"
            elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
                base = "form-select"
            elif isinstance(widget, forms.FileInput):
                base = "form-control"
            else:
                base = "form-control"

            classes = f"{existing} {base}".strip()
            widget.attrs["class"] = classes

            if field.help_text and "aria-describedby" not in widget.attrs:
                widget.attrs.setdefault("aria-label", str(field.label or ""))
