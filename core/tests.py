from django.test import TestCase
from django.urls import reverse


class FrontendPagesTests(TestCase):
    def test_home_page_loads(self):
        response = self.client.get(reverse("core:home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/landing.html")

    def test_help_page_loads(self):
        response = self.client.get(reverse("core:help"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/help.html")

    def test_add_food_page_loads(self):
        response = self.client.get(reverse("core:add_food"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/add_food.html")

    def test_activity_page_loads(self):
        response = self.client.get(reverse("core:activity"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/activity.html")

    def test_history_page_loads(self):
        response = self.client.get(reverse("core:history"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/history.html")

    def test_profile_page_loads(self):
        response = self.client.get(reverse("core:profile"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/profile.html")
