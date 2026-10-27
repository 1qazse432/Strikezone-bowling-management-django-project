# Generated for the initial schema; no objects are inserted by this migration.
import django.core.validators
from django.db import migrations, models
from django.db.models import Q
import django.utils.timezone

class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="Bowler",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("first_name", models.CharField(max_length=60)),
                ("last_name", models.CharField(max_length=60)),
                ("email", models.EmailField(blank=True, max_length=254)),
                ("dominant_hand", models.CharField(choices=[("right", "Right-handed"), ("left", "Left-handed"), ("both", "Ambidextrous")], default="right", max_length=8)),
                ("average_score", models.PositiveSmallIntegerField(default=100, help_text="Optional performance estimate on the standard 0–300 scale.", validators=[django.core.validators.MinValueValidator(0, message="Average score cannot be negative."), django.core.validators.MaxValueValidator(300, message="Average score cannot exceed 300.")])),
                ("joined_on", models.DateField(default=django.utils.timezone.localdate)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ("last_name", "first_name"), "constraints": [models.CheckConstraint(condition=Q(average_score__gte=0, average_score__lte=300), name="bowler_average_between_0_and_300")]},
        ),
    ]
