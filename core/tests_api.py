from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from users.models import Profile


class ApiEndpointSmokeTests(APITestCase):
    def setUp(self):
        self.username = "apiuser"
        self.password = "safe-pass-123"
        self.user = get_user_model().objects.create_user(
            username=self.username,
            email="apiuser@example.com",
            password=self.password,
        )
        Profile.objects.create(user=self.user, weight_kg=70, goal=Profile.GoalChoices.MAINTAIN)

    def _login(self):
        response = self.client.post(
            "/users/auth/login/",
            {"username": self.username, "password": self.password},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        access = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    def test_requires_auth_for_private_endpoints(self):
        response = self.client.get("/evaluations/daily-records/")
        self.assertEqual(response.status_code, 401)

    def test_list_endpoints_with_auth(self):
        self._login()
        urls = [
            "/evaluations/daily-records/",
            "/evaluations/daily-evaluations/",
            "/nutrition/food-consumptions/",
            "/activity/activity-records/",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

    def test_catalog_is_readable(self):
        response = self.client.get("/nutrition/foods/")
        self.assertEqual(response.status_code, 200)
        response = self.client.get("/activity/activities/")
        self.assertEqual(response.status_code, 200)

