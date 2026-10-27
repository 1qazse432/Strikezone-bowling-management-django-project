"""Remove the manually entered average; it is now derived from GameScore rows."""
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("players", "0001_initial"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="bowler",
            name="bowler_average_between_0_and_300",
        ),
        migrations.RemoveField(
            model_name="bowler",
            name="average_score",
        ),
    ]
