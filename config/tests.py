from pathlib import Path

from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from centers.models import BowlingCenter, Lane
from games.models import BowlingGame, GameScore
from players.models import Bowler


class DashboardAndErrorPageTests(TestCase):
    def test_dashboard_renders_with_an_empty_database(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Every frame.")

    def test_custom_not_found_page_is_used(self):
        response = self.client.get("/this-route-does-not-exist/")
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "This page is off the lane.", status_code=404)

    def test_local_bootstrap_assets_and_primary_footer_navigation_are_rendered(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="/static/vendor/bootstrap/css/bootstrap.min.css"')
        self.assertContains(response, 'src="/static/vendor/bootstrap/js/bootstrap.bundle.min.js"')
        self.assertContains(response, 'href="/static/css/site.css"')
        for route_name in (
            "home",
            "centers:center_list",
            "centers:center_create",
            "games:lane_list",
            "games:lane_create",
            "players:bowler_list",
            "players:bowler_create",
            "games:game_list",
            "games:game_create",
            "games:score_list",
            "games:score_create",
        ):
            self.assertContains(response, f'href="{reverse(route_name)}"')

    def test_footer_links_to_detail_edit_and_delete_pages_for_existing_records(self):
        center = BowlingCenter.objects.create(
            name="North Bowl", address="1 Lane Road", city="Sofia"
        )
        lane = Lane.objects.create(center=center, number=1)
        bowler = Bowler.objects.create(
            first_name="Alex", last_name="Lane", joined_on="2026-01-01"
        )
        game = BowlingGame.objects.create(
            title="Tuesday League", lane=lane, scheduled_at=timezone.now()
        )
        score = GameScore.objects.create(game=game, bowler=bowler, score=187)

        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        route_names_and_objects = (
            ("centers:center_detail", center),
            ("centers:center_update", center),
            ("centers:center_delete", center),
            ("games:lane_detail", lane),
            ("games:lane_update", lane),
            ("games:lane_delete", lane),
            ("players:bowler_detail", bowler),
            ("players:bowler_update", bowler),
            ("players:bowler_delete", bowler),
            ("games:game_detail", game),
            ("games:game_update", game),
            ("games:game_delete", game),
            ("games:score_update", score),
            ("games:score_delete", score),
            ("games:score_create_for_game", game),
        )
        for route_name, obj in route_names_and_objects:
            url = reverse(route_name, args=(obj.pk,))
            self.assertContains(response, f'href="{url}"')

    def test_bootstrap_vendor_assets_are_present_on_disk(self):
        static_root = Path(settings.BASE_DIR) / "static"
        self.assertTrue((static_root / "vendor/bootstrap/css/bootstrap.min.css").is_file())
        self.assertTrue((static_root / "vendor/bootstrap/js/bootstrap.bundle.min.js").is_file())

    def test_bootstrap_stylesheet_is_served_locally_with_default_debug_setting(self):
        response = self.client.get("/static/vendor/bootstrap/css/bootstrap.min.css")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Bootstrap", html=False)
        self.assertContains(response, "--bs-blue", html=False)
