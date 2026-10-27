from django.test import TestCase
from django.urls import reverse
from .models import BowlingCenter, Lane
from .forms import BowlingCenterForm, LaneForm

class CenterAndLaneTests(TestCase):
    def setUp(self):
        self.center = BowlingCenter.objects.create(name="North Bowl", address="1 Main St", city="Sofia")

    def test_center_list_is_accessible_without_authentication(self):
        response = self.client.get(reverse("centers:center_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "North Bowl")

    def test_lane_number_is_unique_per_center(self):
        Lane.objects.create(center=self.center, number=1)
        form = LaneForm(data={"center": self.center.pk, "number": 1, "surface": "synthetic", "is_available": True})
        self.assertFalse(form.is_valid())
        self.assertIn("number", form.errors)

    def test_center_duplicate_name_city_is_rejected_by_form(self):
        form = BowlingCenterForm(data={"name": "North Bowl", "address": "2 Other St", "city": "Sofia", "phone": "", "email": "", "description": ""})
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)
