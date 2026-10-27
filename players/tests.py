from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from centers.models import BowlingCenter, Lane
from games.models import BowlingGame, GameScore
from .forms import BowlerForm
from .models import Bowler


class BowlerTests(TestCase):
    def setUp(self):
        self.bowler = Bowler.objects.create(first_name="Alex", last_name="Lane")
        center = BowlingCenter.objects.create(name="Average Bowl", address="2 Game Road", city="Sofia")
        lane = Lane.objects.create(center=center, number=1)
        self.game_one = BowlingGame.objects.create(
            title="First Game", lane=lane, scheduled_at=timezone.now() + timedelta(days=1)
        )
        self.game_two = BowlingGame.objects.create(
            title="Second Game", lane=lane, scheduled_at=timezone.now() + timedelta(days=2)
        )

    def test_bowler_list_is_public_and_renders_empty_state(self):
        response = self.client.get(reverse("players:bowler_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Bowlers")

    def test_average_is_none_until_a_score_is_recorded(self):
        self.assertIsNone(self.bowler.average_score)

    def test_average_is_calculated_from_all_recorded_scores(self):
        GameScore.objects.create(game=self.game_one, bowler=self.bowler, score=150)
        GameScore.objects.create(game=self.game_two, bowler=self.bowler, score=181)
        self.bowler.refresh_from_db()
        self.assertEqual(self.bowler.average_score, 165.5)

    def test_average_updates_when_a_score_is_edited_or_deleted(self):
        first = GameScore.objects.create(game=self.game_one, bowler=self.bowler, score=100)
        second = GameScore.objects.create(game=self.game_two, bowler=self.bowler, score=200)
        self.assertEqual(self.bowler.average_score, 150.0)

        first.score = 160
        first.save()
        self.assertEqual(self.bowler.average_score, 180.0)

        second.delete()
        self.assertEqual(self.bowler.average_score, 160.0)

    def test_bowler_form_does_not_allow_manual_average_entry(self):
        form = BowlerForm(data={
            "first_name": "Alex",
            "last_name": "Lane",
            "email": "",
            "dominant_hand": "right",
            "joined_on": "2026-01-01",
            "average_score": "299",
        })
        self.assertTrue(form.is_valid(), form.errors)
        self.assertNotIn("average_score", form.fields)

    def test_average_sort_uses_recorded_scores_and_places_unscored_players_last(self):
        lower = Bowler.objects.create(first_name="Bea", last_name="Bowler")
        higher = Bowler.objects.create(first_name="Chris", last_name="Player")
        GameScore.objects.create(game=self.game_one, bowler=lower, score=120)
        GameScore.objects.create(game=self.game_two, bowler=lower, score=160)
        GameScore.objects.create(game=self.game_one, bowler=higher, score=220)

        response = self.client.get(reverse("players:bowler_list"), {"sort": "average"})
        self.assertEqual(response.status_code, 200)
        ordered_bowlers = list(response.context["bowlers"])
        self.assertEqual([bowler.pk for bowler in ordered_bowlers[:3]], [higher.pk, lower.pk, self.bowler.pk])

    def test_bowler_detail_shows_calculated_average(self):
        GameScore.objects.create(game=self.game_one, bowler=self.bowler, score=175)
        response = self.client.get(reverse("players:bowler_detail", kwargs={"pk": self.bowler.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "175.0")

    def test_full_name_property(self):
        self.assertEqual(self.bowler.full_name, "Alex Lane")
