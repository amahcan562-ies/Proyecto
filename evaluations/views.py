from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from core.permissions import IsDailyRecordOwner, IsOwner
from .models import DailyEvaluation, DailyRecord
from .serializers import DailyEvaluationSerializer, DailyRecordSerializer
from .services import ensure_daily_evaluation


class DailyRecordViewSet(ModelViewSet):
    serializer_class = DailyRecordSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        return DailyRecord.objects.filter(user=self.request.user).order_by("-date")

    def perform_create(self, serializer):
        instance = serializer.save()
        ensure_daily_evaluation(instance)

    def perform_update(self, serializer):
        instance = serializer.save()
        ensure_daily_evaluation(instance)


class DailyEvaluationViewSet(ModelViewSet):
    serializer_class = DailyEvaluationSerializer
    permission_classes = [IsAuthenticated, IsDailyRecordOwner]

    def get_queryset(self):
        return (
            DailyEvaluation.objects.select_related("daily_record", "daily_record__user")
            .filter(daily_record__user=self.request.user)
            .order_by("-daily_record__date")
        )

    def perform_create(self, serializer):
        instance = serializer.save()
        ensure_daily_evaluation(instance.daily_record)

    def perform_update(self, serializer):
        instance = serializer.save()
        ensure_daily_evaluation(instance.daily_record)
