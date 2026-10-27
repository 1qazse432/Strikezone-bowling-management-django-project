"""Application-level views shared across the project."""
from django.db.models import Count
from django.shortcuts import render


def home(request):
    """Render a live dashboard from the database without requiring seed data."""
    from centers.models import BowlingCenter, Lane
    from games.models import BowlingGame, GameScore
    from players.models import Bowler

    context = {
        "center_count": BowlingCenter.objects.count(),
        "lane_count": Lane.objects.count(),
        "bowler_count": Bowler.objects.count(),
        "game_count": BowlingGame.objects.count(),
        "score_count": GameScore.objects.count(),
        "upcoming_games": BowlingGame.objects.filter(status=BowlingGame.Status.SCHEDULED)
        .annotate(participant_total=Count("scores__bowler", distinct=True))
        .select_related("lane__center")
        .order_by("scheduled_at")[:5],
        "recent_scores": GameScore.objects.select_related("game", "bowler")
        .order_by("-created_at")[:5],
        "popular_centers": BowlingCenter.objects.annotate(lane_count=Count("lanes"))
        .order_by("-lane_count", "name")[:3],
    }
    return render(request, "home.html", context)


def custom_404(request, exception):
    """Serve the project-specific not-found page when DEBUG is disabled."""
    return render(request, "404.html", status=404)
