from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIRequestFactory

from evaluations.models import DailyRecord
from evaluations.serializers import DailyEvaluationSerializer, DailyRecordSerializer


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
