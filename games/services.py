"""Application services for score filtering and performance analytics."""
from __future__ import annotations

from django.db.models import Avg, Count, F, Max, Q
from django.db.models.functions import TruncMonth

from centers.models import BowlingCenter
from players.models import Bowler
from .models import BowlingGame, GameScore


class ScoreQueryService:
    """Centralise the supported search and ordering rules for score records."""

    SORT_OPTIONS = {
        "top": ("-score", "bowler__last_name", "bowler__first_name"),
        "recent": ("-created_at", "-pk"),
        "player": ("bowler__last_name", "bowler__first_name", "-score"),
        "game": ("game__scheduled_at", "game__title", "-score"),
    }

    @classmethod
    def filter_queryset(cls, queryset, params):
        query = params.get("q", "").strip()
        if query:
            queryset = queryset.filter(
                Q(bowler__first_name__icontains=query)
                | Q(bowler__last_name__icontains=query)
                | Q(game__title__icontains=query)
                | Q(game__lane__center__name__icontains=query)
            )

        sort = params.get("sort", "top")
        return queryset.order_by(*cls.SORT_OPTIONS.get(sort, cls.SORT_OPTIONS["top"]))


class BowlingAnalyticsService:
    """Build a database-backed performance overview for the Insights page."""

    SCORE_BANDS = (
        ("Elite", 220, 300, "elite"),
        ("Competitive", 180, 219, "competitive"),
        ("Developing", 120, 179, "developing"),
        ("Beginner", 0, 119, "beginner"),
    )

    @classmethod
    def build_context(cls) -> dict:
        scores = GameScore.objects.select_related("game", "bowler")
        summary = scores.aggregate(
            total_scores=Count("pk"),
            average_score=Avg("score"),
            highest_score=Max("score"),
            perfect_games=Count("pk", filter=Q(score=300)),
            active_bowlers=Count("bowler", distinct=True),
        )

        top_bowlers = list(
            Bowler.objects.annotate(
                games_played=Count("scores"),
                average=Avg("scores__score"),
                personal_best=Max("scores__score"),
            )
            .filter(games_played__gt=0)
            .order_by("-average", "-personal_best", "last_name", "first_name")[:8]
        )

        monthly_activity = list(
            scores.annotate(month=TruncMonth("game__scheduled_at"))
            .values("month")
            .annotate(
                games_scored=Count("pk"),
                average_score=Avg("score"),
                highest_score=Max("score"),
            )
            .order_by("-month")[:6]
        )
        monthly_activity.reverse()
        max_month_count = max((item["games_scored"] for item in monthly_activity), default=0)
        for item in monthly_activity:
            item["bar_width"] = round(item["games_scored"] / max_month_count * 100) if max_month_count else 0

        band_counts = []
        total_scores = summary["total_scores"] or 0
        for label, lower, upper, css_class in cls.SCORE_BANDS:
            count = scores.filter(score__gte=lower, score__lte=upper).count()
            band_counts.append(
                {
                    "label": label,
                    "count": count,
                    "percentage": round(count / total_scores * 100) if total_scores else 0,
                    "css_class": css_class,
                }
            )

        center_performance = list(
            BowlingCenter.objects.annotate(
                lane_count=Count("lanes", distinct=True),
                game_count=Count("lanes__games", distinct=True),
                average_score=Avg("lanes__games__scores__score"),
            )
            .order_by(F("average_score").desc(nulls_last=True), "name")[:6]
        )

        perfect_score_records = scores.filter(score=300).order_by("-game__scheduled_at")[:5]

        return {
            **summary,
            "total_games": BowlingGame.objects.count(),
            "completed_games": BowlingGame.objects.filter(status=BowlingGame.Status.COMPLETED).count(),
            "top_bowlers": top_bowlers,
            "monthly_activity": monthly_activity,
            "score_bands": band_counts,
            "center_performance": center_performance,
            "perfect_score_records": perfect_score_records,
        }
