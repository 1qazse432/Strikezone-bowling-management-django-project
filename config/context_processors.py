"""Shared navigation data used by the site-wide footer."""
from centers.models import BowlingCenter, Lane
from games.models import BowlingGame, GameScore
from players.models import Bowler


def footer_navigation(request):
    """Expose existing records so the footer can link to every available CRUD page.

    The querysets are deliberately narrowed and use select_related where labels
    reference related objects. They remain lazy until the footer is rendered.
    """
    return {
        "footer_centers": BowlingCenter.objects.only("id", "name", "city").order_by("name", "city"),
        "footer_lanes": Lane.objects.select_related("center").only(
            "id", "center", "number", "center__name", "center__city"
        ).order_by("center__name", "number"),
        "footer_bowlers": Bowler.objects.only(
            "id", "first_name", "last_name"
        ).order_by("last_name", "first_name"),
        "footer_games": BowlingGame.objects.select_related("lane__center").only(
            "id", "lane", "title", "lane__number", "lane__center", "lane__center__name"
        ).order_by("title", "id"),
        "footer_scores": GameScore.objects.select_related("game", "bowler").only(
            "id", "game", "bowler", "score", "game__title", "bowler__first_name", "bowler__last_name"
        ).order_by("game__title", "bowler__last_name", "bowler__first_name"),
    }
