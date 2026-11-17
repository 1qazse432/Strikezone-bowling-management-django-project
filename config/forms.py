"""Shared Bootstrap presentation mixins for Django forms.

This module is intentionally located in the project package because every
application imports :class:`BootstrapFormMixin` from ``config.forms``.
"""
from __future__ import annotations

from django import forms


class BootstrapFormMixin:
    """Apply accessible Bootstrap classes to visible form widgets.

    The mixin is designed for normal Django ``Form`` and ``ModelForm`` classes.
    It preserves widget attributes declared by each form and adds accessible
    help/error associations without changing validation or persistence logic.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            widget = field.widget
            if widget.is_hidden:
                continue

            css_class = self._bootstrap_class_for(widget)
            existing_classes = widget.attrs.get("class", "").split()
            if css_class not in existing_classes:
                existing_classes.append(css_class)
            widget.attrs["class"] = " ".join(existing_classes)

            described_by = widget.attrs.get("aria-describedby", "").split()
            if field.help_text:
                described_by.append(f"{field_name}-help")
            if described_by:
                widget.attrs["aria-describedby"] = " ".join(dict.fromkeys(described_by))

            if field.required:
                widget.attrs.setdefault("aria-required", "true")


    def full_clean(self):
        """Run Django validation, then mark invalid widgets accessibly.

        Validation is deliberately deferred until Django calls ``full_clean``;
        this allows subclasses to finish configuring querysets and field rules
        after their call to ``super().__init__``.
        """
        super().full_clean()
        for field_name, field in self.fields.items():
            if self._errors and self._errors.get(field_name):
                widget = field.widget
                widget.attrs["aria-invalid"] = "true"
                described_by = widget.attrs.get("aria-describedby", "").split()
                described_by.append(f"{field_name}-errors")
                widget.attrs["aria-describedby"] = " ".join(dict.fromkeys(described_by))
                classes = widget.attrs.get("class", "").split()
                if "is-invalid" not in classes:
                    classes.append("is-invalid")
                widget.attrs["class"] = " ".join(classes)

    @staticmethod
    def _bootstrap_class_for(widget: forms.Widget) -> str:
        """Return the suitable Bootstrap class for a widget type."""
        if isinstance(widget, (forms.CheckboxInput, forms.CheckboxSelectMultiple, forms.RadioSelect)):
            return "form-check-input"
        if isinstance(widget, (forms.Select, forms.SelectMultiple)):
            return "form-select"
        return "form-control"
