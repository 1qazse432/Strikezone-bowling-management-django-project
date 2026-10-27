"""Validated form for editable bowler profile information.

A bowler's average is calculated from recorded GameScore rows and is therefore
not manually editable on the profile form.
"""
from django import forms
from config.forms import BootstrapFormMixin
from .models import Bowler


class BowlerForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Bowler
        fields = ("first_name", "last_name", "email", "dominant_hand", "joined_on")
        labels = {
            "first_name": "First name",
            "last_name": "Last name",
            "email": "Email address",
            "dominant_hand": "Dominant hand",
            "joined_on": "Join date",
        }
        help_texts = {"joined_on": "The date the bowler joined the club."}
        widgets = {
            "first_name": forms.TextInput(attrs={"placeholder": "First name", "autofocus": True}),
            "last_name": forms.TextInput(attrs={"placeholder": "Last name"}),
            "email": forms.EmailInput(attrs={"placeholder": "Optional email address"}),
            "joined_on": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        }

    def clean_first_name(self):
        value = self.cleaned_data["first_name"].strip()
        if not value:
            raise forms.ValidationError("Enter the bowler's first name.")
        return value

    def clean_last_name(self):
        value = self.cleaned_data["last_name"].strip()
        if not value:
            raise forms.ValidationError("Enter the bowler's last name.")
        return value
