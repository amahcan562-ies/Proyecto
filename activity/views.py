from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from core.permissions import IsDailyRecordOwner, IsStaffOrReadOnly
from evaluations.services import ensure_daily_evaluation, estimate_activity_calories, get_user_profile
from .models import ActivityRecord, PhysicalActivity
from .serializers import ActivityRecordSerializer, PhysicalActivitySerializer


class PhysicalActivityViewSet(ModelViewSet):
    serializer_class = PhysicalActivitySerializer
    permission_classes = [IsStaffOrReadOnly]

    def get_queryset(self):
        queryset = PhysicalActivity.objects.all()
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_active=True)
        return queryset.order_by("name")


class ActivityRecordViewSet(ModelViewSet):
    serializer_class = ActivityRecordSerializer
    permission_classes = [IsAuthenticated, IsDailyRecordOwner]

    def get_queryset(self):
        return (
            ActivityRecord.objects.select_related("daily_record", "activity")
            .filter(daily_record__user=self.request.user)
            .order_by("-created_at")
        )

    def perform_create(self, serializer):
        profile = get_user_profile(self.request.user)
        calories = estimate_activity_calories(
            serializer.validated_data.get("activity"),
            serializer.validated_data.get("duration_min"),
            getattr(profile, "weight_kg", None),
        )
        instance = serializer.save(calories_burned_estimated=calories)
        ensure_daily_evaluation(instance.daily_record)

    def perform_update(self, serializer):
        profile = get_user_profile(self.request.user)
        activity = serializer.validated_data.get("activity", serializer.instance.activity)
        duration = serializer.validated_data.get("duration_min", serializer.instance.duration_min)
        calories = estimate_activity_calories(
            activity,
            duration,
            getattr(profile, "weight_kg", None),
        )
        instance = serializer.save(calories_burned_estimated=calories)
        ensure_daily_evaluation(instance.daily_record)

    def perform_destroy(self, instance):
        daily_record = instance.daily_record
        instance.delete()
        ensure_daily_evaluation(daily_record)
