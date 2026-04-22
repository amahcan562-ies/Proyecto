from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIRequestFactory

from activity.models import PhysicalActivity
from activity.serializers import ActivityRecordSerializer
from evaluations.models import DailyRecord


class ActivityRecordSerializerTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.owner = user_model.objects.create_user(username="owner_a", password="safe-pass-123")
        self.other_user = user_model.objects.create_user(username="other_a", password="safe-pass-123")
        self.record = DailyRecord.objects.create(user=self.owner)
        self.activity = PhysicalActivity.objects.create(
            name="Correr",
            met_value=8.0,
            intensity=PhysicalActivity.IntensityChoices.HIGH,
            is_active=False,
        )

    def test_activity_record_rejects_inactive_activity(self):
        request = APIRequestFactory().post("/")
        request.user = self.owner
        serializer = ActivityRecordSerializer(
            data={
                "daily_record": self.record.id,
                "activity": self.activity.id,
                "duration_min": 30,
            },
            context={"request": request},
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("activity", serializer.errors)

    def test_activity_record_rejects_foreign_daily_record(self):
        self.activity.is_active = True
        self.activity.save(update_fields=["is_active"])

        request = APIRequestFactory().post("/")
        request.user = self.other_user
        serializer = ActivityRecordSerializer(
            data={
                "daily_record": self.record.id,
                "activity": self.activity.id,
                "duration_min": 30,
            },
            context={"request": request},
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("daily_record", serializer.errors)
