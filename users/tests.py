from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework.test import APITestCase

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


class AuthJwtApiTests(APITestCase):
    def setUp(self):
        self.username = "lucia"
        self.password = "safe-pass-123"
        self.user = get_user_model().objects.create_user(
            username=self.username,
            email="lucia@example.com",
            password=self.password,
        )
        Profile.objects.create(user=self.user, weight_kg=62, goal=Profile.GoalChoices.MAINTAIN)

    def test_me_profile_requires_authentication(self):
        response = self.client.get("/users/me/profile/")
        self.assertEqual(response.status_code, 401)

    def test_login_and_access_profile(self):
        login_response = self.client.post(
            "/users/auth/login/",
            {"username": self.username, "password": self.password},
            format="json",
        )
        self.assertEqual(login_response.status_code, 200)
        self.assertIn("access", login_response.data)

        access = login_response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        me_response = self.client.get("/users/me/profile/")

        self.assertEqual(me_response.status_code, 200)
        self.assertEqual(me_response.data["user"], self.user.id)

    def test_logout_blacklists_refresh_token(self):
        login_response = self.client.post(
            "/users/auth/login/",
            {"username": self.username, "password": self.password},
            format="json",
        )
        refresh = login_response.data["refresh"]
        access = login_response.data["access"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        logout_response = self.client.post(
            "/users/auth/logout/",
            {"refresh": refresh},
            format="json",
        )
        self.assertEqual(logout_response.status_code, 205)

        refresh_response = self.client.post(
            "/users/auth/refresh/",
            {"refresh": refresh},
            format="json",
        )
        self.assertIn(refresh_response.status_code, [400, 401])

