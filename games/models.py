"""Game scheduling and individual score records."""
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q


class BowlingGame(models.Model):
    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        IN_PROGRESS = "in_progress", "In progress"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    title = models.CharField(max_length=120, help_text="Give the match a short, descriptive name.")
    lane = models.ForeignKey("centers.Lane", on_delete=models.PROTECT, related_name="games")
    scheduled_at = models.DateTimeField()
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.SCHEDULED)
    notes = models.TextField(max_length=500, blank=True)
    players = models.ManyToManyField("players.Bowler", through="GameScore", related_name="games", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-scheduled_at", "title")

    def __str__(self) -> str:
        return self.title

    def clean(self) -> None:
        """Prevent new games or lane changes from using unavailable lanes."""
        super().clean()
        if not self.lane_id:
            return

        from centers.models import Lane

        lane = Lane.objects.filter(pk=self.lane_id).only("is_available").first()
        if lane is None or lane.is_available:
            return

        # Existing games can keep their current lane if it later becomes
        # unavailable, but a new game or reassignment to that lane is forbidden.
        if self._state.adding:
            raise ValidationError({"lane": "This lane is unavailable. Select an available lane."})

        original_lane_id = type(self).objects.filter(pk=self.pk).values_list(
            "lane_id", flat=True
        ).first()
        if original_lane_id != self.lane_id:
            raise ValidationError({"lane": "This lane is unavailable. Select an available lane."})

    @property
    def participant_count(self) -> int:
        return self.scores.values("bowler_id").distinct().count()

    @property
    def highest_score(self):
        return self.scores.order_by("-score").select_related("bowler").first()


class GameScore(models.Model):
    game = models.ForeignKey(BowlingGame, on_delete=models.CASCADE, related_name="scores")
    bowler = models.ForeignKey("players.Bowler", on_delete=models.PROTECT, related_name="scores")
    score = models.PositiveSmallIntegerField(validators=[MinValueValidator(0, message="Score cannot be negative."), MaxValueValidator(300, message="Score cannot exceed 300.")])
    notes = models.CharField(max_length=180, blank=True, help_text="Optional note about the result.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-score", "bowler__last_name", "bowler__first_name")
        constraints = [
            models.UniqueConstraint(fields=("game", "bowler"), name="one_score_per_bowler_per_game"),
            models.CheckConstraint(condition=Q(score__gte=0, score__lte=300), name="game_score_between_0_and_300"),
        ]

    def __str__(self) -> str:
        return f"{self.bowler} — {self.score} ({self.game})"
