from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from core.permissions import IsDailyRecordOwner, IsOwner
from .models import DailyEvaluation, DailyRecord
from .serializers import DailyEvaluationSerializer, DailyRecordSerializer


class DailyRecordViewSet(ModelViewSet):
    serializer_class = DailyRecordSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        return DailyRecord.objects.filter(user=self.request.user).order_by("-date")


class DailyEvaluationViewSet(ModelViewSet):
    serializer_class = DailyEvaluationSerializer
    permission_classes = [IsAuthenticated, IsDailyRecordOwner]

    def get_queryset(self):
        return (
            DailyEvaluation.objects.select_related("daily_record", "daily_record__user")
            .filter(daily_record__user=self.request.user)
            .order_by("-daily_record__date")
        )
