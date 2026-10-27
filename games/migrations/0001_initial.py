# Generated for the initial schema; no objects are inserted by this migration.
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
from django.db.models import Q

class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ("centers", "0001_initial"),
        ("players", "0001_initial"),
    ]
    operations = [
        migrations.CreateModel(
            name="BowlingGame",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(help_text="Give the match a short, descriptive name.", max_length=120)),
                ("scheduled_at", models.DateTimeField()),
                ("status", models.CharField(choices=[("scheduled", "Scheduled"), ("in_progress", "In progress"), ("completed", "Completed"), ("cancelled", "Cancelled")], default="scheduled", max_length=12)),
                ("notes", models.TextField(blank=True, max_length=500)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("lane", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="games", to="centers.lane")),
            ],
            options={"ordering": ("-scheduled_at", "title")},
        ),
        migrations.CreateModel(
            name="GameScore",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("score", models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(0, message="Score cannot be negative."), django.core.validators.MaxValueValidator(300, message="Score cannot exceed 300.")])),
                ("notes", models.CharField(blank=True, help_text="Optional note about the result.", max_length=180)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("bowler", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="scores", to="players.bowler")),
                ("game", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="scores", to="games.bowlinggame")),
            ],
            options={"ordering": ("-score", "bowler__last_name", "bowler__first_name"), "constraints": [models.UniqueConstraint(fields=("game", "bowler"), name="one_score_per_bowler_per_game"), models.CheckConstraint(condition=Q(score__gte=0, score__lte=300), name="game_score_between_0_and_300")]},
        ),
        migrations.AddField(
            model_name="bowlinggame",
            name="players",
            field=models.ManyToManyField(blank=True, related_name="games", through="games.GameScore", to="players.bowler"),
        ),
    ]
