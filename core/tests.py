from django.test import TestCase
from django.urls import reverse


class FrontendPagesTests(TestCase):
    def test_home_page_loads(self):
        response = self.client.get(reverse("core:home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/home.html")

    def test_help_page_loads(self):
        response = self.client.get(reverse("core:help"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/help.html")
