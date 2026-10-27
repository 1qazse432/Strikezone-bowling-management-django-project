from datetime import timedelta
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from centers.models import BowlingCenter, Lane
from players.models import Bowler
from .forms import BowlingGameForm, GameScoreForm
from .models import BowlingGame, GameScore

class GameScoreTests(TestCase):
    def setUp(self):
        center = BowlingCenter.objects.create(name="Test Bowl", address="1 Lane Road", city="Sofia")
        lane = Lane.objects.create(center=center, number=1)
        self.bowler = Bowler.objects.create(first_name="Mila", last_name="Petrova")
        self.game = BowlingGame.objects.create(title="Weekly Match", lane=lane, scheduled_at=timezone.now() + timedelta(days=1))

    def test_game_detail_links_to_score_creation(self):
        response = self.client.get(reverse("games:game_detail", kwargs={"pk": self.game.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Record participant score")

    def test_new_game_form_only_offers_available_lanes(self):
        unavailable_lane = Lane.objects.create(
            center=self.game.lane.center, number=2, is_available=False
        )
        form = BowlingGameForm()
        offered_lane_ids = set(form.fields["lane"].queryset.values_list("pk", flat=True))
        self.assertIn(self.game.lane_id, offered_lane_ids)
        self.assertNotIn(unavailable_lane.pk, offered_lane_ids)

    def test_new_game_form_rejects_posted_unavailable_lane(self):
        unavailable_lane = Lane.objects.create(
            center=self.game.lane.center, number=2, is_available=False
        )
        form = BowlingGameForm(data={
            "title": "Unavailable Lane Match",
            "lane": unavailable_lane.pk,
            "scheduled_at": (timezone.now() + timedelta(days=2)).strftime("%Y-%m-%dT%H:%M"),
            "status": BowlingGame.Status.SCHEDULED,
            "notes": "",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("lane", form.errors)

    def test_create_view_does_not_save_game_on_unavailable_lane(self):
        unavailable_lane = Lane.objects.create(
            center=self.game.lane.center, number=2, is_available=False
        )
        original_count = BowlingGame.objects.count()
        response = self.client.post(reverse("games:game_create"), data={
            "title": "Attempted Unavailable Lane Match",
            "lane": unavailable_lane.pk,
            "scheduled_at": (timezone.now() + timedelta(days=2)).strftime("%Y-%m-%dT%H:%M"),
            "status": BowlingGame.Status.SCHEDULED,
            "notes": "",
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(BowlingGame.objects.count(), original_count)
        self.assertContains(response, "Select an available lane")

    def test_existing_game_can_keep_lane_that_later_becomes_unavailable(self):
        self.game.lane.is_available = False
        self.game.lane.save(update_fields=["is_available"])
        form = BowlingGameForm(data={
            "title": self.game.title,
            "lane": self.game.lane_id,
            "scheduled_at": self.game.scheduled_at.strftime("%Y-%m-%dT%H:%M"),
            "status": self.game.status,
            "notes": self.game.notes,
        }, instance=self.game)
        self.assertTrue(form.is_valid(), form.errors)

    def test_model_validation_rejects_new_game_on_unavailable_lane(self):
        unavailable_lane = Lane.objects.create(
            center=self.game.lane.center, number=2, is_available=False
        )
        game = BowlingGame(
            title="Invalid Lane Match",
            lane=unavailable_lane,
            scheduled_at=timezone.now() + timedelta(days=2),
        )
        with self.assertRaises(ValidationError):
            game.full_clean()

    def test_score_over_300_is_rejected(self):
        form = GameScoreForm(data={"game": self.game.pk, "bowler": self.bowler.pk, "score": 301, "notes": ""})
        self.assertFalse(form.is_valid())
        self.assertIn("score", form.errors)

    def test_duplicate_bowler_score_for_same_game_is_rejected(self):
        GameScore.objects.create(game=self.game, bowler=self.bowler, score=170)
        form = GameScoreForm(data={"game": self.game.pk, "bowler": self.bowler.pk, "score": 171, "notes": ""})
        self.assertFalse(form.is_valid())
        self.assertIn("bowler", form.errors)

    def test_scoreboard_is_reachable_when_empty(self):
        response = self.client.get(reverse("games:score_list"))
        self.assertEqual(response.status_code, 200)
