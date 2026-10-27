"""Models describing bowling venues and their lanes."""
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q


class BowlingCenter(models.Model):
    name = models.CharField(max_length=120, verbose_name="Center name")
    address = models.CharField(max_length=180)
    city = models.CharField(max_length=80)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    description = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("city", "name")
        verbose_name = "bowling center"
        verbose_name_plural = "bowling centers"

    def __str__(self) -> str:
        return f"{self.name} — {self.city}"


class Lane(models.Model):
    class Surface(models.TextChoices):
        SYNTHETIC = "synthetic", "Synthetic"
        WOOD = "wood", "Wood"

    center = models.ForeignKey(
        BowlingCenter,
        on_delete=models.PROTECT,
        related_name="lanes",
        help_text="Select the bowling center that owns this lane.",
    )
    number = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1, message="Lane number must be at least 1.")],
        help_text="Lane numbers must be positive and unique within a center.",
    )
    surface = models.CharField(max_length=12, choices=Surface.choices, default=Surface.SYNTHETIC)
    is_available = models.BooleanField(default=True, verbose_name="Available for booking")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("center__name", "number")
        constraints = [
            models.UniqueConstraint(fields=("center", "number"), name="unique_lane_number_per_center"),
            models.CheckConstraint(condition=Q(number__gte=1), name="lane_number_positive"),
        ]

    def __str__(self) -> str:
        return f"{self.center.name} · Lane {self.number}"
