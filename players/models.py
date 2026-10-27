"""Bowler profile model and derived performance statistics."""
from django.db import models
from django.db.models import Avg
from django.utils import timezone


class Bowler(models.Model):
    class Hand(models.TextChoices):
        RIGHT = "right", "Right-handed"
        LEFT = "left", "Left-handed"
        BOTH = "both", "Ambidextrous"

    first_name = models.CharField(max_length=60)
    last_name = models.CharField(max_length=60)
    email = models.EmailField(blank=True)
    dominant_hand = models.CharField(max_length=8, choices=Hand.choices, default=Hand.RIGHT)
    joined_on = models.DateField(default=timezone.localdate)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("last_name", "first_name")

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def average_score(self):
        """Return the mean of all recorded game scores, or None if unscored.

        This is deliberately computed from GameScore records, so creating,
        editing, or deleting a score updates the average automatically.
        """
        prefetched_scores = getattr(self, "_prefetched_objects_cache", {}).get("scores")
        if prefetched_scores is not None:
            if not prefetched_scores:
                return None
            return round(sum(record.score for record in prefetched_scores) / len(prefetched_scores), 1)

        average = self.scores.aggregate(value=Avg("score"))["value"]
        return round(average, 1) if average is not None else None

    def __str__(self) -> str:
        return self.full_name
