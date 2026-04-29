from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from core.permissions import IsDailyRecordOwner, IsStaffOrReadOnly
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
