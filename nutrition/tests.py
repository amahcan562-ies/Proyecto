from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIRequestFactory

from evaluations.models import DailyRecord
from nutrition.models import Food
from nutrition.serializers import FoodConsumptionSerializer, FoodSerializer


class FoodSerializerTests(TestCase):
    def test_food_rejects_invalid_macro_sum(self):
        serializer = FoodSerializer(
            data={
                "name": "Alimento test",
                "brand": "",
                "calories_per_100g": "500.00",
                "protein_per_100g": "50.00",
                "carbs_per_100g": "40.00",
                "fat_per_100g": "20.00",
                "fiber_per_100g": "0.00",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)


class FoodConsumptionSerializerTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.owner = user_model.objects.create_user(username="owner_n", password="safe-pass-123")
        self.other_user = user_model.objects.create_user(username="other_n", password="safe-pass-123")

        self.record = DailyRecord.objects.create(user=self.owner)
        self.food = Food.objects.create(
            name="Manzana",
            brand="",
            calories_per_100g=52,
            protein_per_100g=0.3,
            carbs_per_100g=14,
            fat_per_100g=0.2,
            fiber_per_100g=2.4,
            is_active=True,
        )

        self.request = APIRequestFactory().post("/")
        self.request.user = self.other_user

    def test_food_consumption_rejects_foreign_daily_record(self):
        serializer = FoodConsumptionSerializer(
            data={"daily_record": self.record.id, "food": self.food.id, "amount_g": "150.00"},
            context={"request": self.request},
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("daily_record", serializer.errors)
