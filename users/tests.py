from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIRequestFactory

from users.models import Profile
from users.serializers import ProfileSerializer


class ProfileSerializerTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="ana",
            email="ana@example.com",
            password="safe-pass-123",
        )
        self.profile = Profile.objects.create(user=self.user, weight_kg=70, goal=Profile.GoalChoices.MAINTAIN)
        self.request = APIRequestFactory().get("/")
        self.request.user = self.user

    def test_birth_date_future_is_invalid(self):
        serializer = ProfileSerializer(
            instance=self.profile,
            data={"birth_date": "2999-01-01"},
            partial=True,
            context={"request": self.request},
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("birth_date", serializer.errors)

    def test_goal_lose_requires_lower_target_weight(self):
        serializer = ProfileSerializer(
            instance=self.profile,
            data={"goal": Profile.GoalChoices.LOSE, "target_weight_kg": "75.00"},
            partial=True,
            context={"request": self.request},
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("target_weight_kg", serializer.errors)
