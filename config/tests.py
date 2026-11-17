from pathlib import Path

from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from config.forms import BootstrapFormMixin

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
            "games:analytics",
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

    def test_forms_render_their_disabled_read_only_guidance_fields(self):
        from centers.forms import LaneForm
        from games.forms import BowlingGameForm

        lane_form = LaneForm()
        game_form = BowlingGameForm()
        self.assertIn("operational_note", lane_form.fields)
        self.assertTrue(lane_form.fields["operational_note"].disabled)
        self.assertIn("scoring_guidance", game_form.fields)
        self.assertTrue(game_form.fields["scoring_guidance"].disabled)

    def test_shared_bootstrap_form_mixin_is_importable_and_styles_widgets(self):
        from django import forms

        class SampleForm(BootstrapFormMixin, forms.Form):
            title = forms.CharField(help_text="Short title")
            status = forms.ChoiceField(choices=(("open", "Open"),))

        form = SampleForm()
        self.assertIn("form-control", form.fields["title"].widget.attrs["class"])
        self.assertIn("form-select", form.fields["status"].widget.attrs["class"])
        self.assertEqual(form.fields["title"].widget.attrs["aria-describedby"], "title-help")

    def test_insights_page_renders_without_seed_data(self):
        response = self.client.get(reverse("games:analytics"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Performance insights")
        self.assertContains(response, "No perfect games have been recorded yet.")

    def test_score_csv_export_includes_saved_records_and_formula_protection(self):
        center = BowlingCenter.objects.create(
            name="North Bowl", address="1 Lane Road", city="Sofia"
        )
        lane = Lane.objects.create(center=center, number=1)
        bowler = Bowler.objects.create(first_name="Alex", last_name="Lane")
        game = BowlingGame.objects.create(
            title="=HYPERLINK(\"https://example.invalid\")",
            lane=lane,
            scheduled_at=timezone.now(),
        )
        GameScore.objects.create(game=game, bowler=bowler, score=245)

        response = self.client.get(reverse("games:score_export"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv; charset=utf-8")
        self.assertIn("attachment; filename=\"strikezone-scoreboard.csv\"", response["Content-Disposition"])
        self.assertIn("'=HYPERLINK", response.content.decode("utf-8-sig"))
        self.assertIn("245", response.content.decode("utf-8-sig"))

    def test_all_model_workflows_are_reachable_from_valid_routes(self):
        center = BowlingCenter.objects.create(
            name="Coverage Bowl", address="8 Frame Street", city="Sofia"
        )
        lane = Lane.objects.create(center=center, number=4)
        bowler = Bowler.objects.create(first_name="Raya", last_name="Strike")
        game = BowlingGame.objects.create(
            title="Coverage Match",
            lane=lane,
            scheduled_at=timezone.now(),
            status=BowlingGame.Status.COMPLETED,
        )
        score = GameScore.objects.create(game=game, bowler=bowler, score=214)

        routes = (
            "centers:center_list",
            "centers:center_create",
            ("centers:center_detail", center),
            ("centers:center_update", center),
            ("centers:center_delete", center),
            "games:lane_list",
            "games:lane_create",
            ("games:lane_detail", lane),
            ("games:lane_update", lane),
            ("games:lane_delete", lane),
            "players:bowler_list",
            "players:bowler_create",
            ("players:bowler_detail", bowler),
            ("players:bowler_update", bowler),
            ("players:bowler_delete", bowler),
            "games:game_list",
            "games:game_create",
            ("games:game_detail", game),
            ("games:game_update", game),
            ("games:game_delete", game),
            "games:score_list",
            "games:score_create",
            ("games:score_create_for_game", game),
            ("games:score_update", score),
            ("games:score_delete", score),
            "games:analytics",
        )
        for route in routes:
            if isinstance(route, tuple):
                route_name, obj = route
                url = reverse(route_name, args=(obj.pk,))
            else:
                url = reverse(route)
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_insights_aggregates_player_center_and_perfect_game_data(self):
        center = BowlingCenter.objects.create(
            name="Perfect Frame", address="10 Pin Avenue", city="Plovdiv"
        )
        lane = Lane.objects.create(center=center, number=1)
        bowler = Bowler.objects.create(first_name="Dani", last_name="Tenpin")
        game = BowlingGame.objects.create(
            title="Perfect Match",
            lane=lane,
            scheduled_at=timezone.now(),
            status=BowlingGame.Status.COMPLETED,
        )
        GameScore.objects.create(game=game, bowler=bowler, score=300)

        response = self.client.get(reverse("games:analytics"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["perfect_games"], 1)
        self.assertEqual(response.context["active_bowlers"], 1)
        self.assertEqual(response.context["top_bowlers"][0].personal_best, 300)
        self.assertEqual(response.context["center_performance"][0].name, "Perfect Frame")
        self.assertContains(response, "Perfect Match")

    def test_evaluator_can_create_every_model_through_the_ui(self):
        center_response = self.client.post(reverse("centers:center_create"), data={
            "name": "UI Test Bowl",
            "address": "20 Strike Road",
            "city": "Sofia",
            "phone": "",
            "email": "",
            "description": "Created through the application interface.",
        })
        self.assertEqual(center_response.status_code, 302)
        center = BowlingCenter.objects.get(name="UI Test Bowl")

        lane_response = self.client.post(reverse("games:lane_create"), data={
            "center": center.pk,
            "number": 3,
            "surface": Lane.Surface.SYNTHETIC,
            "is_available": "on",
        })
        self.assertEqual(lane_response.status_code, 302)
        lane = Lane.objects.get(center=center, number=3)

        bowler_response = self.client.post(reverse("players:bowler_create"), data={
            "first_name": "Mira",
            "last_name": "Frame",
            "email": "",
            "dominant_hand": Bowler.Hand.RIGHT,
            "joined_on": timezone.localdate().isoformat(),
        })
        self.assertEqual(bowler_response.status_code, 302)
        bowler = Bowler.objects.get(first_name="Mira", last_name="Frame")

        game_response = self.client.post(reverse("games:game_create"), data={
            "title": "UI Created Match",
            "lane": lane.pk,
            "scheduled_at": timezone.localtime(timezone.now()).strftime("%Y-%m-%dT%H:%M"),
            "status": BowlingGame.Status.SCHEDULED,
            "notes": "",
        })
        self.assertEqual(game_response.status_code, 302)
        game = BowlingGame.objects.get(title="UI Created Match")

        score_response = self.client.post(
            reverse("games:score_create_for_game", kwargs={"game_pk": game.pk}),
            data={"bowler": bowler.pk, "score": 198, "notes": "UI score entry"},
        )
        self.assertEqual(score_response.status_code, 302)
        self.assertTrue(GameScore.objects.filter(game=game, bowler=bowler, score=198).exists())
