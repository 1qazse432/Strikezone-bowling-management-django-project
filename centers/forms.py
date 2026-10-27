"""Validated forms for centers and lane management."""
from django import forms
from .models import BowlingCenter, Lane
from config.forms import BootstrapFormMixin


class BowlingCenterForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = BowlingCenter
        fields = ("name", "address", "city", "phone", "email", "description")
        labels = {"name": "Center name", "address": "Street address", "city": "City", "phone": "Contact phone", "email": "Contact email", "description": "Description"}
        help_texts = {"description": "Optional; maximum 500 characters.", "email": "Optional contact address."}
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "e.g. StrikeZone Central", "autofocus": True}),
            "address": forms.TextInput(attrs={"placeholder": "Street and building number"}),
            "city": forms.TextInput(attrs={"placeholder": "City"}),
            "phone": forms.TextInput(attrs={"placeholder": "+359 ..."}),
            "email": forms.EmailInput(attrs={"placeholder": "contact@example.com"}),
            "description": forms.Textarea(attrs={"rows": 3, "placeholder": "Facilities, opening notes, or accessibility information"}),
        }

    def clean_name(self):
        return self.cleaned_data["name"].strip()

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get("name", "")
        city = cleaned_data.get("city", "")
        if name and city:
            duplicates = BowlingCenter.objects.filter(name__iexact=name, city__iexact=city)
            if self.instance.pk:
                duplicates = duplicates.exclude(pk=self.instance.pk)
            if duplicates.exists():
                self.add_error("name", "A center with this name already exists in the selected city.")
        return cleaned_data


class LaneForm(BootstrapFormMixin, forms.ModelForm):
    operational_note = forms.CharField(
        label="Operational note", required=False, disabled=True,
        initial="Assign each lane to a center. A lane number must be unique within that center.",
        help_text="Read-only guidance.",
    )

    class Meta:
        model = Lane
        fields = ("center", "number", "surface", "is_available")
        labels = {"center": "Bowling center", "number": "Lane number", "surface": "Lane surface", "is_available": "Available for booking"}
        help_texts = {"is_available": "Uncheck if the lane is closed for maintenance."}
        widgets = {
            "number": forms.NumberInput(attrs={"min": "1", "placeholder": "e.g. 4"}),
            "center": forms.Select(),
            "surface": forms.Select(),
        }

    def clean_number(self):
        number = self.cleaned_data["number"]
        if number < 1:
            raise forms.ValidationError("Lane number must be at least 1.")
        center = self.cleaned_data.get("center")
        if center:
            duplicates = Lane.objects.filter(center=center, number=number)
            if self.instance.pk:
                duplicates = duplicates.exclude(pk=self.instance.pk)
            if duplicates.exists():
                raise forms.ValidationError("That lane number is already used at this center.")
        return number
