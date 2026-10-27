# Generated for the initial schema; no objects are inserted by this migration.
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
from django.db.models import Q

class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="BowlingCenter",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120, verbose_name="Center name")),
                ("address", models.CharField(max_length=180)),
                ("city", models.CharField(max_length=80)),
                ("phone", models.CharField(blank=True, max_length=30)),
                ("email", models.EmailField(blank=True, max_length=254)),
                ("description", models.TextField(blank=True, max_length=500)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ("city", "name"), "verbose_name": "bowling center", "verbose_name_plural": "bowling centers"},
        ),
        migrations.CreateModel(
            name="Lane",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("number", models.PositiveSmallIntegerField(help_text="Lane numbers must be positive and unique within a center.", validators=[django.core.validators.MinValueValidator(1, message="Lane number must be at least 1.")])),
                ("surface", models.CharField(choices=[("synthetic", "Synthetic"), ("wood", "Wood")], default="synthetic", max_length=12)),
                ("is_available", models.BooleanField(default=True, verbose_name="Available for booking")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("center", models.ForeignKey(help_text="Select the bowling center that owns this lane.", on_delete=django.db.models.deletion.PROTECT, related_name="lanes", to="centers.bowlingcenter")),
            ],
            options={"ordering": ("center__name", "number"), "constraints": [models.UniqueConstraint(fields=("center", "number"), name="unique_lane_number_per_center"), models.CheckConstraint(condition=Q(number__gte=1), name="lane_number_positive")]},
        ),
    ]
