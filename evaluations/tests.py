from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIRequestFactory

from activity.models import ActivityRecord, PhysicalActivity
from evaluations.models import DailyRecord
from evaluations.serializers import DailyEvaluationSerializer, DailyRecordSerializer
from evaluations.services import ensure_daily_evaluation
from nutrition.models import Food, FoodConsumption
from users.models import Profile


class DailyRecordSerializerTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="eva", password="safe-pass-123")
        self.request = APIRequestFactory().get("/")
        self.request.user = self.user

    def test_daily_record_rejects_future_date(self):
        future_date = timezone.localdate() + timedelta(days=1)
        serializer = DailyRecordSerializer(
            data={"date": future_date, "water_intake_ml": 2000},
            context={"request": self.request},
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("date", serializer.errors)


class DailyEvaluationSerializerTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.owner = user_model.objects.create_user(username="owner", password="safe-pass-123")
        self.other_user = user_model.objects.create_user(username="other", password="safe-pass-123")
        self.record = DailyRecord.objects.create(user=self.owner)

        self.request = APIRequestFactory().post("/")
        self.request.user = self.other_user

    def test_daily_evaluation_rejects_foreign_daily_record(self):
        serializer = DailyEvaluationSerializer(
            data={"daily_record": self.record.id, "score": 80},
            context={"request": self.request},
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("daily_record", serializer.errors)


class DailyEvaluationServiceTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username="service", password="safe-pass-123")
        self.profile = Profile.objects.create(user=self.user, weight_kg=70, goal=Profile.GoalChoices.MAINTAIN)
        self.record = DailyRecord.objects.create(user=self.user)

        self.food = Food.objects.create(
            name="Avena",
            brand="",
            calories_per_100g=100,
            protein_per_100g=10,
            carbs_per_100g=10,
            fat_per_100g=5,
        )
        FoodConsumption.objects.create(daily_record=self.record, food=self.food, amount_g=200)

        self.activity = PhysicalActivity.objects.create(name="Caminar", met_value=5, intensity=PhysicalActivity.IntensityChoices.MODERATE)
        ActivityRecord.objects.create(
            daily_record=self.record,
            activity=self.activity,
            duration_min=60,
            calories_burned_estimated=350,
        )

    def test_service_creates_evaluation(self):
        evaluation, totals, goals, recommendations = ensure_daily_evaluation(self.record)

        self.assertIsNotNone(evaluation)
        self.assertGreaterEqual(evaluation.score, 0)
        self.assertLessEqual(evaluation.score, 100)
        self.assertTrue(recommendations)
