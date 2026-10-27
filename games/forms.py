"""Forms for game scheduling and score recording."""
from django import forms
from django.db.models import Q
from centers.models import Lane
from config.forms import BootstrapFormMixin
from .models import BowlingGame, GameScore

class BowlingGameForm(BootstrapFormMixin, forms.ModelForm):
    scoring_guidance = forms.CharField(
        label="Scoring guidance", required=False, disabled=True,
        initial="A standard ten-pin bowling game has a maximum score of 300.",
        help_text="Read-only information; record each participant's result after creating the game.",
    )
    class Meta:
        model = BowlingGame
        fields = ("title", "lane", "scheduled_at", "status", "notes")
        labels = {"title": "Game title", "lane": "Lane", "scheduled_at": "Scheduled date and time", "status": "Game status", "notes": "Notes"}
        help_texts = {"lane": "Only existing lanes can be assigned to a game.", "notes": "Optional; maximum 500 characters."}
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "e.g. Friday League — Round 3", "autofocus": True}),
            "scheduled_at": forms.DateTimeInput(format="%Y-%m-%dT%H:%M", attrs={"type": "datetime-local"}),
            "notes": forms.Textarea(attrs={"rows": 3, "placeholder": "Optional match details"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["scheduled_at"].input_formats = ["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M:%S"]

        # New games may only select operational lanes. When editing an existing
        # game, retain its current lane even if it has since become unavailable,
        # so that other game details can still be updated without reassigning it.
        available_lanes = Lane.objects.filter(is_available=True)
        if self.instance.pk and self.instance.lane_id:
            self.fields["lane"].queryset = Lane.objects.filter(
                Q(is_available=True) | Q(pk=self.instance.lane_id)
            ).select_related("center")
            current_lane = self.instance.lane
            if not current_lane.is_available:
                self.fields["lane"].help_text = (
                    "This game's current lane is unavailable. You may keep this "
                    "existing assignment while editing, but it cannot be assigned "
                    "to a new game."
                )
        else:
            self.fields["lane"].queryset = available_lanes.select_related("center")
            if not available_lanes.exists():
                self.fields["lane"].help_text = (
                    "No lanes are currently available. Mark a lane as available "
                    "before scheduling a new game."
                )

        self.fields["lane"].error_messages["invalid_choice"] = (
            "Select an available lane. The chosen lane may be unavailable or no longer exist."
        )

    def clean_title(self):
        title = self.cleaned_data["title"].strip()
        if not title:
            raise forms.ValidationError("Enter a title for this game.")
        return title

class GameScoreForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = GameScore
        fields = ("game", "bowler", "score", "notes")
        labels = {"game": "Game", "bowler": "Bowler", "score": "Final score", "notes": "Score note"}
        help_texts = {"score": "Enter a whole number from 0 to 300.", "notes": "Optional; maximum 180 characters."}
        widgets = {
            "score": forms.NumberInput(attrs={"min": 0, "max": 300, "placeholder": "e.g. 187"}),
            "notes": forms.TextInput(attrs={"placeholder": "Optional note"}),
        }

    def __init__(self, *args, game=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fixed_game = game
        if game is not None:
            self.fields["game"].initial = game.pk
            self.fields["game"].disabled = True
            self.fields["game"].label = "Game (fixed)"
            self.fields["game"].help_text = "This score will be recorded for the game shown above."
        self.fields["game"].queryset = BowlingGame.objects.select_related("lane__center").order_by("-scheduled_at")

    def clean_score(self):
        score = self.cleaned_data["score"]
        if not 0 <= score <= 300:
            raise forms.ValidationError("A bowling score must be between 0 and 300.")
        return score

    def clean(self):
        cleaned_data = super().clean()
        game = cleaned_data.get("game")
        bowler = cleaned_data.get("bowler")
        if game and bowler:
            existing = GameScore.objects.filter(game=game, bowler=bowler)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                self.add_error("bowler", "This bowler already has a score recorded for the selected game. Edit the existing score instead.")
        return cleaned_data
